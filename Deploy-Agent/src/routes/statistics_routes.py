from pathlib import Path
from fastapi import APIRouter
import json
import subprocess
from datetime import datetime, timezone
from models.common.http_result import HttpResult
from manager.project_data_manager import ProjectDataManager
from utils.docker_util import run_docker_command


statistics_router = APIRouter()
PROJECT_DATA_MANAGER = ProjectDataManager().get_instance()

@statistics_router.get("/api/deploy-agent/statistics/project-status", summary="聚合统计项目部署状态", description="返回所有项目运行状态统计")
async def get_project_deployment_statistics():
    check_time = datetime.now(timezone.utc).isoformat()

    try:
        all_projects = PROJECT_DATA_MANAGER.list_projects()
        result = run_docker_command(["ps", "-a", "--format", "json"])

        container_lines = result.strip().split("\n")
        container_status_map = {}

        for line in container_lines:
            try:
                container_info = json.loads(line)
                name = container_info.get("Names", "")
                status = container_info.get("Status", "")
                container_status_map[name] = status
            except json.JSONDecodeError:
                continue

        status_summary = {
            "total": len(all_projects),
            "running": 0,
            "exited": 0,
            "restarting": 0,
            "unknown": 0,
            "awaiting_deployment": 0,
        }

        for p in all_projects:
            container_name = p.get("container_name")
            container_path = p.get("container_path")
            project_type = p.get("project_type")
            
            path_obj = Path(container_path)
            if project_type == "web":
                if path_obj.exists() and any(path_obj.iterdir()):
                    status_summary["running"] += 1
            else:
                # 如果该项目未定义 container_name，或者没有匹配到任何现存容器，视为未部署
                if not container_name or not any(container_name in name for name in container_status_map):
                    status_summary["awaiting_deployment"] += 1
                    continue

                # 能匹配到容器名称，进入状态分析
                for name, status in container_status_map.items():
                    if container_name in name:
                        normalized = (status or "").lower()
                        if "up" in normalized:
                            status_summary["running"] += 1
                        elif "exited" in normalized:
                            status_summary["exited"] += 1
                        elif "restarting" in normalized:
                            status_summary["restarting"] += 1
                        break

        return HttpResult(code=200, status="success", msg=None, data={
            **status_summary,
            "check_time": check_time
        })

    except subprocess.CalledProcessError as e:
        return HttpResult(code=500, status="failed", msg=f"Docker command failed: {e}", data=None)
    except Exception as e:
        return HttpResult(code=500, status="failed", msg=str(e), data=None)