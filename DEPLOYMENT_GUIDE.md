# Deployment Guide: Bangladesh Flood Predictor

This guide will help you deploy your full-stack application for free.

## Prerequisites
- A [GitHub](https://github.com) account.
- A [Render](https://render.com) account (for Backend & Database).
- A [Vercel](https://vercel.com) account (for Frontend).

---

## Step 1: Push Code to GitHub
1.  Create a new repository on GitHub.
2.  Push your project code to this repository.

## Step 2: Deploy Database (Render)
1.  Log in to Render and click **New +** -> **PostgreSQL**.
2.  Name: `flood-db`.
3.  Region: Choose one close to you (e.g., Singapore or Frankfurt).
4.  Plan: **Free**.
5.  Click **Create Database**.
6.  Wait for it to be created. Copy the **Internal Database URL** (starts with `postgres://...`).

## Step 3: Deploy Backend (Render)
1.  Click **New +** -> **Web Service**.
2.  Connect your GitHub repository.
3.  **Root Directory**: `backend`
4.  **Runtime**: `Python 3`
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
7.  **Environment Variables**:
    - Key: `DATABASE_URL`
    - Value: Paste the **Internal Database URL** from Step 2.
    - Key: `PYTHON_VERSION`
    - Value: `3.11.0`
8.  Click **Create Web Service**.
9.  Wait for deployment. Copy your backend URL (e.g., `https://flood-api.onrender.com`).

## Step 4: Deploy Frontend (Vercel)
1.  Log in to Vercel and click **Add New...** -> **Project**.
2.  Import your GitHub repository.
3.  **Framework Preset**: Vite.
4.  **Root Directory**: `frontend` (Click Edit to select the folder).
5.  **Environment Variables**:
    - Key: `VITE_API_URL`
    - Value: Your Render Backend URL (e.g., `https://flood-api.onrender.com`).
    *Note: You might need to update your frontend code to use this variable if you hardcoded `localhost`.*
6.  Click **Deploy**.

## Step 5: Final Check
- Open your Vercel URL.
- Try making a prediction.
- If it works, your data is being saved to the cloud database!
