# 📋 Deployment Verification Checklist

## Before Starting
- [ ] You have access to your Vercel dashboard
- [ ] You have Vercel CLI installed (`npm install -g vercel`)
- [ ] Project changes are committed and pushed

## Deployment Process
- [ ] **Step 1**: Delete old project from Vercel dashboard
- [ ] **Step 2**: Run `./deploy.sh` script
- [ ] **Step 3**: Follow CLI prompts (say No to linking existing project)
- [ ] **Step 4**: Wait for deployment to complete

## Post-Deployment Testing

### Health Check
- [ ] Test: `GET https://your-project.vercel.app/api/health`
- [ ] Expected: `{"status": "healthy", "service": "Entrepedia AI Platform"}`

### Authentication Test
- [ ] Test: `POST https://your-project.vercel.app/api/auth/login`
- [ ] Body: `username=admin@entrepedia.ai&password=admin123`
- [ ] Expected: `{"access_token": "...", "token_type": "bearer"}`

### Frontend Integration
- [ ] Update frontend API URL to new Vercel domain
- [ ] Test login from frontend
- [ ] Verify CORS is working (no console errors)

## Success Criteria
- [ ] ✅ Health endpoint returns 200 OK
- [ ] ✅ Login endpoint accepts credentials
- [ ] ✅ JWT token is returned
- [ ] ✅ Frontend can authenticate users
- [ ] ✅ No 500 errors in Vercel logs

## If Something Fails

### Check Vercel Logs
1. Go to Vercel dashboard → Your project
2. Click "Functions" tab
3. Check logs for any Python errors

### Common Issues
- **"Function not found"**: Check vercel.json routing
- **"Import errors"**: Verify requirements.txt
- **"CORS errors"**: Check network tab in browser

### Rollback Plan
If deployment fails completely:
1. Keep old authentication working locally
2. Debug new deployment without affecting users
3. Update DNS only when fully working

---

## 🎯 Final Result

After completing this checklist, you should have:
- ✅ Clean Vercel deployment without logger errors
- ✅ Working authentication API
- ✅ Frontend integration ready
- ✅ No more 500 errors

**Estimated total time: 5-10 minutes**