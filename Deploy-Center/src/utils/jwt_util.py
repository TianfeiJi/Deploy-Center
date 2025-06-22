import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from manager.system_config_data_manager import SystemConfigManager
SYSTEM_CONFIG_MANAGER = SystemConfigManager.get_instance()

raw_config = SYSTEM_CONFIG_MANAGER.get_config("token_expiration_hours")
if raw_config is None:
    token_expiration_hours = 24
else:
    token_expiration_hours = int(raw_config.config_value)

# JWT 配置
JWT_SECRET = "9f86d081884c7d659a2feaa0c55ad0f17a2c01997a033b48d1f4b42d69f2475b"  # 密钥
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(hours=token_expiration_hours)  # Token 有效期

class JWTUtil:
    @staticmethod
    def generate_token(user_id: int, username: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        生成 JWT Token。

        Args:
            user_id (int): 用户 ID。
            username (str): 用户名。
            expires_delta (Optional[timedelta]): Token 有效期，默认为 JWT_EXPIRATION_DELTA。

        Returns:
            str: 生成的 JWT Token。
        """
        if expires_delta is None:
            expires_delta = JWT_EXPIRATION_DELTA
        expire = datetime.now(timezone.utc) + expires_delta

        payload = {
            "user_id": user_id,
            "username": username,
            "exp": expire
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        解码并验证 JWT Token。

        Args:
            token (str): JWT Token。

        Returns:
            Optional[Dict]: 解码后的用户信息，如果 Token 无效或已过期，返回 None。
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
        except jwt.InvalidTokenError:
            print("Invalid token.")
        except Exception as e:
            print(f"Error decoding token: {e}")
        return None

    @staticmethod
    def get_user_from_token(token: str) -> Optional[Dict]:
        """
        从 JWT Token 中提取用户信息。

        Args:
            token (str): JWT Token。

        Returns:
            Optional[Dict]: 用户信息，如果 Token 无效或已过期，返回 None。
        """
        payload = JWTUtil.decode_token(token)
        if payload:
            return {
                "user_id": payload.get("user_id"),
                "username": payload.get("username")
            }
        return None