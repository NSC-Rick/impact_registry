# Render Persistent Disk Configuration

## Overview

This application uses Render's Persistent Disk feature to ensure all project workspace data survives application restarts, deployments, and scaling events.

## Configuration

### render.yaml

The `render.yaml` file in the repository root configures:

```yaml
disk:
  name: impact-registry-workspaces
  mountPath: /opt/render/project/src/workspaces
  sizeGB: 1
```

### What This Means

**Mount Path:** `/opt/render/project/src/workspaces`
- On Render, the persistent disk is mounted at this absolute path
- The application's `workspaces/` directory maps to this location
- All `.irp` files written to `workspaces/` are stored on the persistent disk

**Size:** 1GB
- Starting size for workspace storage
- Can be expanded as needed through Render dashboard
- Sufficient for 100-200 typical projects

**Cost:** ~$0.25/month per GB

## Data Persistence

### What Gets Saved (Persistent Disk)

✅ **All project workspaces** (`workspaces/*.irp`)
- SQLite database files
- Project metadata
- Impact registry data
- Enterprise assets
- All user-created content

✅ **Project registry** (`workspaces/project_registry.json`)
- List of all discovered projects
- Project metadata cache

### What Gets Rebuilt (Ephemeral)

❌ **Application code**
- Redeployed from GitHub on every deploy
- Always uses latest committed code

❌ **Python dependencies**
- Reinstalled from `requirements.txt` on every deploy
- Ensures consistent environment

❌ **Temporary files**
- Cleared on restart
- Not needed for persistence

## How It Works

### Project Creation Flow

1. User creates project "Client ABC"
2. Application writes to `workspaces/Client_ABC.irp`
3. File is written to persistent disk at `/opt/render/project/src/workspaces/Client_ABC.irp`
4. Data persists across restarts

### Project Discovery Flow

1. Application starts
2. Home page runs `workspace.discover_projects()`
3. Scans persistent disk at `/opt/render/project/src/workspaces/`
4. Finds all `.irp` files
5. Reads metadata from each database
6. Populates project registry
7. Projects available for selection

### After Deployment

1. Render deploys new code
2. Container restarts with new code
3. Persistent disk remains intact
4. Application discovers existing projects
5. All data available immediately

## Deployment

### First-Time Setup

When deploying with `render.yaml`:

1. Render creates the persistent disk automatically
2. Disk is mounted at specified path
3. Directory starts empty
4. Projects created by users populate the disk

### Existing Deployment

If you already have a Render deployment without persistent disk:

**⚠️ WARNING:** Adding a persistent disk to an existing service will NOT preserve existing data (it was ephemeral).

**Steps:**
1. Export any important data before adding disk
2. Update service to use `render.yaml` blueprint
3. Render will create new persistent disk
4. Re-import data if needed

## Monitoring

### Disk Usage

Monitor disk usage through Render dashboard:
- Navigate to service → Disks tab
- View current usage
- Expand size if needed

### Typical Usage

- **Empty project:** ~100KB
- **Small project (10 impacts):** ~200KB
- **Medium project (100 impacts):** ~500KB
- **Large project (1000 impacts):** ~2-5MB

**1GB supports:**
- 200+ large projects
- 1000+ small projects

## Scaling

### Expanding Disk Size

If you need more space:

1. Go to Render dashboard
2. Navigate to service → Disks
3. Click on `impact-registry-workspaces`
4. Increase size (e.g., 1GB → 5GB)
5. Confirm change
6. Service will restart with larger disk

**Note:** Disk size can be increased but NOT decreased.

### Cost Scaling

- 1GB: $0.25/month
- 5GB: $1.25/month
- 10GB: $2.50/month

## Backup Strategy

### Automatic Persistence

Persistent disk provides automatic retention:
- Data survives restarts
- Data survives deployments
- No manual intervention needed

### Recommended Backups

For production use:

1. **Regular Exports**
   - Use Monitor workspace to export data
   - Download `.irp` files periodically
   - Store backups externally (S3, Google Drive, etc.)

2. **Project Archives**
   - Download individual `.irp` files
   - Self-contained workspace files
   - Easy to restore by uploading back to `workspaces/`

3. **Automated Backups** (Future Enhancement)
   - Scheduled exports to cloud storage
   - Automated backup scripts
   - Version control for data

## Troubleshooting

### Projects Not Appearing After Restart

**Symptom:** Projects created before restart are missing

**Diagnosis:**
1. Check if persistent disk is configured in `render.yaml`
2. Verify disk is mounted in Render dashboard
3. Check build logs for disk mount confirmation

**Solution:**
- Ensure `render.yaml` is committed to repository
- Redeploy using Blueprint (not manual web service)
- Verify disk appears in Render dashboard → Disks tab

### Disk Full

**Symptom:** Cannot create new projects

**Diagnosis:**
- Check disk usage in Render dashboard
- Verify available space

**Solution:**
- Expand disk size through Render dashboard
- Archive/delete old projects if needed
- Export and remove unused workspaces

### Data Loss After Deployment

**Symptom:** All projects disappeared after code deployment

**Cause:** Persistent disk not configured (using ephemeral storage)

**Solution:**
- Add `render.yaml` to repository
- Redeploy as Blueprint
- Data from before disk configuration is lost (ephemeral)
- Future data will persist

## Migration from Ephemeral to Persistent

If you're currently deployed WITHOUT persistent disk:

### Before Migration

1. **Export all data:**
   - Download all `.irp` files from current deployment
   - Use Monitor workspace to export data
   - Save `project_registry.json` if accessible

### During Migration

1. Add `render.yaml` to repository
2. Commit and push to GitHub
3. In Render dashboard:
   - Delete existing service (data will be lost anyway)
   - Create new Blueprint deployment
   - Select repository with `render.yaml`
4. Render creates service with persistent disk

### After Migration

1. Re-import data:
   - Upload `.irp` files to `workspaces/` directory
   - Or recreate projects through UI
2. Verify projects appear after restart
3. Test create/restart/discover cycle

## Best Practices

### Development

- Test locally without persistent disk first
- Use `workspaces/` directory consistently
- Don't hardcode absolute paths

### Production

- Always use `render.yaml` for deployment
- Monitor disk usage regularly
- Export critical projects as backups
- Plan for disk expansion as usage grows

### Architecture

- One project = one `.irp` file
- Self-contained workspace files
- Filesystem as source of truth
- Registry rebuilt from filesystem on startup

## Future Enhancements

### Potential Improvements

1. **Cloud Storage Integration**
   - Store `.irp` files in S3/GCS
   - Hybrid local + cloud storage
   - Automatic cloud backups

2. **PostgreSQL Migration**
   - Centralized database
   - Better multi-user support
   - Managed backups

3. **Workspace Sync**
   - Multi-instance synchronization
   - Distributed deployments
   - Real-time replication

## Summary

✅ **Persistent disk configured** via `render.yaml`  
✅ **All workspace data persists** across restarts  
✅ **Automatic discovery** on every startup  
✅ **Self-contained workspaces** easy to backup  
✅ **Scalable storage** expandable as needed  
✅ **Cost-effective** starting at $0.25/month  

**The filesystem-based architecture + persistent disk = robust, reliable project persistence!**
