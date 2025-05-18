from enum import Enum

class StatusEnum(str, Enum):
    NOT_STARTED = "not_started"   # 初始状态
    IN_PROGRESS = "in_progress"   # 处理中
    COMPLETED = "completed"       # 完成（可能成功或失败）
    SUCCESS = "success"           # 成功
    FAILED = "failed"             # 失败

    @property
    def label(self) -> str:
        labels = {
            self.NOT_STARTED: "未开始",
            self.IN_PROGRESS: "进行中",
            self.COMPLETED: "已完成",
            self.SUCCESS: "成功",
            self.FAILED: "失败",
        }
        return labels[self]

    @property
    def is_terminal(self) -> bool:
        """是否为终态（不会再改变）"""
        return self in {self.COMPLETED, self.SUCCESS, self.FAILED}

    @property
    def is_successful(self) -> bool:
        """是否表示成功"""
        return self == self.SUCCESS
