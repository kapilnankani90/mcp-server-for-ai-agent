# Google MCP Server

A Python-based MCP-style server that integrates with Google Docs and Gmail, providing endpoints to append content to documents and create email drafts. Features a manual interactive terminal approval system for local environments, and environment-driven configurations for headless cloud environments like Railway.

## Project Structure
```text
google-mcp-server/
│
├── auth.py             # Google OAuth 2.0 authentication handler
├── docs_tool.py         # Google Docs API utility (append content)
├── gmail_tool.py        # Gmail API utility (create email draft)
├── server.py           # FastAPI app & approval prompt endpoint controller
│
├── requirements.txt    # Application dependencies
├── Dockerfile          # Container configuration for production
├── README.md           # Instructions & local setup documentation
└── deployment_plan.md  # Detailed Railway deployment instructions
```

---

## 1. Google Cloud Console Setup (Prerequisites)

Before running the server, you need to set up a project in the Google Cloud Console:

1. **Create/Select a Project**: Go to the [Google Cloud Console](https://console.google.com/) and create a new project.
2. **Enable Google APIs**:
   - Navigate to **API & Services > Library**.
   - Search for **Google Docs API** and click **Enable**.
   - Search for **Gmail API** and click **Enable**.
3. **Configure the OAuth Consent Screen**:
   - Go to **API & Services > OAuth consent screen**.
   - Choose **External** user type and click **Create**.
   - Fill in the required application registration details.
   - **Scopes**: Add the following scopes:
     - `https://www.googleapis.com/auth/documents`
     - `https://www.googleapis.com/auth/gmail.compose`
   - **Test Users** (CRITICAL): Under the "Test Users" section, click **Add Users** and enter the Gmail address you will use to log in and test. If you skip this, authentication will fail with a "Developer details not verified" error.
4. **Create Desktop Credentials**:
   - Go to **API & Services > Credentials**.
   - Click **Create Credentials** and select **OAuth client ID**.
   - Select **Desktop app** as the Application Type.
   - Name your client (e.g., `Google MCP Client`) and click **Create**.
   - Download the client secrets JSON file.
   - Rename the downloaded file to `credentials.json` and place it in the root folder of this project (`google-mcp-server/`).

---

## 2. Local Setup and Token Generation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate token.json**:
   Run the authentication handler script to start the local OAuth browser flow:
   ```bash
   python auth.py
   ```
   - This script will open your web browser automatically.
   - Select the Google Account added as a Test User.
   - Click "Continue" through warning pages (since it's a test application).
   - Grant permissions for Docs and Gmail.
   - Once completed, the browser will display "The authentication flow has completed..."
   - A `token.json` file will be auto-generated in your project directory. Keep this file secure as it contains authentication credentials.

---

## 3. Running the Server Locally

1. **Start the FastAPI server**:
   ```bash
   python server.py
   ```
   The server will start on `http://localhost:8000`.

2. **Console Approval Mechanics**:
   When any client requests a tool action via the POST endpoints, the server console will output the action name and request payload, and prompt for confirmation:
   ```text
   ==============================================
   [APPROVAL REQUIRED] Action: append_to_doc
   Payload: {'doc_id': 'your-doc-id', 'content': 'Hello, world!'}
   ==============================================
   Approve? (y/n): 
   ```
   - Typing **`y`** or **`yes`** will authorize the request to interact with the Google API.
   - Typing **`n`** or **`no`** will refuse authorization, resulting in a `403 Forbidden` response to the client.

---

## 4. Endpoints and Usage Examples

### 1. Append to Document
* **Endpoint**: `POST /append_to_doc`
* **Content-Type**: `application/json`
* **Request Body**:
  ```json
  {
    "doc_id": "YOUR_GOOGLE_DOCUMENT_ID",
    "content": "\nThis text is appended from the Google MCP Server!"
  }
  ```
* **cURL Command**:
  ```bash
  curl -X POST http://localhost:8000/append_to_doc \
       -H "Content-Type: application/json" \
       -d '{"doc_id": "YOUR_GOOGLE_DOCUMENT_ID", "content": "\nThis text is appended from the Google MCP Server!"}'
  ```

### 2. Create Email Draft
* **Endpoint**: `POST /create_email_draft`
* **Content-Type**: `application/json`
* **Request Body**:
  ```json
  {
    "to": "recipient@example.com",
    "subject": "Hello from Google MCP",
    "body": "This is a draft email body created via the FastAPI Google MCP server."
  }
  ```
* **cURL Command**:
  ```bash
  curl -X POST http://localhost:8000/create_email_draft \
       -H "Content-Type: application/json" \
       -d '{"to": "recipient@example.com", "subject": "Hello from Google MCP", "body": "This is a draft email body created via the FastAPI Google MCP server."}'
  ```

---

## 5. Deployment on Railway

For detailed, step-by-step instructions on deploying this project to Railway, managing environment-based secrets, and auto-bypassing approval prompts, see [deployment_plan.md](file:///c:/mcp%20server%20for%20ai%20agent/google-mcp-server/deployment_plan.md).
