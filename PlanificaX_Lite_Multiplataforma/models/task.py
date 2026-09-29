from dataclasses import dataclass, asdict

@dataclass
class Task:
    subject: str
    title: str
    priority: str = "Media"
    completed: bool = False

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Task(data.get("subject",""),data.get("title",""),data.get("priority","Media"),data.get("completed",False))
