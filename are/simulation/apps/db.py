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
    A basic database application that manages user entries with contact information.
    This app provides simple CRUD operations for database entries containing user details.
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
        """
        Gets a specific database entry by entry_id.
        :param entry_id: ID of the database entry to retrieve
        :returns: Database entry details if entry_id exists, otherwise raise KeyError
        """
        if entry_id not in self.data:
            raise KeyError(f"Database entry {entry_id} does not exist.")
        return self.data[entry_id]
    
    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.WRITE)
    def create_db_entry(self, entry: DBEntry) -> str:
        """
        Creates a new database entry.
        :param entry: Database entry object to create
        :returns: entry_id of the newly created database entry
        """
        self.data[entry.entry_id] = entry
        return entry.entry_id

    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.WRITE)
    def update_db_entry(
        self,
        entry_id: str,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
    ) -> str:
        """
        Updates specific fields of a database entry by entry_id.
        :param entry_id: ID of the database entry to update
        :param name: Updated name (optional)
        :param email: Updated email (optional)
        :param phone: Updated phone number (optional)
        :param address: Updated address (optional)
        :param city: Updated city (optional)
        :param state: Updated state (optional)
        :param zip_code: Updated zip code (optional)
        :param country: Updated country (optional)
        :returns: entry_id of the updated database entry if successful, otherwise raise KeyError
        """
        if entry_id not in self.data:
            raise KeyError(f"Database entry {entry_id} does not exist.")
        
        entry = self.data[entry_id]
        
        # Update only provided fields
        if name is not None:
            entry.name = name
        if email is not None:
            entry.email = email
        if phone is not None:
            entry.phone = phone
        if address is not None:
            entry.address = address
        if city is not None:
            entry.city = city
        if state is not None:
            entry.state = state
        if zip_code is not None:
            entry.zip_code = zip_code
        if country is not None:
            entry.country = country
        
        # Update the updated_at timestamp
        entry.updated_at = datetime.now().isoformat()
        
        self.data[entry_id] = entry
        return entry_id

    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.WRITE)
    def delete_db_entry(self, entry_id: str) -> str:
        """
        Deletes a specific database entry by entry_id.
        :param entry_id: ID of the database entry to delete
        :returns: entry_id of the deleted database entry if successful, otherwise raise KeyError
        """
        if entry_id not in self.data:
            raise KeyError(f"Database entry {entry_id} does not exist.")
        del self.data[entry_id]
        return entry_id

    @type_check
    @app_tool()
    @data_tool()
    @event_registered(operation_type=OperationType.READ)
    def get_all_db_entries(self) -> list[DBEntry]:
        """
        Gets all database entries.
        :returns: List of all database entries
        """
        return list(self.data.values())