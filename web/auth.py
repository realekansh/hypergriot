from fastapi import Header, HTTPException, status
import os

# Simple token-based header auth for dev dashboards.
# Set WEB_DASH_TOKEN in your .env for access control.
def require_token(x_token: str = Header(...)):
    token = os.getenv("WEB_DASH_TOKEN")
    if not token:
        # if not configured, block access by default
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Dashboard not configured")
    if x_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid X-Token header")
    return True
