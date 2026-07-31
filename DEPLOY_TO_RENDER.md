# Deploying TimeBucks Autopilot to Render.com (100% Free 24/7 Hosting) 🚀

[Render.com](https://render.com) is a popular cloud hosting platform that runs Python web services 24/7 for free!

---

## 📋 3-Step Deployment Guide

### Step 1: Create a Free Render Account & GitHub Repo
1. Sign up for a free account at [render.com](https://render.com).
2. Create a new GitHub repository (e.g., `timebucks-autopilot`) and push the files from `c:/Users/VICKY/Desktop/antigravity/render_deployment` (`app.py`, `requirements.txt`).

### Step 2: Create a New Web Service on Render
1. On your Render dashboard, click **New +** ➔ **Web Service**.
2. Connect your GitHub repository (`timebucks-autopilot`).
3. Fill in the deployment details:
   - **Name**: `timebucks-autopilot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: **Free**

### Step 3: Launch 24/7 Cloud Bot
1. Click **Create Web Service**.
2. Render will automatically build and deploy your app.
3. Your bot will run 24/7 on your custom URL (e.g., `https://timebucks-autopilot.onrender.com`), automatically claiming **Hourly Crown Pools ($1.76+)** and **Daily Streaks**!
