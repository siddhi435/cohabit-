# OAuth Setup (GitHub & Google)

This file explains how to register OAuth apps for GitHub and Google and how to set up local environment variables for the CoHabit app.

## Required environment variables
Create a `.env` file in the project root with the following values:

- `SECRET_KEY` - a long random secret for session signing (example: `dev-secret-key` for local testing)
- `GITHUB_CLIENT_ID` - GitHub OAuth app client id
- `GITHUB_CLIENT_SECRET` - GitHub OAuth app client secret
- `GOOGLE_CLIENT_ID` - Google OAuth client id
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret

Example `.env`:

```env
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=replace_with_a_random_secret
```

## GitHub App registration
1. Go to https://github.com/settings/developers -> OAuth Apps -> New OAuth App.
2. Application name: CoHabit (or whatever you prefer).
3. Homepage URL: `http://127.0.0.1:8000/`
4. Authorization callback URL: `http://127.0.0.1:8000/auth/github`
5. Register App and copy the `Client ID` and `Client Secret` into your `.env`.

## Google App registration
1. Go to Google Cloud Console (https://console.cloud.google.com/).
2. Create or select a project, then go to "APIs & Services" -> "OAuth consent screen" and configure a test user.
3. Go to "Credentials" -> "Create Credentials" -> "OAuth client ID".
4. Choose "Web application".
5. Authorized JavaScript origins: `http://127.0.0.1:8000`
6. Authorized redirect URIs: `http://127.0.0.1:8000/auth/google`
7. Copy the `Client ID` and `Client Secret` into your `.env`.

## Notes about testing locally
- The app uses `SessionMiddleware` and a small file-backed store at `data/sessions.json` to persist sign-ins between server restarts (local dev convenience). Ensure the `data/` folder is writable.
- Start the server with uvicorn: `uvicorn main:app --reload` and open `http://127.0.0.1:8000`.
- Use the header -> "Sign in with GitHub" or "Sign in with Google" links to begin OAuth flows.
- To sign out, the frontend calls `POST /api/logout`, which removes the persistent session and clears the cookie session.

## Deploying to Render

The repository includes a `render.yaml` Blueprint. Push the project to GitHub, then in Render choose **New -> Blueprint**, connect the repository, and deploy the `cohabit` web service. The Blueprint installs `requirements.txt`, starts Uvicorn on Render's assigned port, and generates a `SECRET_KEY`.

After the first deploy, copy the `https://<your-service>.onrender.com` URL from the Render dashboard. To enable OAuth, add the GitHub and Google client ID and secret values as Render environment variables. Set each provider's callback URL to `https://<your-service>.onrender.com/auth/github` or `https://<your-service>.onrender.com/auth/google`, and use `https://<your-service>.onrender.com` as the Google JavaScript origin.

Render's local filesystem is not durable across service restarts or redeploys. The file-backed sessions and user data are suitable for a demo, but should be moved to persistent database or storage for production.
