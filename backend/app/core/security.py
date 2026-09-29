from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)

# Predefined demo accounts for seamless CXO / Auditor role demonstration
DEMO_USERS: Dict[str, Dict[str, Any]] = {
    "executive": {
        "user_id": "usr_exec_01",
        "username": "executive",
        "display_name": "Chief Operating Officer",
        "role": "Executive",
        "allowed_workspaces": ["plant_a", "plant_b", "region_east", "region_west"],
    },
    "auditor": {
        "user_id": "usr_audit_01",
        "username": "auditor",
        "display_name": "Compliance & Security Auditor",
        "role": "Auditor",
        "allowed_workspaces": ["all"],
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> dict:
    if not credentials:
        # Default to executive for smooth CXO demo mode if no token provided
        return DEMO_USERS["executive"]
    
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        return DEMO_USERS["executive"]
    
    # Match user
    for u in DEMO_USERS.values():
        if u["user_id"] == user_id or u["username"] == user_id:
            return u
            
    return {
        "user_id": user_id,
        "username": payload.get("username", "user"),
        "display_name": payload.get("display_name", "Enterprise User"),
        "role": payload.get("role", "Executive"),
        "allowed_workspaces": payload.get("allowed_workspaces", ["plant_a"])
    }

def require_role(required_role: str):
    def role_checker(user: dict = Security(get_current_user)):
        if user.get("role") != required_role and user.get("role") != "Auditor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires '{required_role}' privileges.",
            )
        return user
    return role_checker
