# Deploying FastAPI Backend

## Deploy to Render

1. Go to https://render.com/ and sign up/log in.
2. Click "New +" > "Web Service".
3. Connect your GitHub repo and select the backend folder.
4. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host=0.0.0.0 --port=10000`
   - **Environment:** Python 3
5. Add any required environment variables (like `SECRET_KEY`).
6. Click "Create Web Service" and wait for deployment.
7. Copy your public URL for use in the frontend.

## Deploy to Heroku (Optional)

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
2. In your backend directory, run:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```
3. Heroku will use the `Procfile` to start your app.
4. Set environment variables in the Heroku dashboard if needed.

## Notes
- Make sure your `requirements.txt` is up to date.
- Do **not** commit secrets to GitHub. Use the platform's dashboard to set environment variables.
- Update your frontend to use the deployed backend URL. 