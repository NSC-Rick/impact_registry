# WPP-014: Configure Persistent Workspace Storage for Render

## Objective

Enable persistent storage for Impact Registry workspaces so `.irp` project files survive application restarts, deployments, and container recreation.

This establishes the workspace file as the permanent source of truth for all projects.

## Status: ✅ COMPLETE

## Implementation Summary

### 1. ✅ Render Persistent Disk Configuration

**File:** `render.yaml`

```yaml
disk:
  name: impact-registry-workspaces
  mountPath: /var/data/workspaces
  sizeGB: 1
```

**What This Provides:**
- Persistent 1GB disk mounted at `/var/data/workspaces`
- Data survives restarts, deployments, and scaling
- Expandable as needed through Render dashboard

### 2. ✅ Environment Configuration

**File:** `config.py`

Created centralized configuration module with:

```python
WORKSPACE_ROOT = os.environ.get("WORKSPACE_ROOT", "workspaces")
```

**Environment-Specific Paths:**
- **Local Development:** `./workspaces`
- **Render Production:** `/var/data/workspaces`

**Key Features:**
- `Config.get_workspace_path()` - Get workspace directory
- `Config.validate_workspace()` - Validate accessibility
- `Config.ensure_workspace_exists()` - Create if needed
- `Config.print_startup_diagnostics()` - Startup logging

### 3. ✅ Service Updates

**Updated Components:**

**WorkspaceService** (`services/workspace_service.py`)
- Uses `Config.WORKSPACE_ROOT` instead of hardcoded `"workspaces"`
- Dynamic property access for environment-aware paths

**ProjectRegistry** (`services/project_registry.py`)
- Uses `Config.get_workspace_path()` for discovery
- Uses `Config.get_registry_path()` for registry file
- Uses `Config.APP_VERSION` for version tracking

**All Path References:**
- ✅ Project creation
- ✅ Project discovery
- ✅ Project opening
- ✅ Registry management
- ✅ Import/Export operations

### 4. ✅ Startup Validation

**File:** `app.py`

**Startup Diagnostics Output:**

```
============================================================
Impact Registry Startup
============================================================

Version: 1.0.0
Environment: Production

Workspace Root:
  /var/data/workspaces

Persistent Storage:
  ✓ Available

Projects Found: 4

============================================================
```

**Validation Checks:**
- ✅ Workspace directory exists
- ✅ Directory is readable
- ✅ Directory is writable
- ✅ Persistent disk mounted

**Error Handling:**

If workspace unavailable:
```
⚠️ Persistent Workspace Storage Unavailable
Cannot create workspace directory: [error details]
Projects cannot be saved until storage is available.
```

Application stops gracefully with clear error message.

### 5. ✅ Project Discovery Enhancement

**File:** `pages/00_Home.py`

**Enhanced Logging:**

```
[HOME] Discovered 2 new project(s)

Loaded Projects (4):
  ✓ Mondelez Pilot
  ✓ ERP Implementation
  ✓ Test Project
  ✓ Fieldglass Demo
```

**Discovery Process:**
1. Scan workspace directory for `.irp` files
2. Read metadata from each database
3. Register with correct UUID
4. Log all discovered projects

### 6. ✅ Deployment Configuration

**File:** `render.yaml`

**Complete Configuration:**

```yaml
services:
  - type: web
    name: impact-registry
    runtime: python
    repo: https://github.com/NSC-Rick/impact_registry
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
    
    # Persistent disk
    disk:
      name: impact-registry-workspaces
      mountPath: /var/data/workspaces
      sizeGB: 1
    
    # Environment variables
    envVars:
      - key: WORKSPACE_ROOT
        value: /var/data/workspaces
      - key: STREAMLIT_SERVER_HEADLESS
        value: true
      - key: STREAMLIT_SERVER_ENABLE_CORS
        value: false
      - key: STREAMLIT_BROWSER_GATHER_USAGE_STATS
        value: false
```

**Key Points:**
- Disk mount path matches `WORKSPACE_ROOT` environment variable
- Automatic configuration via Blueprint deployment
- No manual setup required

## Acceptance Criteria

### ✅ Create Project

**Test:** Create `TestProject.irp`

**Result:**
- File written to `/var/data/workspaces/TestProject.irp`
- Stored on persistent disk
- Survives container lifecycle

### ✅ Restart Application

**Test:** Restart Render service

**Result:**
- Project remains on disk
- Discovery finds existing project
- No data loss

### ✅ Discovery

**Test:** Application startup

**Result:**
- Existing projects automatically discovered
- Metadata read from databases
- Projects available for selection
- Startup diagnostics show all projects

### ✅ Deployment

**Test:** Deploy new application version

**Result:**
- Code updated from GitHub
- Persistent disk unchanged
- All projects preserved
- Discovery repopulates registry

### ✅ Recovery

**Test:** Container recreation

**Result:**
- No data loss
- All workspaces remain available
- Discovery automatically repopulates Home page
- Application fully functional

## Architecture

### Workspace-Centric Design

**One Project = One File:**
```
/var/data/workspaces/
├── Client_ABC.irp          # Self-contained project
├── ERP_Implementation.irp  # Self-contained project
├── Test_Project.irp        # Self-contained project
└── project_registry.json   # Discovery cache
```

**Each `.irp` file contains:**
- SQLite database with complete schema
- Project metadata (UUID, name, client, etc.)
- All impacts and relationships
- Enterprise assets
- Complete project state

**Benefits:**
- ✅ Portable - copy file to backup/archive
- ✅ Durable - survives application lifecycle
- ✅ Self-contained - no external dependencies
- ✅ Discoverable - filesystem is source of truth
- ✅ Shareable - easy client handoffs

### Data Flow

