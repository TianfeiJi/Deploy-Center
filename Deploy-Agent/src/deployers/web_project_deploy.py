import os
import uuid
import zipfile
import shutil
from datetime import datetime
from fastapi import UploadFile
from loguru import logger
from models.common.http_result import HttpResult
from models.enum.status_enum import StatusEnum
from manager import PROJECT_DATA_MANAGER, DEPLOY_HISTORY_DATA_MANAGER
from utils.user_context import get_current_user


class WebProjectDeployer:
    def __init__(self):
        """
        初始化前端项目部署器。

        该类用于处理前端项目的部署流程，包括解压上传的 ZIP 文件、验证项目结构、部署到指定路径等。
        """
        self.web_project = None
        
    def deploy(self, id: str, zip_file: UploadFile):
        """部署前端项目"""
        logger.info("==================== Web Project Deploy : Start ====================")
        user = get_current_user()
        safe_user_info = {
            "id": user.get("id"),
            "username": user.get("username"),
            "nickname": user.get("nickname")
        }
        logger.info(f"当前用户（简要）：{safe_user_info}")
        
        self.deploy_status = StatusEnum.START
        self.web_project = PROJECT_DATA_MANAGER.get_project(id)
        if (self.web_project is None):
            return HttpResult[None](code=400, status="failed", msg=f"没有id为{id}的Web项目", data=None)
        
        logger.info(f"开始部署项目：{self.web_project}")
        # 生成部署历史id
        self.deploy_history_id = str(uuid.uuid4()).replace("-", "")[:8]

        self._create_project_directory()
        zip_path = self._save_zip_file(zip_file)
        self._extract_zip_file(zip_path)
        self._delete_zip_file(zip_path)
        self._update_web_project_data(id)
        logger.info("==================== Web Project Deploy : Finish ====================")
        success_msg = (
            f"{self.web_project.get('project_name')} 项目部署成功"
        )
        return HttpResult[None](code=200, status="success", msg=success_msg, data=None)
    
    def _create_project_directory(self):
        """创建项目目录"""
        logger.info(f"1 - Start - 创建项目目录")
        try:
            # 在容器内创建文件夹
            os.makedirs(self.web_project.get('container_project_path'), exist_ok=True)
            logger.info(f"1 - Success - 项目目录已创建: {self.web_project.get('container_project_path')}")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"1 - Failed - 创建项目目录失败: {e}"
            logger.error(err_msg)
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, "failed", err_msg, self.user)
            raise

    def _save_zip_file(self, zip_file: UploadFile) -> str:
        """保存上传的 zip 文件"""
        logger.info(f"2 - Start - 保存 ZIP 文件")
        zip_path = os.path.join(self.web_project.get('container_project_path'), f"{self.web_project.get('project_code')}.zip")
        try:
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(zip_file.file, buffer)
            logger.debug(f"2 - Success - ZIP 文件已保存到: {zip_path}")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"2 - Failed - 保存 ZIP 文件失败: {e}"
            logger.error(err_msg)
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, "failed", err_msg, self.user)
            raise
        return zip_path
        
    def _extract_zip_file(self, zip_path: str):
        """解压上传的 zip 文件"""
        logger.info(f"3 - Start - 解压 ZIP 文件")
        extract_path = self.web_project.get('container_project_path')  # 解压到已创建的当前前端项目文件夹
        
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # 解压文件到指定目录
                zip_ref.extractall(extract_path)
            
            logger.debug(f"3 - Success - ZIP 文件已解压到: {extract_path}")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"3 - Failed - 解压 ZIP 文件失败: {e}"
            logger.error(err_msg)
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, "failed", err_msg, self.user, self.user)
            raise

    def _delete_zip_file(self, zip_path: str):
        """删除 ZIP 文件"""
        logger.info(f"4 - Start - 删除 ZIP 文件")
        try:
            os.remove(zip_path)
            logger.debug(f"4 - Success - 删除临时 ZIP 文件: {zip_path}")
        except Exception as e:
            logger.error(f"4 - Failed - 删除 ZIP 文件失败: {e}")
            self.deploy_status = StatusEnum.FAILED
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, self.deploy_status, None, self.user)
            raise

    def _update_web_project_data(self, id: str):
        """
        5 - 更新项目部署时间和部署记录

        更新部署成功后的项目部署时间和部署记录数据。
        """
        logger.info(f"5 - Start - 更新部署时间")
        updated_data = {
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        # 更新项目可能失败，但是至此，项目更新操作是成功了的
        self.deploy_status = StatusEnum.SUCCESS
        try:
            PROJECT_DATA_MANAGER.update_project(id, updated_data)
            logger.info(f"5 - Success - 更新部署时间成功")
        except Exception as e:
            logger.error(f"5 - Failed - 更新部署时间失败: {e}")
            raise
        
        try:
            logger.info("6. - START - 更新部署记录数据")
            self.deploy_status = StatusEnum.SUCCESS
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, self.deploy_status, None, self.user)
            logger.info("6. - FINISH - 部署记录数据更新成功")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"6 - ERROR - 部署记录数据更新失败: {e}"
            logger.error(err_msg)
        