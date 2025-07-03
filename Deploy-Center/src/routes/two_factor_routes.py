# routes/two_factor_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.entity.user import User
from security.two_factor_auth import TwoFactorAuth
from models.common.http_result import HttpResult
from manager import USER_DATA_MANAGER
from config.log_config import get_logger
from utils.decorators.skip_auth import skip_auth


logger = get_logger()

two_factor_router = APIRouter(prefix="/api/deploy-center/2fa", tags=["Two Factor Auth"])

tfa = TwoFactorAuth()

@skip_auth
@two_factor_router.get("/setup/{username}", response_model=HttpResult)
def setup_2fa(username: str):
    """
    生成用户的 TOTP 密钥并返回二维码 Base64 图片（仅注册时调用一次）
    """
    user: User = USER_DATA_MANAGER.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if (not user.two_factor_secret):
        secret = tfa.generate_secret_key()
        uri = tfa.generate_provisioning_uri(username=username, secret_key=secret)
        qr_base64 = tfa.get_qr_code_base64(uri)
        updated_data = {
            "two_factor_secret": secret
        }
        USER_DATA_MANAGER.update_user(user.id, updated_data)
    else:
        # 已经绑定过 2FA 的情况，可以根据业务处理方式选择：
        # 方式一：返回已存在的二维码（用于前端展示）
        # uri = tfa.generate_provisioning_uri(username=username, secret_key=user.two_factor_secret)
        # qr_base64 = tfa.get_qr_code_base64(uri)

        #  可选方式二：抛出异常阻止重复绑定
        # raise HTTPException(status_code=400, detail="2FA already setup")

        #  可选方式三：允许重新生成（解绑旧的绑定）
        # 新建 secret，更新数据库，并返回新的二维码
        secret = tfa.generate_secret_key()
        uri = tfa.generate_provisioning_uri(username=username, secret_key=secret)
        qr_base64 = tfa.get_qr_code_base64(uri)
        updated_data = {
            "two_factor_secret": secret
        }
        USER_DATA_MANAGER.update_user(user.id, updated_data)

    return HttpResult[dict](code=200, status="success", msg=None, data={"secret": secret, "qr_code_base64": qr_base64})


class Verify2FARequestDto(BaseModel):
    username: str
    code: str


@skip_auth
@two_factor_router.post("/verify", response_model=HttpResult)
def verify_2fa(dto: Verify2FARequestDto):
    """
    验证用户输入的验证码是否正确
    """
    user: User = USER_DATA_MANAGER.get_user_by_username(dto.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    secret = user.two_factor_secret
    is_verified = tfa.verify_code(secret, dto.code, valid_window=1)
    return HttpResult[bool](code=200, status="success", msg=None, data=bool(is_verified))


@skip_auth
@two_factor_router.get("/status/{username}")
def get_2fa_status(username: str) -> HttpResult[bool]:
    """
    查询用户是否已绑定 2FA（是否已有 two_factor_secret）
    """
    user = USER_DATA_MANAGER.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return HttpResult[bool](code=200, status="success", msg=None, data=bool(user.two_factor_secret))
