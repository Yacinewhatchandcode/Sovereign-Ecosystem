---
name: "Full System Deployment"
category: "DevOps"
triggers: ["deploy", "production", "release", "ship"]
tools: ["terminal", "git", "docker"]
priority: "high"
---

# Full System Deployment

Deploy the aSiReM Sovereign System to production with all safety checks.

## Prerequisites
- ✅ All tests passing
- ✅ Backend running without errors
- ✅ Frontend loads correctly
- ✅ Voice system functional
- ✅ Git repository clean

## Deployment Steps

### 1. Pre-Deployment Checks
```bash
# Check git status
git status

# Run tests
python3 test_system_complete.py

# Verify backend
ps aux | grep backend.py
```

### 2. Build Production Assets
```bash
# Minify JavaScript (if needed)
# Optimize images
# Bundle CSS
```

### 3. Database Backup
```bash
# Backup agent communications
cp sovereign-dashboard/agent_communications.db sovereign-dashboard/agent_communications.db.backup

# Backup knowledge store
cp sovereign-dashboard/knowledge_store.json sovereign-dashboard/knowledge_store.json.backup
```

### 4. Deploy Backend
```bash
# Stop existing server
pkill -f "python.*backend.py"

# Start production server
nohup python3 backend.py > logs/production.log 2>&1 &

# Verify startup
tail -f logs/production.log
```

### 5. Deploy Frontend
```bash
# Frontend is served by backend, no separate deployment needed
# Verify at http://localhost:8082/
```

### 6. Post-Deployment Verification
```bash
# Test API endpoints
curl http://localhost:8082/api/status

# Test WebSocket
# (Use browser console to verify WebSocket connection)

# Test voice system
# (Use dashboard podcast feature)
```

## Rollback Procedure

If deployment fails:

```bash
# Stop new server
pkill -f "python.*backend.py"

# Restore database
cp sovereign-dashboard/agent_communications.db.backup sovereign-dashboard/agent_communications.db

# Restart previous version
git checkout <previous-commit>
python3 backend.py > logs/rollback.log 2>&1 &
```

## Monitoring

After deployment, monitor:
- Server logs: `tail -f logs/production.log`
- System metrics: Check dashboard at `/api/status`
- Agent activity: Monitor WebSocket messages
- Error rate: Check for exceptions in logs

## Success Criteria

- ✅ Backend responds to health checks
- ✅ Dashboard loads without errors
- ✅ WebSocket connects successfully
- ✅ Voice commands work
- ✅ All agents operational
- ✅ No critical errors in logs

## Notes

- Default port: 8082
- Logs directory: `logs/`
- Database: `sovereign-dashboard/agent_communications.db`
- Assets: `sovereign-dashboard/assets/`
