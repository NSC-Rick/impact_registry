# Impact Registry - Deployment Guide

## Deployment Configuration

### Runtime Environment

**Python Version:** 3.11.10  
**Platform:** Render (Web Service)  
**Repository:** https://github.com/NSC-Rick/impact_registry

### Dependencies

```
streamlit==1.39.0
sqlalchemy==2.0.36
pandas==2.2.3
openpyxl==3.1.5
```

## Render Deployment

### Prerequisites

1. GitHub repository: `https://github.com/NSC-Rick/impact_registry`
2. Render account connected to GitHub
3. Repository access configured

### Deployment Steps

#### 1. Create New Web Service

1. Log in to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect to GitHub repository: `NSC-Rick/impact_registry`
4. Configure service:
   - **Name:** `impact-registry`
   - **Region:** Choose closest to users
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

#### 2. Environment Variables

No environment variables required for basic deployment.

Optional:
- `STREAMLIT_SERVER_HEADLESS=true`
- `STREAMLIT_SERVER_ENABLE_CORS=false`

#### 3. Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone repository
   - Detect `runtime.txt` (Python 3.11.10)
   - Install dependencies from `requirements.txt`
   - Start Streamlit application
3. Monitor build logs for completion

### Expected Build Output

```
==> Cloning from https://github.com/NSC-Rick/impact_registry...
==> Checking out commit 61184ca in branch main
==> Downloading cache...
==> Using Python version 3.11.10 via runtime.txt
==> Running build command 'pip install -r requirements.txt'...
    Collecting streamlit==1.39.0
    Collecting sqlalchemy==2.0.36
    Collecting pandas==2.2.3
    Collecting openpyxl==3.1.5
    Successfully installed...
==> Build successful
==> Starting service with 'streamlit run app.py --server.port=$PORT --server.address=0.0.0.0'
```

### Deployment Verification

1. **Service Status:** Check Render dashboard shows "Live"
2. **Application Access:** Open provided URL (e.g., `https://impact-registry.onrender.com`)
3. **Functionality Test:**
   - Application loads without errors
   - Setup page accessible
   - Database initializes successfully
   - Navigation works across all pages

## Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/NSC-Rick/impact_registry.git
cd impact_registry

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Local Access

Application runs at: `http://localhost:8501`

## File Structure

```
impact_registry/
├── runtime.txt              # Python version for Render
├── requirements.txt         # Python dependencies
├── app.py                   # Application entry point
├── DEPLOYMENT.md           # This file
├── README.md               # User documentation
├── database/
│   └── schema.py           # Database schema
├── models/                 # Data models
├── services/               # Business logic
└── pages/                  # Streamlit pages
    ├── 01_Setup.py
    ├── 06_Capture_Workspace.py
    ├── 07_Enrichment_Workspace.py
    ├── 08_Analyze_Workspace.py
    ├── 09_Enterprise_Asset_Registry.py
    ├── 10_Bulk_Operations.py
    ├── 11_Question_Engine.py
    ├── 12_Impact_Detail.py
    └── 13_Monitor_Workspace.py
```

## Troubleshooting

### Build Failures

**Issue:** Dependency installation fails  
**Solution:** Verify `requirements.txt` versions are compatible

**Issue:** Python version mismatch  
**Solution:** Verify `runtime.txt` specifies `python-3.11.10`

### Runtime Issues

**Issue:** Application won't start  
**Solution:** Check start command includes `--server.port=$PORT --server.address=0.0.0.0`

**Issue:** Database errors  
**Solution:** Database is SQLite and auto-initializes. Check file permissions.

**Issue:** Page navigation broken  
**Solution:** Verify all page files exist in `pages/` directory

### Performance

**Issue:** Slow initial load  
**Solution:** Normal for Render free tier. Consider upgrading to paid tier.

**Issue:** Application sleeps after inactivity  
**Solution:** Render free tier spins down after 15 minutes. Upgrade to prevent.

## Maintenance

### Updating Dependencies

1. Update `requirements.txt` with new versions
2. Test locally
3. Commit and push to GitHub
4. Render auto-deploys from `main` branch

### Database Backup

SQLite database is stored in application directory. For production:
- Consider PostgreSQL for multi-user deployments
- Implement regular backup strategy
- Export data regularly via Monitor workspace

## Production Recommendations

### For Production Use

1. **Database:** Migrate to PostgreSQL
2. **Hosting:** Upgrade to paid Render tier
3. **Monitoring:** Enable Render metrics
4. **Backups:** Implement automated backups
5. **Authentication:** Add user authentication (Streamlit supports this)
6. **SSL:** Render provides SSL automatically

### Scaling Considerations

- **Users:** 1-10 users: Free tier acceptable
- **Users:** 10-50 users: Paid tier recommended
- **Users:** 50+ users: Consider dedicated hosting
- **Data:** >1000 impacts: Consider PostgreSQL
- **Performance:** Monitor response times, upgrade as needed

## Support

**Repository:** https://github.com/NSC-Rick/impact_registry  
**Documentation:** See WPP-001 through WPP-011 specifications  
**Issues:** Use GitHub Issues for bug reports

## Version History

**v1.0 (WPP-011)** - Deployment stabilization
- Python 3.11.10
- Streamlit 1.39.0
- Render-compatible dependencies

**v0.9 (WPP-009)** - Monitor Workspace
- Complete 9-workspace implementation
- Full documentation

## License

Internal use - NSBI Impact Registry