**Project Creation:**
```
User creates project
  ↓
WorkspaceService.create_new_project()
  ↓
Write to Config.WORKSPACE_ROOT/ProjectName.irp
  ↓
Persistent disk storage
  ↓
ProjectRegistry.add_project()
```

**Application Startup:**
```
app.py starts
  ↓
Config.print_startup_diagnostics()
  ↓
Config.validate_workspace()
  ↓
Home page loads
  ↓
workspace.discover_projects()
  ↓
Scan Config.WORKSPACE_ROOT/*.irp
  ↓
Read metadata from each database
  ↓
Populate registry
  ↓
Display projects
```

**After Deployment:**
```
Render deploys new code
  ↓
Container restarts
  ↓
Persistent disk remains intact
  ↓
Application discovers existing projects
  ↓
All data available immediately
```

## Configuration Reference

### Environment Variables

| Variable | Local Dev | Render Production |
|----------|-----------|-------------------|
| `WORKSPACE_ROOT` | `workspaces` | `/var/data/workspaces` |

### Disk Configuration

| Setting | Value |
|---------|-------|
| Disk Name | `impact-registry-workspaces` |
| Mount Path | `/var/data/workspaces` |
| Initial Size | 1GB |
| Expandable | Yes |
| Cost | ~$0.25/month per GB |

### Capacity Planning

| Projects | Size | Disk Required |
|----------|------|---------------|
| 100-200 typical | ~500KB each | 1GB |
| 500 typical | ~500KB each | 5GB |
| 1000 typical | ~500KB each | 10GB |

## Deployment Instructions

### First-Time Deployment

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Render Dashboard**
   - Click "New +" → "Blueprint"
   - Connect to repository
   - Render detects `render.yaml`
   - Click "Apply"

3. **Verify**
   - Check Disks tab shows persistent disk
   - Check Environment shows `WORKSPACE_ROOT`
   - View logs for startup diagnostics

### Existing Deployment Update

If already deployed without persistent disk:

1. **Export existing data** (if any)
2. **Delete existing service**
3. **Create new Blueprint deployment**
4. **Verify persistent disk attached**
5. **Re-import data** (if needed)

## Monitoring

### Startup Logs

Check Render logs for:
```
============================================================
Impact Registry Startup
============================================================
Version: 1.0.0
Environment: Production
Workspace Root: /var/data/workspaces
Persistent Storage: ✓ Available
Projects Found: X
============================================================
```

### Disk Usage

Monitor through Render dashboard:
- Navigate to service → Disks
- View current usage
- Expand if approaching limit

### Project Discovery

Check logs for:
```
[DISCOVERY] Found project: ProjectName (uuid)
[HOME] Discovered X new project(s)
Loaded Projects (X):
  ✓ Project 1
  ✓ Project 2
```

## Backup Strategy

### Automatic Persistence

Persistent disk provides:
- ✅ Data retention across restarts
- ✅ Data retention across deployments
- ✅ Protection from container recreation

### Recommended Backups

**For Production:**

1. **Regular Exports**
   - Download `.irp` files periodically
   - Store in external location (S3, Google Drive)
   - Automated backup scripts (future)

2. **Project Archives**
   - Download individual projects as needed
   - Self-contained workspace files
   - Easy to restore by uploading

3. **Disaster Recovery**
   - Keep copy of all `.irp` files
   - Document restoration procedure
   - Test recovery process

## Troubleshooting

### Projects Not Appearing

**Symptom:** Projects missing after restart

**Check:**
1. Verify persistent disk in Render dashboard
2. Check `WORKSPACE_ROOT` environment variable
3. Review startup diagnostics in logs
4. Verify disk mount path matches env var

**Solution:**
- Ensure `render.yaml` committed to repository
- Redeploy using Blueprint
- Verify disk appears in Disks tab

### Workspace Validation Failed

**Symptom:** Error on startup about workspace unavailable

**Check:**
1. Disk mounted correctly
2. Mount path matches `WORKSPACE_ROOT`
3. Permissions on mounted directory

**Solution:**
- Verify disk configuration in `render.yaml`
- Check Render logs for mount errors
- Contact Render support if disk not mounting

### Discovery Not Finding Projects

**Symptom:** Projects exist but not discovered

**Check:**
1. Files in correct directory (`WORKSPACE_ROOT`)
2. Files have `.irp` extension
3. Files contain valid SQLite database
4. Discovery logs show errors

**Solution:**
- Verify file paths in logs
- Check file permissions
- Validate database schema
- Review discovery error messages

## Future Enhancements

### Not in Current Scope

- Automatic workspace backups to cloud storage
- Workspace version history
- Cloud synchronization across instances
- Multi-user workspace locking
- Workspace import/export UI

### Potential Improvements

1. **Cloud Storage Integration**
   - Automatic S3/GCS backup
   - Hybrid local + cloud storage
   - Disaster recovery automation

2. **Workspace Management**
   - Archive old projects
   - Workspace templates
   - Bulk operations

3. **Collaboration Features**
   - Workspace sharing
   - Access control
   - Audit logging

## Summary

✅ **Persistent disk configured** via `render.yaml`  
✅ **Environment-aware configuration** via `config.py`  
✅ **All services updated** to use `WORKSPACE_ROOT`  
✅ **Startup validation** ensures workspace accessible  
✅ **Enhanced diagnostics** show all loaded projects  
✅ **Deployment documented** with clear instructions  
✅ **All acceptance criteria met**  

**WPP-014 establishes the foundation for a true workspace-centric architecture where each `.irp` file is a durable, portable project artifact independent of the application lifecycle.**

This provides the persistence foundation needed for:
- AI-assisted discovery
- Client handoffs
- Backups and archiving
- Future collaboration features

**The workspace file is now the permanent source of truth!** 🎉
