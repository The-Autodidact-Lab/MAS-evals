from datetime import datetime
from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.contacts import ContactsApp, Contact, Gender, Status
from are.simulation.apps.db import DBApp, DBEntry
from are.simulation.apps.email_client import Email, EmailClientV2, EmailFolderName
from are.simulation.apps.messaging_v2 import MessagingAppV2, MessagingAppMode
from are.simulation.apps.calendar import CalendarApp
from are.simulation.apps.shopping import ShoppingApp
from are.simulation.apps.reminder import ReminderApp
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss7")
class ss7(Scenario):
    target_id: str | None = None

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize all 7 apps
        agui = AgentUserInterface()
        contacts = ContactsApp()
        db = DBApp()
        email = EmailClientV2()
        messaging = MessagingAppV2(current_user_id="user1", current_user_name="User", mode=MessagingAppMode.NAME)
        calendar = CalendarApp()
        shopping = ShoppingApp()
        reminder = ReminderApp()
        
        # Populate DBApp with entries (target app) - high similarity with ContactsApp
        db.create_db_entry(DBEntry(
            entry_id="1",
            name="John Doe",
            email="john.doe@example.com",
            phone="1234567890",
            address="123 Main St, Anytown, USA",
            city="Anytown",
            state="CA",
            zip_code="12345",
            country="USA",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        ))

        self.target_id = db.create_db_entry(DBEntry(
            entry_id="2",
            name="Jane Doe",
            email="jane.doe@example.com",
            phone="0987654321",
            address="456 Oak Ave, Anytown, USA",
            city="Anytown",
            state="CA",
            zip_code="12345",
            country="USA",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        ))

        db.create_db_entry(DBEntry(
            entry_id="3",
            name="Jim Doe",
            email="jim.doe@example.com",
            phone="1112223333",
            address="789 Pine St, Anytown, USA",
            city="Anytown",
            state="CA",
            zip_code="12345",
            country="USA",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        ))

        # Populate ContactsApp with similar contact-like data (high similarity distractor)
        contacts.add_contact(Contact(
            contact_id="1",
            first_name="Sarah",
            last_name="Johnson",
            email="sarah@example.com",
            phone="5551234567",
            gender=Gender.FEMALE,
            status=Status.EMPLOYED,
        ))

        # Populate distractor apps
        email.add_email(Email(sender="sender@example.com", recipients=["user@meta.com"], subject="Test", content="Test email"), EmailFolderName.INBOX)
        messaging.add_users(["Alice"])
        calendar.add_calendar_event(title="Meeting", start_datetime="2024-01-15 10:00:00", end_datetime="2024-01-15 11:00:00")
        reminder.add_reminder(title="Buy groceries", due_datetime="2024-01-20 18:00:00", description="Remember to buy groceries")

        self.apps = [contacts, db, email, messaging, calendar, shopping, reminder, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        db = self.get_typed_app(DBApp)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please get the database entry for Jane Doe",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                db.get_db_entry(self.target_id)
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        agent_events = [
            event for event in env.event_log.list_view() if event.event_type == EventType.AGENT
        ]

        # ensure that agent called the get_db_entry tool
        try:
            target_event = next(event for event in agent_events if event.action.function_name == "get_db_entry" and event.action.args["entry_id"] == self.target_id)
        except StopIteration:
            return ScenarioValidationResult(success=False, exception=Exception("Target event not found"))
        
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss7())

