from datetime import datetime
from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.contacts import ContactsApp, Contact, Gender, Status
from are.simulation.apps.db import DBApp, DBEntry
from are.simulation.apps.email_client import EmailClientV2, EmailFolderName
from are.simulation.apps.messaging_v2 import MessagingAppV2, MessagingAppMode
from are.simulation.apps.calendar import CalendarApp
from are.simulation.apps.shopping import ShoppingApp
from are.simulation.apps.reminder import ReminderApp
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss11")
class ss11(Scenario):
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

        # Populate distractor apps with unrelated data
        contacts.add_contact(Contact(first_name="John", last_name="Doe", email="john@example.com", phone="1234567890", gender=Gender.MALE, status=Status.EMPLOYED))
        db.create_db_entry(DBEntry(entry_id="1", name="Jane Doe", email="jane@example.com", phone="0987654321", address="123 Main St", city="Anytown", state="CA", zip_code="12345", country="USA", created_at=datetime.now().isoformat(), updated_at=datetime.now().isoformat()))
        # Add messaging users and some messages to create similarity with EmailClientApp (high similarity)
        messaging.add_users(["Alice", "Bob"])
        calendar.add_calendar_event(title="Meeting", start_datetime="2024-01-15 10:00:00", end_datetime="2024-01-15 11:00:00")
        reminder.add_reminder(title="Buy groceries", due_datetime="2024-01-20 18:00:00", description="Remember to buy groceries")

        self.apps = [contacts, db, email, messaging, calendar, shopping, reminder, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        email = self.get_typed_app(EmailClientV2)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please send an email to recipient@example.com with subject 'Meeting Request' and content 'Can we schedule a meeting?'",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                email.send_email(
                    recipients=["recipient@example.com"],
                    subject="Meeting Request",
                    content="Can we schedule a meeting?",
                )
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss11())

