from dataclasses import dataclass, field
from datetime import datetime

@dataclass(slots=True)
class Budget:

    budget: int = 0
    pk: int = 0
    added_date: datetime = field(default_factory=datetime.now)