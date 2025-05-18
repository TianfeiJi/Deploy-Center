import os
import json
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

class TemplateManager:
    _instance = None
    _data_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "template_data.json")
    _template_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "template")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TemplateManager, cls).__new__(cls)
        return cls._instance

    def _load_templates(self) -> List[Dict]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_templates(self, templates: List[Dict]):
        with open(self._data_file_path, "w", encoding="utf-8") as file:
            json.dump(templates, file, indent=4, ensure_ascii=False)

    def create_template(self, template_data: Dict) -> Dict:
        templates = self._load_templates()
        now = datetime.now().isoformat()

        template_path = os.path.join(self._template_folder_path, template_data["relative_path"])
        Path(template_path).parent.mkdir(parents=True, exist_ok=True)
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_data["content"])

        template = {
            "id": str(uuid.uuid4()).replace("-", "")[:8],
            "template_name": template_data.get("template_name"),
            "relative_path": template_data.get("relative_path"),
            "template_type": template_data.get("template_type"),
            "project_type": template_data.get("project_type"),
            "description": template_data.get("description", ""),
            "created_at": now,
            "updated_at": now
        }
        templates.append(template)
        self._save_templates(templates)
        return template

    def get_template(self, template_id: str) -> Optional[Dict]:
        templates = self._load_templates()
        for tpl in templates:
            if tpl["id"] == template_id:
                return tpl
        return None

    def update_template(self, template_id: str, updated_data: Dict):
        templates = self._load_templates()
        for tpl in templates:
            if tpl["id"] == template_id:
                if "content" in updated_data:
                    file_path = os.path.join(self._template_folder_path, tpl["relative_path"])
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(updated_data["content"])
                if "description" in updated_data:
                    tpl["description"] = updated_data["description"]
                tpl["updated_at"] = datetime.now().isoformat()
                self._save_templates(templates)
                return
        raise ValueError(f"Template with ID {template_id} not found.")

    def delete_template(self, template_id: str):
        templates = self._load_templates()
        target_tpl = None
        for tpl in templates:
            if tpl["id"] == template_id:
                target_tpl = tpl
                break

        if target_tpl:
            file_path = os.path.join(self._template_folder_path, target_tpl["relative_path"])
            if os.path.exists(file_path):
                os.remove(file_path)
            templates = [tpl for tpl in templates if tpl["id"] != template_id]
            self._save_templates(templates)
        else:
            raise ValueError(f"Template with ID {template_id} not found.")

    def list_templates(self) -> List[Dict]:
        return self._load_templates()

    def get_template_content(self, template_id: str) -> str:
        tpl = self.get_template(template_id)
        if not tpl:
            raise ValueError(f"Template with ID {template_id} not found.")
        file_path = os.path.join(self._template_folder_path, tpl["relative_path"])
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
