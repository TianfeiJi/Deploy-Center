from fastapi import APIRouter
from utils.jwt_util import JWTUtil
from utils.decorators.skip_auth import skip_auth
from models.entity.user import User
from models.dto.user_login_request_dto import UserLoginRequestDto
from models.common.http_result import HttpResult
from models.entity.system_config import SystemConfig
from manager import SYSTEM_CONFIG_DATA_MANAGER, USER_DATA_MANAGER
from security.two_factor_auth import TwoFactorAuth


# 路由
auth_router = APIRouter()

# TODO：考虑登录成功后 缓存登录用户到cached_data.json
@skip_auth
@auth_router.post("/api/deploy-center/auth/login")
async def login(dto: UserLoginRequestDto):
    username = dto.identifier
    password = dto.credential
    two_factor_code = dto.two_factor_code

    user: User = USER_DATA_MANAGER.get_user_by_username(username)
    if not user:
        return HttpResult[None](code=400, status="failed", msg="用户不存在", data=None)
    if password != user.password:
        return HttpResult[None](code=400, status="failed", msg="密码错误", data=None)
    if user.status != "ENABLED":
        return HttpResult[None](code=400, status="failed", msg="用户已被禁用", data=None)
    
    # 检查是否开启 2FA
    enable_2fa_config: SystemConfig = SYSTEM_CONFIG_DATA_MANAGER.get_config("enable_2fa")
    is_2fa_enabled = enable_2fa_config and str(enable_2fa_config.config_value).lower() == "true"

    if is_2fa_enabled:
        if not user.two_factor_secret:
            return HttpResult[None](code=400, status="failed", msg="该用户未绑定双因素认证", data=None)

        if not two_factor_code:
            return HttpResult[None](code=400, status="failed", msg="请输入双因素验证码", data=None)

        tfa = TwoFactorAuth()
        if not tfa.verify_code(user.two_factor_secret, two_factor_code, valid_window=1):
            return HttpResult[None](code=400, status="failed", msg="双因素验证码错误", data=None)
        
    # 密码校验和2FA都通过 -> 生成token
    token = JWTUtil.generate_token(user.id, username)
    result_dict = {
        "user_id": user.id,
        "token": token
    }
    return HttpResult[dict](code=200, status="success", msg="登录成功", data=result_dict)


@skip_auth
@auth_router.post("/api/deploy-center/auth/logout")
async def logout():
    # TODO: 考虑加一些别的逻辑
    return HttpResult[None](code=200, status="success", msg="退出登录成功", data=None)