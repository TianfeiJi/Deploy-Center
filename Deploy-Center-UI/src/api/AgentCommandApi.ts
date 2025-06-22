import type { AxiosProgressEvent } from 'axios';
import { HttpResult } from "src/types/HttpResult";
import { Template } from "src/types/Template";
import { AddWebProjectRequestDto } from 'src/types/dto/AddWebProjectRequestDto';
import { AddJavaProjectRequestDto } from 'src/types/dto/AddJavaProjectRequestDto';
import { UpdateJavaProjectRequestDto } from "src/types/dto/UpdateJavaProjectRequestDto";
import { UpdateWebProjectRequestDto } from "src/types/dto/UpdateWebProjectRequestDto";
import { UpdatePythonProjectRequestDto } from "src/types/dto/UpdatePythonProjectRequestDto";
import { DeployHistoryVo } from "src/types/vo/DeployHistoryVo";
import { callAgentApi } from "./agentApi";


export class AgentCommandApi {
  private agentId: number;

  constructor(agentId: number) {
    this.agentId = agentId;
  }
  
  // ========================== Agent 统计接口 ==========================
  // 获取 Agent 项目状态统计信息
  async fetchProjectStatusStatistics(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/statistics/project-status', 'GET');
    return httpResult.data.data;
  }

  // ========================== Agent Inspect 信息 ==========================
  // 获取 Agent 聚合信息（版本、Docker、主机等）
  async fetchInspectInfo(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/inspect/info', 'GET');
    return httpResult.data.data;
  }

  // 获取 Agent 版本信息
  async fetchAgentVersion(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/inspect/agent-version', 'GET');
    return httpResult.data.data;
  }

  // 获取健康检查状态
  async fetchHealthStatus(): Promise<string> {
    const httpResult: HttpResult<HttpResult<string>> = await callAgentApi(this.agentId, '/api/deploy-agent/health', 'GET');
    return httpResult.data.data;
  }

  // ========================== SystemConfig 管理 ==========================
  // 获取系统配置列表
  async fetchSystemConfigList(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> =  await callAgentApi(this.agentId, '/api/deploy-agent/system-config/list', 'GET');
    return httpResult.data.data;
  }
  
