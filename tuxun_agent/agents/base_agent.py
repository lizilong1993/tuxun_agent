# Base agent class for TuXun Agent  
from abc import ABC, abstractmethod  
from typing import Any, Dict  
  
class BaseAgent(ABC):  
    def __init__(self, name: str, config: Dict[str, Any]):  
        self.name = name  
        self.config = config  
  
    @abstractmethod  
    async def execute(self, task: Dict[str, Any]) -, Any]:  
        pass 
