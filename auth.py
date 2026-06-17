import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Google API Scopes required by the application
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.compose'
]

def get_credentials():
    """
    Retrieves Google OAuth 2.0 credentials.
    Loads from token.json or GOOGLE_TOKEN_JSON environment variable.
    If credentials don't exist or are invalid/expired, runs the OAuth flow.
    """
    creds = None

    # 1. Try to load credentials from the environment variable (primarily for Railway/Production)
    token_env = os.environ.get("GOOGLE_TOKEN_JSON")
    if token_env:
        try:
            print("Loading credentials from GOOGLE_TOKEN_JSON environment variable...")
            token_data = json.loads(token_env)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"Error loading credentials from GOOGLE_TOKEN_JSON: {e}")

    # 2. Try to load from the local token.json file
    if not creds and os.path.exists('token.json'):
        try:
            print("Loading credentials from token.json file...")
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}")

    # If credentials exist but are expired, attempt to refresh them
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                print("Credentials expired. Attempting to refresh...")
                creds.refresh(Request())
                # If we loaded from a file, update it with the new refreshed token
                if os.path.exists('token.json'):
                    with open('token.json', 'w') as token_file:
                        token_file.write(creds.to_json())
                    print("Updated token.json with refreshed credentials.")
                else:
                    print("Refreshed credentials. (Set GOOGLE_TOKEN_JSON with the refreshed token if running on a server.)")
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None
        else:
            creds = None

    # 3. If credentials still do not exist or are invalid, run OAuth flow
    if not creds or not creds.valid:
        print("No valid credentials found. Initiating Google OAuth 2.0 authorization flow...")
        
        credentials_env = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if credentials_env:
            try:
                print("Parsing client credentials from GOOGLE_CREDENTIALS_JSON env var...")
                client_config = json.loads(credentials_env)
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            except Exception as e:
                raise ValueError(f"Failed to load client config from GOOGLE_CREDENTIALS_JSON: {e}")
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json file is missing! Please place it in the application root directory "
                    "or set the GOOGLE_CREDENTIALS_JSON environment variable."
                )
            print("Loading client credentials from credentials.json file...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

        # Run the local authorization server to acquire user authentication via browser.
        # This will block and open the browser.
        creds = flow.run_local_server(port=0)
        
        # Save the token for subsequent runs
        try:
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
            print("Successfully authorized! Saved token to token.json.")
        except Exception as e:
            print(f"Authorized, but failed to write token.json: {e}")

    return creds

if __name__ == "__main__":
    # Running auth.py directly allows generating token.json before starting the FastAPI server
    print("--- Google MCP Server: Auth Initialization Check ---")
    try:
        credentials = get_credentials()
        print("Status: Active & Valid credentials obtained.")
    except Exception as e:
        print(f"Status: Authorization failed: {e}")
