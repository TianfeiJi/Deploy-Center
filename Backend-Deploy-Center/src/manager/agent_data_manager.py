import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class AgentDataManager:
    _instance = None
    _data_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "agent_data.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentDataManager, cls).__new__(cls)
        return cls._instance

    def _load_agents(self) -> List[Dict]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_agents(self, agents: List[Dict]):
        with open(self._data_file_path, "w", encoding="utf-8") as file:
            json.dump(agents, file, indent=4, ensure_ascii=False)
         
    def create_agent(self, agent_data: Dict) -> Dict:
        agents = self._load_agents()
        new_id = 1 if not agents else max(agent.id for agent in agents) + 1
        now = datetime.now().isoformat()
        new_agent = {
            "id": new_id,
            "name": agent_data.get("name"),
            "ip": agent_data.get("ip"),
            "port": agent_data.get("port"),
            "service_url": agent_data.get("service_url"),
            "created_at": now,
            "updated_at": None
        }
        agents.append(new_agent)
        self._save_agents(agents)

    def get_agent(self, agent_id: int) -> Optional[Dict]:
        agents = self._load_agents()
        for agent in agents:
            if agent["id"] == agent_id:
                return agent
        return None

    def update_agent(self, agent_id: int, updated_data: dict):
        agents = self._load_agents()
        for agent in agents:
            if agent["id"] == agent_id:
                agent.update(updated_data)
                agent["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_agents(agents)
                return
        raise ValueError(f"Agent with ID {agent_id} not found.")

    def delete_agent(self, agent_id: int):
        agents = self._load_agents()
        agents = [agent for agent in agents if agent["id"] != agent_id]
        self._save_agents(agents)

    def list_agents(self) -> List[Dict]:
        return self._load_agents()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance