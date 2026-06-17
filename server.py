import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import uvicorn

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from auth import get_credentials
from docs_tool import append_to_doc
from gmail_tool import create_email_draft

# Initialize FastAPI application
app = FastAPI(
    title="Google MCP Server",
    description="MCP-style server providing tools for Google Docs and Gmail with terminal approval logic.",
    version="1.0.0"
)

# Pydantic models for incoming request bodies
class AppendToDocRequest(BaseModel):
    doc_id: str = Field(..., description="The ID of the Google Doc to append content to.")
    content: str = Field(..., description="The text content to append to the document.")

class CreateEmailDraftRequest(BaseModel):
    to: str = Field(..., description="The recipient's email address.")
    subject: str = Field(..., description="The subject of the email.")
    body: str = Field(..., description="The plain text body content of the email.")

async def ask_approval(action_name: str, payload: dict) -> bool:
    """
    Prints the action details to the terminal and prompts the administrator for manual approval.
    Blocks the current request handler until the user inputs 'y' or 'n'.
    Utilizes asyncio.to_thread to prevent blocking the FastAPI event loop.
    Supports auto-approval if the AUTO_APPROVE environment variable is set.
    """
    print(f"\n==============================================")
    print(f"[APPROVAL REQUIRED] Action: {action_name}")
    print(f"Payload: {payload}")
    print(f"==============================================")
    
    # 1. Handle auto-approve environment variable (critical for headless environments like Railway)
    auto_approve = os.environ.get("AUTO_APPROVE", "false").lower() in ("true", "1", "yes")
    if auto_approve:
        print(">>> Auto-approved (AUTO_APPROVE=true)")
        return True
        
    # 2. Check if we have an interactive terminal (stdin is a TTY)
    if not sys.stdin.isatty():
        print(">>> Stdin is not a TTY (non-interactive environment) and AUTO_APPROVE is not enabled.")
        print(">>> Action DECLINED automatically to prevent hanging.")
        return False

    # 3. Synchronous input function wrapped in asyncio.to_thread
    def get_terminal_approval() -> bool:
        try:
            while True:
                response = input("Approve? (y/n): ").strip().lower()
                if response in ('y', 'yes'):
                    print(">>> Action APPROVED by terminal administrator.")
                    return True
                elif response in ('n', 'no'):
                    print(">>> Action DECLINED by terminal administrator.")
                    return False
                print("Invalid input. Please enter 'y' or 'n'.")
        except EOFError:
            print(">>> EOF encountered on stdin. Action DECLINED.")
            return False

    return await asyncio.to_thread(get_terminal_approval)

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Root status page for the Google MCP Server.
    """
    return {
        "status": "online",
        "service": "Google MCP Server",
        "documentation": "/docs",
        "endpoints": {
            "append_to_doc": "POST /append_to_doc",
            "create_email_draft": "POST /create_email_draft"
        }
    }

@app.post("/append_to_doc", status_code=status.HTTP_200_OK)

async def endpoint_append_to_doc(request: AppendToDocRequest):
    """
    FastAPI endpoint to append text to a Google Doc.
    Prompts the console for approval before execution.
    """
    payload = request.model_dump()
    approved = await ask_approval("append_to_doc", payload)
    
    if not approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action rejected: approval denied."
        )
        
    try:
        # Load credentials (will trigger local server OAuth if token.json is missing)
        creds = get_credentials()
        result = append_to_doc(request.doc_id, request.content, creds)
        return {
            "status": "success",
            "message": "Content successfully appended to document.",
            "details": {
                "documentId": result.get("documentId")
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google API Error: {str(e)}"
        )

@app.post("/create_email_draft", status_code=status.HTTP_201_CREATED)
async def endpoint_create_email_draft(request: CreateEmailDraftRequest):
    """
    FastAPI endpoint to create an email draft in Gmail.
    Prompts the console for approval before execution.
    """
    payload = request.model_dump()
    approved = await ask_approval("create_email_draft", payload)
    
    if not approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action rejected: approval denied."
        )
        
    try:
        # Load credentials (will trigger local server OAuth if token.json is missing)
        creds = get_credentials()
        result = create_email_draft(request.to, request.subject, request.body, creds)
        return {
            "status": "success",
            "message": "Gmail draft successfully created.",
            "details": {
                "draftId": result.get("id"),
                "message": result.get("message")
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google API Error: {str(e)}"
        )

if __name__ == "__main__":
    # Get port from environment (Railway standardizes on using PORT env var)
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Google MCP Server on port {port}...")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
