from are.simulation.apps.app import App
from are.simulation.tool_utils import OperationType, app_tool, data_tool
from are.simulation.types import event_registered
from are.simulation.utils import get_state_dict, type_check
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any

@dataclass
class DBEntry:
    entry_id: str
    name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    created_at: str
    updated_at: str

@dataclass
class DBApp(App):
    """
    Most basic DB app fr
    """

    name: str | None = "DBApp"
    data: dict[str, DBEntry] = field(default_factory=dict)

    def __post_init__(self):
        super().__init__(self.name)

    # state mgmt for the fake DB
    def get_state(self) -> dict[str, Any]:
        return get_state_dict(self, ["data"])
    
    def load_state(self, state: dict[str, Any]) -> None:
        self.data = {}
        db_data = state.get("data", {})

        for i, entry in db_data.items():
            self.data[i] = DBEntry(
                entry_id=entry.get("entry_id", i),
                name=entry.get("name", ""),
                email=entry.get("email", ""),
                phone=entry.get("phone", ""),
                address=entry.get("address", ""),
                city=entry.get("city", ""),
                state=entry.get("state", ""),
                zip_code=entry.get("zip_code", ""),
                country=entry.get("country", ""),
                created_at=entry.get("created_at", datetime.now().isoformat()),
                updated_at=entry.get("updated_at", datetime.now().isoformat()),
            )
    
    def reset(self) -> None:
        super().reset()
        self.data = {}

    # tools
    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.READ)
    def get_db_entry(self, entry_id: str) -> DBEntry:
        return self.data[entry_id]
    
    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.WRITE)
    def create_db_entry(self, entry: DBEntry) -> str:
        self.data[entry.entry_id] = entry
        return entry.entry_id

    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.WRITE)
    def update_db_entry(self, entry_id: str, entry: DBEntry) -> None:
        self.data[entry_id] = entry
        return entry_id

    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.WRITE)
    def delete_db_entry(self, entry_id: str) -> None:
        del self.data[entry_id]
        return entry_id

    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.READ)
    def get_all_db_entries(self) -> list[DBEntry]:
        return list(self.data.values())