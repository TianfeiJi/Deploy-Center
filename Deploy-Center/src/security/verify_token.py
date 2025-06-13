from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.jwt_util import JWTUtil

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    验证 JWT Token，并返回用户信息。

    Args:
        token (str): JWT Token。

    Returns:
        User: 用户，如果 Token 无效或已过期，返回 None。
    """
    user_info: dict = JWTUtil.get_user_from_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_info