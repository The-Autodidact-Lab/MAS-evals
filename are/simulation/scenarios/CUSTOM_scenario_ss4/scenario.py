from datetime import datetime, timezone
from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.contacts import ContactsApp, Contact, Gender, Status
from are.simulation.apps.db import DBApp, DBEntry
from are.simulation.apps.email_client import Email, EmailClientV2, EmailFolderName
from are.simulation.apps.messaging_v2 import MessagingAppV2, MessagingAppMode
from are.simulation.apps.calendar import CalendarApp
from are.simulation.apps.shopping import CartItem, Order, ShoppingApp
from are.simulation.apps.reminder import ReminderApp
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss4")
class ss4(Scenario):
    target_order_id: str | None = None

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
        
        # Populate ShoppingApp with orders (target app)
        order1 = Order(
            order_id="order1",
            order_status="processed",
            order_date=datetime.now(timezone.utc),
            order_total=50.0,
            order_items={"item1": CartItem(item_id="item1", quantity=2, price=25.0)},
        )
        shopping.orders["order1"] = order1

        self.target_order_id = "order2"
        target_order = Order(
            order_id=self.target_order_id,
            order_status="shipped",
            order_date=datetime.now(timezone.utc),
            order_total=100.0,
            order_items={"item2": CartItem(item_id="item2", quantity=1, price=100.0)},
        )
        shopping.orders[self.target_order_id] = target_order

        order3 = Order(
            order_id="order3",
            order_status="delivered",
            order_date=datetime.now(timezone.utc),
            order_total=75.0,
            order_items={"item3": CartItem(item_id="item3", quantity=3, price=25.0)},
        )
        shopping.orders["order3"] = order3

        # Populate distractor apps with unrelated data
        contacts.add_contact(Contact(first_name="John", last_name="Doe", email="john@example.com", phone="1234567890", gender=Gender.MALE, status=Status.EMPLOYED))
        db.create_db_entry(DBEntry(entry_id="1", name="Jane Doe", email="jane@example.com", phone="0987654321", address="123 Main St", city="Anytown", state="CA", zip_code="12345", country="USA", created_at=datetime.now().isoformat(), updated_at=datetime.now().isoformat()))
        email.add_email(Email(sender="sender@example.com", recipients=["user@meta.com"], subject="Test", content="Test email"), EmailFolderName.INBOX)
        messaging.add_users(["Alice"])
        calendar.add_calendar_event(title="Meeting", start_datetime="2024-01-15 10:00:00", end_datetime="2024-01-15 11:00:00")
        reminder.add_reminder(title="Buy groceries", due_datetime="2024-01-20 18:00:00", description="Remember to buy groceries")

        self.apps = [contacts, db, email, messaging, calendar, shopping, reminder, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        shopping = self.get_typed_app(ShoppingApp)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please get the details of order order2",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                shopping.get_order_details(self.target_order_id)
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        agent_events = [
            event for event in env.event_log.list_view() if event.event_type == EventType.AGENT
        ]

        # ensure that agent called the get_order_details tool
        try:
            target_event = next(event for event in agent_events if event.action.function_name == "get_order_details" and event.action.args["order_id"] == self.target_order_id)
        except StopIteration:
            return ScenarioValidationResult(success=False, exception=Exception("Target event not found"))
        
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss4())