  // 获取系统配置
  async fetchSystemConfig(configKey: string): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> =  await callAgentApi(this.agentId, `/api/deploy-agent/system-config/${configKey}`, 'GET');
    return httpResult.data.data;
  }

  // ========================== Server 管理 ==========================
  // 获取服务器系统信息
  async fetchServerSystemInfo(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/server/system_info', 'GET');
    return httpResult.data.data;
  }

  // 获取服务器CPU使用率
  async fetchServerCpuUsage(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/server/cpu_usage', 'GET');
    return httpResult.data.data;
  }

  // 获取服务器内存信息
  async fetchServerMemoryInfo(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/server/memory_info', 'GET');
    return httpResult.data.data;
  }

  // 获取服务器磁盘信息
  async fetchServerDiskInfo(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/server/disk_info', 'GET');
    return httpResult.data.data;
  }

  // 获取服务器网速信息
  async fetchServerNetworkSpeed(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/server/network_speed', 'GET'
    );
    return httpResult.data.data;
  }

  // ========================== Docker 管理 ==========================
  
  // 获取容器状态
  async fetchDockerContainerStatus(container_name: string): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, `/api/deploy-agent/docker/container-status?container_name=${container_name}`, 'GET');
    return httpResult.data.data;
  }

  // ========================== DeployHistory 管理 ==========================

  // 获取部署历史列表
  async fetchDeployHistoryList(): Promise<DeployHistoryVo[]> {
    const httpResult: HttpResult<HttpResult<DeployHistoryVo[]>> =  await callAgentApi(this.agentId, '/api/deploy-agent/deploy-history/list', 'GET');
    return httpResult.data.data;
  }

  // ========================== DeployLog 管理 ==========================
  // 获取部署日志列表
  async fetchDeployLogList(): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> =  await callAgentApi(this.agentId, '/api/deploy-agent/deploy-log/list', 'GET');
    return httpResult.data.data;
  }

  // 获取部署日志内容
  async fetchDeployLogContent(filename: string): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> =  await callAgentApi(this.agentId, `/api/deploy-agent/deploy-log/${filename}`, 'GET');
    return httpResult.data.data;
  }

  // ========================== 项目部署辅助接口 ==========================
  // 模版渲染
  async renderTemplateContent(projectId: string, templateId: string): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(
      this.agentId,
      encodeURIComponent(`/api/deploy-agent/project/support/render-template-content?project_id=${projectId}&template_id=${templateId}`),
      'GET'
    );
    return httpResult.data.data;
  }

  // ========================== Project 管理 ==========================
  // 获取项目列表
  async fetchProjectList(): Promise<any[]> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/project/list', 'GET');
    return httpResult.data.data;
  }

  // 检查前端项目可及性
  async checkWebProjectAccessibility(url: string): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(
      this.agentId, 
      encodeURIComponent(`/api/deploy-agent/project/check-web-project-accessibility?url=${url}`),
      'GET');
    return httpResult.data.data;
  }

  // 添加 Web 项目
  async addWebProject(addWebProjectRequestDto: AddWebProjectRequestDto): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/project/web/add', 'POST', addWebProjectRequestDto, undefined);
    return httpResult.data.data;
  }

  // 更新 Web 项目
  async updateWebProject(updateWebProjectRequestDto: UpdateWebProjectRequestDto): Promise<any> {
    const httpResult: HttpResult<any> = await callAgentApi(this.agentId, '/api/deploy-agent/project/web/update', 'PUT', updateWebProjectRequestDto, undefined);
    return httpResult.data;
  }

  // 部署 Web 项目
  async deployWebProject(formData: FormData, config?: { onUploadProgress?: (event: AxiosProgressEvent) => void }): Promise<any> {
    const requestConfig = {
      ...config,
    };
    const httpResult: HttpResult<any> = await callAgentApi(this.agentId, '/api/deploy-agent/project/web/deploy', 'POST', undefined, formData, requestConfig);
    return httpResult.data;
  }
  
  // 删除 Web 项目
  async deleteWebProject(id: string): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, `/api/deploy-agent/project/web/delete/${id}`, 'DELETE');
    return httpResult.data.data;
  }

  // 添加 Java 项目
  async addJavaProject(addJavaProjectRequestDto: AddJavaProjectRequestDto): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, '/api/deploy-agent/project/java/add', 'POST', addJavaProjectRequestDto, undefined);
    return httpResult.data.data;
  }

  // 更新 Java 项目
  async updateJavaProject(updateJavaProjectRequestDto: UpdateJavaProjectRequestDto): Promise<any> {
    const httpResult: HttpResult<any> = await callAgentApi(this.agentId, '/api/deploy-agent/project/java/update', 'PUT', updateJavaProjectRequestDto, undefined);
    return httpResult.data;
  }

  // 部署 Java 项目
  async deployJavaProject(formData: FormData, config?: { onUploadProgress?: (event: AxiosProgressEvent) => void }): Promise<any> {
    const requestConfig = {
      ...config,
    };
    const httpResult: HttpResult<any> = await callAgentApi(this.agentId, '/api/deploy-agent/project/java/deploy', 'POST', undefined, formData, requestConfig);
    return httpResult.data;
  }

  // 删除 Java 项目
  async deleteJavaProject(id: string): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, `/api/deploy-agent/project/java/delete/${id}`, 'DELETE');
    return httpResult.data.data;
  }

  // 更新 Python 项目
  async updatePythonProject(updatePythonProjectRequestDto: UpdatePythonProjectRequestDto): Promise<any> {
    const httpResult: HttpResult<any> = await callAgentApi(this.agentId, '/api/deploy-agent/project/python/update', 'PUT', updatePythonProjectRequestDto, undefined);
    return httpResult.data;
  }

  // 部署 Python 项目
  async deployPythonProject(formData: FormData, config?: { onUploadProgress?: (event: AxiosProgressEvent) => void }): Promise<any> {
    const requestConfig = {
      ...config,
    };
    const httpResult: HttpResult<any> = await callAgentApi(this.agentId, '/api/deploy-agent/project/python/deploy', 'POST', undefined, formData, requestConfig);
    return httpResult.data;
  }

  // 删除 Python 项目
  async deletePythonProject(id: string): Promise<any> {
    const httpResult: HttpResult<HttpResult<any>> = await callAgentApi(this.agentId, `/api/deploy-agent/project/python/delete/${id}`, 'DELETE');
    return httpResult.data.data;
  }

  // ========================== Template 管理 ==========================
  // 获取模板列表（可按类型筛选）
  async fetchTemplateList(templateType?: string): Promise<Template[]> {
    const httpResult: HttpResult<HttpResult<Template[]>> = await callAgentApi(
      this.agentId,
      '/api/deploy-agent/template/list',
      'get',
      templateType ? { params: { template_type: templateType } } : undefined
    );
    return httpResult.data.data;
  }

  // 获取单个模板详情
  async fetchTemplate(templateId: string): Promise<Template> {
    const httpResult: HttpResult<HttpResult<Template>> = await callAgentApi(
      this.agentId,
      `/api/deploy-agent/template/${templateId}`,
      'get'
    );
    return httpResult.data.data;
  }

  // 获取模板内容
  async fetchTemplateContent(templateId: string): Promise<string> {
    const httpResult: HttpResult<{ content: string }> = await callAgentApi(
      this.agentId,
      `/api/deploy-agent/template/content/${templateId}`,
      'get'
    );
    return httpResult.data.content;
  }

  // 创建模板
  async createTemplate(templateInfo: Partial<Template> & { content: string }): Promise<Template> {
    const httpResult: HttpResult<Template> = await callAgentApi(
      this.agentId,
      '/api/deploy-agent/template',
      'post',
      { data: templateInfo }
    );
    return httpResult.data;
  }

  // 更新模板
  async updateTemplate(templateId: string, updatedInfo: Partial<Template> & { content?: string }): Promise<Template> {
    const httpResult: HttpResult<Template> = await callAgentApi(
      this.agentId,
      `/api/deploy-agent/template/${templateId}`,
      'put',
      { data: updatedInfo }
    );
    return httpResult.data;
  }

  // 删除模板
  async deleteTemplate(templateId: string): Promise<void> {
    await callAgentApi(
      this.agentId,
      `/api/deploy-agent/template/${templateId}`,
      'delete'
    );
  }

}