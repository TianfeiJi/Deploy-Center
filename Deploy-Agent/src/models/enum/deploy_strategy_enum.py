# models/enum/deploy_strategy_enum.py
from enum import Enum


class DeployStrategyEnum(str, Enum):
    """
    DeployStrategyEnum

    部署策略枚举（Deployment Strategy Enum）

    用于定义系统支持的部署方式，不同策略对应不同的服务替换逻辑。

    分类说明：
        1. 单实例类（Simple）
        2. 双实例切换类（Switch）
        3. 渐进替换类（Progressive）
        4. 流量控制类（Traffic Control）
        5. 验证类（Verification）
    """

    # =========================
    # 一、单实例类（Simple）
    # =========================

    RECREATE = "recreate"
    """
    单实例重建式部署（Recreate Deployment）

    流程：
        停止旧容器 → 删除旧容器 → 构建新镜像 → 启动新容器

    特点：
        - 实现最简单
        - 存在服务中断
        - 无回滚保障（除非保留旧镜像）

    适用场景：
        - 内部工具
        - 对可用性要求不高的系统
    """

    # =========================
    # 二、双实例切换类（Switch）
    # =========================

    BLUE_GREEN = "blue_green"
    """
    蓝绿部署（Blue-Green Deployment）

    流程：
        保留旧版本（Blue）
        启动新版本（Green）
        健康检查通过后切换流量
        最后下线旧版本

    特点：
        - 接近无感更新
        - 支持快速回滚
        - 资源占用较高（双实例）

    适用场景：
        - ToB系统
        - 稳定性要求高的服务
    """

    # =========================
    # 三、渐进替换类（Progressive）
    # =========================

    ROLLING = "rolling"
    """
    滚动部署（Rolling Deployment）

    流程：
        分批替换旧实例为新实例

    示例：
        A A A A → A A A B → A A B B → A B B B → B B B B

    特点：
        - 无停机（理论上）
        - 资源占用低于蓝绿
        - 回滚较慢
        - 错误可能逐步扩散

    适用场景：
        - 多实例服务
        - 有负载均衡的系统
    """

    # =========================
    # 四、流量控制类（Traffic Control）
    # =========================

    CANARY = "canary"
    """
    金丝雀发布（Canary Deployment）

    流程：
        将少量流量（如10%）导入新版本
        观察系统指标（错误率、延迟等）
        逐步扩大流量比例

    特点：
        - 风险最低
        - 可精细控制发布范围
        - 实现复杂（需要流量控制能力）

    适用场景：
        - 高流量系统
        - 需要稳定上线的业务
    """

    AB_TEST = "ab_test"
    """
    A/B 测试部署（A/B Testing Deployment）

    流程：
        不同用户访问不同版本（A / B）
        用于对比实验效果

    特点：
        - 用于产品实验，而非部署安全
        - 可长期共存多个版本

    适用场景：
        - 产品功能实验
        - 数据驱动优化
    """

    # =========================
    # 五、验证类（Verification）
    # =========================

    SHADOW = "shadow"
    """
    影子部署（Shadow Deployment）

    流程：
        用户请求正常走旧系统
        同时复制请求给新系统（不返回结果）

    特点：
        - 对用户完全无影响
        - 用于验证新系统性能和兼容性

    适用场景：
        - 新系统验证
        - 架构迁移前测试
    """

    # =========================
    # 工具方法
    # =========================

    @classmethod
    def list(cls):
        """返回所有部署策略"""
        return [item.value for item in cls]

    @classmethod
    def is_valid(cls, strategy: str) -> bool:
        """校验是否为合法部署策略"""
        return strategy in cls._value2member_map_

    @classmethod
    def default(cls):
        """默认部署策略"""
        return cls.RECREATE.value