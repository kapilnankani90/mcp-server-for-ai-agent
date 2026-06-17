import base64
from email.message import EmailMessage
from googleapiclient.discovery import build

def create_email_draft(to: str, subject: str, body: str, creds) -> dict:
    """
    Creates a draft email in the user's Gmail account.
    
    Parameters:
    - to (str): The recipient's email address.
    - subject (str): The subject line of the email.
    - body (str): The body text of the email.
    - creds: Authorized Google OAuth2 credentials.
    
    Returns:
    - dict: The response from the Gmail drafts create API call containing draft details.
    """
    # Initialize Gmail API client
    service = build('gmail', 'v1', credentials=creds)
    
    # Construct the email message using the EmailMessage utility
    mime_msg = EmailMessage()
    mime_msg['To'] = to
    mime_msg['Subject'] = subject
    mime_msg.set_content(body)
    
    # Convert the message to bytes and encode to base64url format as required by the Gmail API
    raw_bytes = mime_msg.as_bytes()
    raw_message = base64.urlsafe_b64encode(raw_bytes).decode('utf-8')
    
    # Prepare draft request payload
    draft_body = {
        'message': {
            'raw': raw_message
        }
    }
    
    # Execute draft creation
    draft = service.users().drafts().create(
        userId='me',
        body=draft_body
    ).execute()
    
    return draft
