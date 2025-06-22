from models.entity.deploy_history import DeployHistory


class DeployHistoryVo(DeployHistory):
    project_code: str
    project_name: str