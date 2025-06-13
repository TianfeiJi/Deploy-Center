import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class ProjectDataManager:
    _instance = None
    _data_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "project_data.json")

    def __new__(cls):
        """
        确保只创建一个实例。
        """
        if cls._instance is None:
            cls._instance = super(ProjectDataManager, cls).__new__(cls)
        return cls._instance

    def _load_projects(self) -> List[Dict]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        
    def _save_projects(self, projects: List[Dict]):
        with open(self._data_file_path, "w", encoding="utf-8") as file:
            json.dump(projects, file, indent=4, ensure_ascii=False)
            
    def create_project(self, project: Dict):
        projects = self._load_projects()
        projects.append(project)
        self._save_projects(projects)

    def get_project(self, project_id: str) -> Optional[Dict]:
        projects = self._load_projects()
        for project in projects:
            if project["id"] == project_id:
                return project
        return None

    def update_project(self, project_id: str, updated_data: Dict):
        projects = self._load_projects()
        for project in projects:
            if project["id"] == project_id:
                project.update(updated_data)
                project["updated_at"] = datetime.now().isoformat()
                self._save_projects(projects)
                return
        raise ValueError(f"Project with ID {project_id} not found.")

    def delete_project(self, project_id: str):
        projects = self._load_projects()
        projects = [project for project in projects if project["id"] != project_id]
        self._save_projects(projects)

    def list_projects(self) -> List[Dict]:
        return self._load_projects()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance