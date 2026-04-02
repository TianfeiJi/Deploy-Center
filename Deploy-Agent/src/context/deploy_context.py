from typing import Optional


class DeployContext:
    """
    DeployContext

    部署上下文对象（Runtime Context）

    用于在各个部署步骤（steps）之间传递运行时数据，
    避免依赖 self.xxx 或函数返回值链式调用。

    设计原则：
        - 只存“过程数据”，不存控制信息
        - 所有字段允许为 None（逐步填充）
        - 不包含业务逻辑，仅作为数据载体
    """

    # ===== 文件相关 =====
    artifact_path: Optional[str] = None
    
    project_root_path: Optional[str] = None
    dockerfile_path: Optional[str] = None

    # ===== Docker相关 =====
    image_name: Optional[str] = None
    image_tag: Optional[str] = None
    container_name: Optional[str] = None

    # ===== 当前执行步骤 =====
    current_step: Optional[str] = None

    def __init__(self):
        self.artifact_path = None
        
        self.project_root_path = None
        self.dockerfile_path = None

        self.image_name = None
        self.image_tag = None
        self.container_name = None

        self.current_step = None