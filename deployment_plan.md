# Railway Deployment Plan

This document outlines the step-by-step procedure to deploy the Google MCP Server to [Railway](https://railway.app/) and configure it for headless production execution.

---

## The Challenge of Headless Google OAuth
Google's standard OAuth 2.0 flow is designed for interactive environments where a browser can open and receive redirects. Headless environments like Railway cannot execute browser prompts. 

### Solution
1. Execute the authentication process locally first to generate the local `token.json` file containing the OAuth session and refresh token.
2. Store the contents of `credentials.json` and `token.json` directly as environment variables in Railway.
3. Enable `AUTO_APPROVE` to bypass blocking terminal console checks.

---

## Step-by-Step Deployment Instructions

### Step 1: Initialize Git and Ignore Secrets
Create a `.gitignore` file to ensure you do not accidentally commit client secrets or tokens to GitHub.

1. Create a `.gitignore` file in `google-mcp-server/`:
   ```text
   credentials.json
   token.json
   __pycache__/
   .env
   .venv/
   ```
2. Initialize and commit your files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Google MCP Server"
   ```
3. Push your repository to a private GitHub repository.

---

### Step 2: Retrieve JSON Payloads
We need to format the contents of `credentials.json` and `token.json` as single-line strings.

1. **Client Credentials**: Open `credentials.json` and copy the entire JSON object.
2. **Authorized Token**: Ensure you have successfully run `python auth.py` locally to generate `token.json`. Open `token.json` and copy its entire JSON object.

---

### Step 3: Deploy to Railway

1. Log in to [Railway](https://railway.app/).
2. Click **New Project** > **Deploy from GitHub repository**.
3. Select your repository.
4. Click **Deploy Now**. (The initial build may fail or idle until variables are set, which is normal).

---

### Step 4: Configure Variables in Railway
Once the service is created, go to the **Variables** tab of your service in Railway and add the following environment variables:

| Variable Name | Value | Description |
|:---|:---|:---|
| `PORT` | `8000` | The port the FastAPI app exposes. (Railway automatically binds external traffic to this port). |
| `AUTO_APPROVE` | `true` | Bypasses the console approval (`Approve? (y/n)`) prompt since headless environments lack interactive terminals. |
| `GOOGLE_CREDENTIALS_JSON` | *[Paste entire contents of `credentials.json` here]* | Raw JSON configuration from Google Cloud Console. |
| `GOOGLE_TOKEN_JSON` | *[Paste entire contents of `token.json` here]* | Raw JSON authentication credentials containing the active session & refresh token. |

*Note: Ensure both JSON variables are valid, full JSON objects.*

---

### Step 5: Verify Deployment
1. Navigate to the **Deployments** tab in Railway to watch the build finish. Railway will read the `Dockerfile`, install the requirements, and spin up the server on the configured port.
2. Under your service settings, click **Generate Domain** to assign a public HTTPS domain to the application (e.g., `https://google-mcp-server-production.up.railway.app`).
3. Send a test request to your production endpoint to verify integration:
   ```bash
   curl -X POST https://YOUR_RAILWAY_URL.up.railway.app/create_email_draft \
        -H "Content-Type: application/json" \
        -d '{
              "to": "your-test-email@example.com",
              "subject": "Railway Deployment Test",
              "body": "Hello! This draft was generated from the Google MCP server running on Railway."
            }'
   ```
4. Verify in Gmail that the draft was successfully created, and check the Railway application logs to verify the operation completed without prompting.
