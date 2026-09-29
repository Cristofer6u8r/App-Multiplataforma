import json
from pathlib import Path
from models.task import Task

class TaskRepository:
    """Encapsula la persistencia local de PlanificaX Lite."""
    def __init__(self,file_path="data/tasks.json"):
        self.file_path=Path(file_path); self.file_path.parent.mkdir(parents=True,exist_ok=True)
    def load(self):
        if not self.file_path.exists(): return []
        try:
            data=json.loads(self.file_path.read_text(encoding="utf-8")); return [Task.from_dict(x) for x in data]
        except (json.JSONDecodeError,OSError): return []
    def save(self,tasks):
        self.file_path.write_text(json.dumps([t.to_dict() for t in tasks],ensure_ascii=False,indent=2),encoding="utf-8")
