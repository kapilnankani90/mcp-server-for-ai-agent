from googleapiclient.discovery import build

def append_to_doc(doc_id: str, content: str, creds) -> dict:
    """
    Appends the given content string to a Google Document.
    
    Parameters:
    - doc_id (str): The Google Document ID.
    - content (str): The text content to append.
    - creds: Authorized Google OAuth2 credentials.
    
    Returns:
    - dict: The response from the Google Docs batchUpdate API call.
    """
    # Initialize Google Docs API client
    service = build('docs', 'v1', credentials=creds)
    
    # Retrieve the document metadata and content structure
    doc = service.documents().get(documentId=doc_id).execute()
    
    body = doc.get('body', {})
    content_elements = body.get('content', [])
    
    # Identify the index to insert content. 
    # To append, we want to insert right before the very end of the body content.
    # The last element represents the document body end-point.
    # Indices in Google Docs are 1-based.
    end_index = 1
    if content_elements:
        # Get the endIndex of the last element, and subtract 1 to insert inside the document's body section.
        # This prevents inserting after the final document boundary.
        end_index = content_elements[-1].get('endIndex', 1) - 1
        if end_index < 1:
            end_index = 1
            
    # Prepare the batch update request payload
    requests = [
        {
            'insertText': {
                'location': {
                    'index': end_index
                },
                'text': content
            }
        }
    ]
    
    # Execute batch update
    response = service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()
    
    return response
