from jinja2 import Template
from manager.project_data_manager import ProjectDataManager
from manager.template_manager import TemplateManager

project_data_manager = ProjectDataManager().get_instance()
template_manager = TemplateManager().get_instance()

def render_template_for_project(project_id: str, template_id: str) -> str:
    project = project_data_manager.get_project(project_id)
    template_content = template_manager.get_template_content(template_id)
    template = Template(template_content)
    return template.render(**project)
