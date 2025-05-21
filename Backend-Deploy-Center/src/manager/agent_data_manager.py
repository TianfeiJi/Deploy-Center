import json
import os
from typing import List, Optional
from datetime import datetime
from models.entity.agent import Agent


class AgentDataManager:
    _instance = None
    _data_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "agent_data.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentDataManager, cls).__new__(cls)
        return cls._instance

    def _load_agents(self) -> List[Agent]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                return [Agent(**item) for item in raw_data]
        except FileNotFoundError:
            return []

    def _save_agents(self, agents: List[Agent]):
        with open(self._data_file_path, "w", encoding="utf-8") as file:
            json.dump([agent.model_dump() for agent in agents], file, indent=4, ensure_ascii=False)

    def create_agent(self, agent_data: dict) -> Agent:
        agents = self._load_agents()
        new_id = 1 if not agents else max(agent.id for agent in agents) + 1
        now = datetime.now().isoformat()
        agent = Agent(
            id=new_id,
            name=agent_data.get("name"),
            ip=agent_data.get("ip"),
            port=agent_data.get("port"),
            service_url=agent_data.get("service_url"),
            os=agent_data.get("os"),
            type=agent_data.get("type"),
            status="online",
            created_at=now,
            updated_at=now
        )
        agents.append(agent)
        self._save_agents(agents)
        return agent

    def get_agent(self, agent_id: int) -> Optional[Agent]:
        agents = self._load_agents()
        for agent in agents:
            if agent.id == agent_id:
                return agent
        return None

    def update_agent(self, agent_id: int, updated_data: dict):
        agents = self._load_agents()
        for agent in agents:
            if agent.id == agent_id:
                if "name" in updated_data:
                    agent.name = updated_data["name"]
                if "ip" in updated_data:
                    agent.ip = updated_data["ip"]
                if "port" in updated_data:
                    agent.port = updated_data["port"]
                if "os" in updated_data:
                    agent.os = updated_data["os"]
                if "type" in updated_data:
                    agent.type = updated_data["type"]
                if "status" in updated_data:
                    agent.status = updated_data["status"]
                agent.updated_at = datetime.now().isoformat()
                self._save_agents(agents)
                return
        raise ValueError(f"Agent with ID {agent_id} not found.")

    def delete_agent(self, agent_id: int):
        agents = self._load_agents()
        agents = [agent for agent in agents if agent.id != agent_id]
        self._save_agents(agents)

    def list_agents(self) -> List[Agent]:
        return self._load_agents()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance