# Render Deployment Configuration

This application can be deployed on Render.com with the following setup:

## Backend Deployment (Web Service)

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure the service:**
   - **Name:** `forensics-engine-backend`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables:**
   ```
   MONGO_URL=<your_mongodb_atlas_connection_string>
   DB_NAME=forensics_db
   CORS_ORIGINS=*
   ```

5. **MongoDB Setup:**
   - Create a free MongoDB Atlas cluster at https://www.mongodb.com/cloud/atlas
   - Get connection string and add to MONGO_URL environment variable
   - Format: `mongodb+srv://<username>:<password>@cluster.mongodb.net/<dbname>?retryWrites=true&w=majority`

## Frontend Deployment (Static Site)

1. **Create a new Static Site** on Render
2. **Connect your GitHub repository**
3. **Configure the service:**
   - **Name:** `forensics-engine-frontend`
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Build Command:** `yarn install && yarn build`
   - **Publish Directory:** `build`

4. **Environment Variables:**
   ```
   REACT_APP_BACKEND_URL=<your_backend_render_url>
   ```
   Replace with the URL from your backend deployment (e.g., `https://forensics-engine-backend.onrender.com`)

## Alternative: Single Service Deployment

If you prefer to deploy both frontend and backend as a single service:

1. **Create a Web Service**
2. **Build Command:**
   ```bash
   cd backend && pip install -r requirements.txt && cd ../frontend && yarn install && yarn build
   ```

3. **Start Command:**
   ```bash
   cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
   ```

4. Modify backend to serve frontend static files (add to server.py):
   ```python
   from fastapi.staticfiles import StaticFiles
   
   # Serve frontend build
   app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="frontend")
   ```

## Post-Deployment Checklist

- [ ] Backend URL is accessible
- [ ] Frontend can connect to backend
- [ ] MongoDB connection is working
- [ ] CSV upload functionality works
- [ ] Graph visualization renders correctly
- [ ] JSON download works
- [ ] CORS is properly configured

## Troubleshooting

### Backend not starting
- Check MongoDB connection string
- Verify all environment variables are set
- Check build logs for Python dependency errors

### Frontend can't connect to backend
- Verify REACT_APP_BACKEND_URL is correct
- Check CORS_ORIGINS in backend includes frontend domain
- Use browser console to check for CORS errors

### Performance Issues
- Upgrade to paid Render plan for better performance
- Optimize MongoDB indexes for faster queries
- Consider Redis caching for frequent queries

## Cost Estimation

**Free Tier:**
- Backend: Free (spins down after 15 min of inactivity)
- Frontend: Free
- MongoDB Atlas: Free (512MB storage)

**Paid Plans:**
- Backend: $7/month (always on)
- Frontend: Free
- MongoDB Atlas: $9/month (2GB storage)

Total: ~$16/month for production-ready deployment

## Notes

- Render free tier has cold start delay (~30 seconds)
- For hackathon evaluation, free tier is sufficient
- Remember to keep the app active during evaluation period
- Set up uptime monitoring (e.g., UptimeRobot) to prevent cold starts
