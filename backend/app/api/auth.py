from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.security import DEMO_USERS, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str

@router.post("/login")
def login(req: LoginRequest):
    username = req.username.lower()
    user = DEMO_USERS.get(username)
    if not user:
        # Default fallback to executive for easy demonstration
        user = DEMO_USERS["executive"]
        
    token = create_access_token(data={
        "sub": user["user_id"],
        "username": user["username"],
        "display_name": user["display_name"],
        "role": user["role"],
        "allowed_workspaces": user["allowed_workspaces"]
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/demo-users")
def get_demo_users():
    return list(DEMO_USERS.values())
