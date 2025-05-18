# security/two_factor_auth.py
import pyotp
import qrcode
import io
import base64


class TwoFactorAuth:
    """用于生成和验证基于时间的一次性验证码（TOTP）的 2FA 工具类。"""

    def __init__(self, issuer_name: str = "Deploy Center"):
        """
        初始化 2FA 工具类。

        Args:
            issuer_name (str): 发行方名称，显示在 Authenticator 应用中。
        """
        self.issuer_name = issuer_name

    def generate_secret_key(self) -> str:
        """
        生成一个新的 base32 秘钥，用于绑定用户的身份验证器。

        Returns:
            str: 新生成的 base32 编码密钥。
        """
        return pyotp.random_base32()

    def get_totp(self, secret_key: str) -> pyotp.TOTP:
        """
        创建一个 TOTP 实例，用于生成和验证验证码。

        Args:
            secret_key (str): 用户的 base32 秘钥。

        Returns:
            pyotp.TOTP: TOTP 对象。
        """
        return pyotp.TOTP(secret_key)

    def generate_provisioning_uri(self, username: str, secret_key: str) -> str:
        """
        生成用于绑定 Authenticator 应用的 URI。

        Args:
            username (str): 用户名，将作为账号标识显示在 Authenticator 中。
            secret_key (str): 用户的 base32 秘钥。

        Returns:
            str: 可用于生成二维码的 URI。
        """
        totp = self.get_totp(secret_key)
        return totp.provisioning_uri(name=username, issuer_name=self.issuer_name)

    def get_qr_code_base64(self, uri: str) -> str:
        """
        将 URI 转换为二维码并返回 base64 编码字符串，便于前端展示。

        Args:
            uri (str): 用于绑定的 provisioning URI。

        Returns:
            str: base64 编码的 PNG 图片
        """
        qr_img = qrcode.make(uri)
        buffered = io.BytesIO()
        qr_img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{base64_str}"

    def get_current_code(self, secret_key: str) -> str:
        """
        获取当前时间窗口下的动态验证码（TOTP），仅用于调试或测试。

        Args:
            secret_key (str): 用户的 base32 密钥。

        Returns:
            str: 当前验证码（通常为 6 位）。
        """
        return self.get_totp(secret_key).now()

    def verify_code(self, secret_key: str, code: str, valid_window: int = 0) -> bool:
        """
        验证用户输入的 TOTP 验证码是否正确。

        Args:
            secret_key (str): 用户的 base32 密钥。
            code (str): 用户输入的 6 位验证码。
            valid_window (int, optional): 容忍的时间窗口数（单位：30 秒）。默认为 0，表示只验证当前时间窗口。
                                           设为 1 时，允许前后偏移一个时间窗口（共 90 秒）。

        Returns:
            bool: 验证是否通过。
        """
        try:
            totp = self.get_totp(secret_key)
            return totp.verify(otp=code, valid_window=valid_window)
        except Exception:
            return False
