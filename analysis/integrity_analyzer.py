"""
Data Integrity Analyzer

Evaluates data quality, completeness, and consistency.
"""

from typing import List, Dict
from sqlalchemy.orm import Session
from database.schema import Impact, StakeholderGroup, OrganizationUnit, BusinessProcess, System, Policy
from analysis.analysis_models import IntegrityAnalysisResult, AnalysisFinding


class IntegrityAnalyzer:
    """
    Analyzes data integrity of the registry.
    
    Checks for:
    - Missing required fields
    - Duplicate records
    - Invalid values
    - Data consistency
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze(self) -> IntegrityAnalysisResult:
        """
        Perform comprehensive integrity analysis.
        
        Returns:
            IntegrityAnalysisResult with score and findings
        """
        findings = []
        missing_fields = {}
        duplicate_impacts = []
        duplicate_assets = {}
        invalid_values = []
        
        # Analyze impacts
        impacts = self.session.query(Impact).all()
        total_records = len(impacts)
        records_with_issues = 0
        
        # Check for missing required fields
        missing_description = 0
        missing_title = 0
        missing_impact_number = 0
        
        for impact in impacts:
            has_issue = False
            
            if not impact.description or impact.description.strip() == "":
                missing_description += 1
                has_issue = True
            
            if not impact.title or impact.title.strip() == "":
                missing_title += 1
                has_issue = True
            
            if not impact.impact_number or impact.impact_number.strip() == "":
                missing_impact_number += 1
                has_issue = True
            
            if has_issue:
                records_with_issues += 1
        
        if missing_description > 0:
            missing_fields['description'] = missing_description
            findings.append(AnalysisFinding(
                severity="Critical",
                category="Missing Required Field",
                title=f"{missing_description} impact(s) missing description",
                description="Impact description is required for proper documentation and understanding.",
                recommendation="Add descriptions to all impacts to ensure clarity and completeness."
            ))
        
        if missing_title > 0:
            missing_fields['title'] = missing_title
            findings.append(AnalysisFinding(
                severity="High",
                category="Missing Required Field",
                title=f"{missing_title} impact(s) missing title",
                description="Impact title provides quick identification and context.",
                recommendation="Add concise titles to all impacts."
            ))
        
        if missing_impact_number > 0:
            missing_fields['impact_number'] = missing_impact_number
            findings.append(AnalysisFinding(
                severity="High",
                category="Missing Required Field",
                title=f"{missing_impact_number} impact(s) missing impact number",
                description="Impact numbers provide unique identification for tracking.",
                recommendation="Assign unique impact numbers to all impacts."
            ))
        
        # Check for duplicate impact numbers
        impact_numbers = {}
        for impact in impacts:
            if impact.impact_number:
                num = impact.impact_number.strip().upper()
                if num in impact_numbers:
                    impact_numbers[num].append(impact.id)
                else:
                    impact_numbers[num] = [impact.id]
        
        for num, ids in impact_numbers.items():
            if len(ids) > 1:
                duplicate_impacts.append({
                    'impact_number': num,
                    'ids': ids,
                    'count': len(ids)
                })
                records_with_issues += len(ids)
        
        if duplicate_impacts:
            findings.append(AnalysisFinding(
                severity="Critical",
                category="Duplicate Records",
                title=f"{len(duplicate_impacts)} duplicate impact number(s) found",
                description="Multiple impacts share the same impact number, causing confusion.",
                recommendation="Ensure all impact numbers are unique. Renumber duplicates."
            ))
        
        # Check for duplicate stakeholder groups
        sg_names = {}
        for sg in self.session.query(StakeholderGroup).all():
            name = sg.name.strip().lower()
            if name in sg_names:
                sg_names[name].append({'id': sg.id, 'name': sg.name})
            else:
                sg_names[name] = [{'id': sg.id, 'name': sg.name}]
        
        duplicate_sgs = [{'name': name, 'records': records} for name, records in sg_names.items() if len(records) > 1]
        if duplicate_sgs:
            duplicate_assets['stakeholder_groups'] = duplicate_sgs
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Duplicate Assets",
                title=f"{len(duplicate_sgs)} duplicate stakeholder group(s) found",
                description="Multiple stakeholder groups with the same name exist.",
                recommendation="Consolidate duplicate stakeholder groups or rename for clarity."
            ))
        
        # Check for duplicate organization units
        ou_names = {}
        for ou in self.session.query(OrganizationUnit).all():
            name = ou.name.strip().lower()
            if name in ou_names:
                ou_names[name].append({'id': ou.id, 'name': ou.name})
            else:
                ou_names[name] = [{'id': ou.id, 'name': ou.name}]
        
        duplicate_ous = [{'name': name, 'records': records} for name, records in ou_names.items() if len(records) > 1]
        if duplicate_ous:
            duplicate_assets['organization_units'] = duplicate_ous
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Duplicate Assets",
                title=f"{len(duplicate_ous)} duplicate organization unit(s) found",
                description="Multiple organization units with the same name exist.",
                recommendation="Consolidate duplicate organization units or rename for clarity."
            ))
        
        # Check for invalid severity values
        valid_severities = ['Critical', 'High', 'Medium', 'Low', '']
        invalid_severity_impacts = []
        for impact in impacts:
            if impact.severity and impact.severity not in valid_severities:
                invalid_severity_impacts.append({
                    'id': impact.id,
                    'impact_number': impact.impact_number,
                    'severity': impact.severity
                })
        
        if invalid_severity_impacts:
            invalid_values.extend(invalid_severity_impacts)
            findings.append(AnalysisFinding(
                severity="Low",
                category="Invalid Values",
                title=f"{len(invalid_severity_impacts)} impact(s) with invalid severity",
                description="Severity values should be: Critical, High, Medium, or Low.",
                recommendation="Update severity values to use standard options."
            ))
        
        # Calculate integrity score
        score = self._calculate_score(
            total_records=total_records,
            records_with_issues=records_with_issues,
            findings=findings
        )
        
        return IntegrityAnalysisResult(
            score=score,
            total_records=total_records,
            records_with_issues=records_with_issues,
            findings=findings,
            missing_required_fields=missing_fields,
            duplicate_impacts=duplicate_impacts,
            duplicate_assets=duplicate_assets,
            invalid_values=invalid_values
        )
    
    def _calculate_score(self, total_records: int, records_with_issues: int, findings: List[AnalysisFinding]) -> float:
        """
        Calculate integrity score.
        
        Args:
            total_records: Total number of records analyzed
            records_with_issues: Number of records with issues
            findings: List of findings
            
        Returns:
            Score from 0-100
        """
        if total_records == 0:
            return 100.0
        
        # Base score from clean records
        clean_ratio = (total_records - records_with_issues) / total_records
        base_score = clean_ratio * 100
        
        # Deduct points for critical findings
        critical_penalty = sum(10 for f in findings if f.severity == "Critical")
        high_penalty = sum(5 for f in findings if f.severity == "High")
        medium_penalty = sum(2 for f in findings if f.severity == "Medium")
        
        total_penalty = critical_penalty + high_penalty + medium_penalty
        
        final_score = max(0, base_score - total_penalty)
        
        return round(final_score, 1)
