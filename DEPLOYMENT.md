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

#### Option A: Deploy with render.yaml (Recommended)

**This repository includes `render.yaml` for automatic configuration.**

1. Log in to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect to GitHub repository: `NSC-Rick/impact_registry`
4. Render will automatically detect `render.yaml` and configure:
   - Web service with Python runtime
   - Persistent disk mounted at `/workspaces`
   - Environment variables
   - Build and start commands
5. Click "Apply" to deploy

**Persistent Disk:**
- **Name:** `impact-registry-workspaces`
- **Mount Path:** `/opt/render/project/src/workspaces`
- **Size:** 1GB (expandable)
- **Cost:** ~$0.25/month

#### Option B: Manual Configuration (Alternative)

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
5. Add Persistent Disk:
   - Go to "Disks" tab
   - Click "Add Disk"
   - **Name:** `impact-registry-workspaces`
   - **Mount Path:** `/opt/render/project/src/workspaces`
   - **Size:** 1GB
6. Add Environment Variables:
   - `STREAMLIT_SERVER_HEADLESS=true`
   - `STREAMLIT_SERVER_ENABLE_CORS=false`
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`

#### Deploy

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

### Data Persistence

**Persistent Disk Configuration:**

The `render.yaml` file configures a persistent disk that ensures all project workspaces survive:
- ✅ Application restarts
- ✅ Code deployments
- ✅ Service scaling
- ✅ Container rebuilds

**What Gets Persisted:**
- All `.irp` workspace files in `workspaces/` directory
- Project databases (SQLite)
- Project metadata
- All impact registry data

**What Doesn't Persist (Ephemeral):**
- Application code (redeployed from GitHub)
- Python dependencies (reinstalled on deploy)
- Temporary files
- Session state

### Database Backup

**Automatic Persistence:**
- Persistent disk provides automatic data retention
- No manual backup needed for basic use

**Recommended for Production:**
- Export projects regularly via Monitor workspace
- Download `.irp` files as backups
- Consider PostgreSQL for multi-user deployments
- Implement automated backup strategy for critical data

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
