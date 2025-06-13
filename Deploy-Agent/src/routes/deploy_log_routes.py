from datetime import datetime
import os
from fastapi import APIRouter
from models.entity.log import Log
from models.common.http_result import HttpResult


deploy_log_router = APIRouter()


# 获取所有日志文件
@deploy_log_router.get("/api/deploy-agent/deploy-log/list", summary="获取日志列表", description="返回所有日志文件的详细信息。")
async def get_deploy_log_list():
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在文件夹
    current_folder = os.path.dirname(current_file_path)
    # 获取父级文件夹
    parent_directory = os.path.dirname(current_folder)
    # 获取父级的父级文件夹
    parent_parent_directory = os.path.dirname(parent_directory)
    # 日志文件所在文件夹
    log_directory = os.path.join(parent_parent_directory, "logs")

    if not os.path.exists(log_directory):
        return HttpResult(code=404, status="failed", msg="日志目录不存在", data=None)
    
    log_objects = []
    for log_file in os.listdir(log_directory):
        # print(log_file)
        file_path = os.path.join(log_directory, log_file)
        # 检查是否为文件且扩展名为 .log
        if os.path.isfile(file_path) and log_file.endswith(".log"):
            try:
                # 获取文件大小
                filesize = os.path.getsize(file_path)
                # 获取文件的创建时间和修改时间
                created_at = datetime.fromtimestamp(os.path.getctime(file_path))
                updated_at = datetime.fromtimestamp(os.path.getmtime(file_path))
                # 获取文件的行数
                with open(file_path, "r", encoding="utf-8") as f:
                    line_count = sum(1 for line in f)  # 计算文件的行数
                # 创建 Log 对象
                log = Log(
                    filename=log_file,
                    filesize=filesize,
                    line_count=line_count,
                    created_at=created_at,
                    updated_at=updated_at
                )
                log_objects.append(log)
            except Exception as e:
                return HttpResult(code=500, status="error", msg=f"处理日志文件 {log_file} 时出错: {e}", data=None)
    return HttpResult(code=200, status="success", msg=None, data=log_objects)

# 获取指定日志文件的内容
@deploy_log_router.get("/api/deploy-agent/deploy-log/{filename}", summary="获取指定日志内容", description="根据日志文件名返回对应日志文件的内容。")
async def get_deploy_log_content(filename: str):
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在文件夹
    current_folder = os.path.dirname(current_file_path)
    # 获取父级文件夹
    parent_directory = os.path.dirname(current_folder)
    # 获取父级的父级文件夹
    parent_parent_directory = os.path.dirname(parent_directory)
    # 日志文件所在文件夹
    log_directory = os.path.join(parent_parent_directory, "logs")
    # 日志文件所在路径
    log_file_path = os.path.join(log_directory, filename)

    if not os.path.exists(log_file_path):
        return HttpResult(code=404, status="success", msg=f"Log file {filename} not found.", data=None)

    try:
        with open(log_file_path, "r", encoding="utf-8") as file:
            log_content = file.read()
        return HttpResult(code=200, status="success", msg=None, data=log_content)
    except Exception as e:
        return HttpResult(code=500, status="failed", msg=f"Failed to read log file: {str(e)}", data=None)