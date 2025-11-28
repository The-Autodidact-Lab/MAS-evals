from datetime import datetime, timedelta, timezone
import time
from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.contacts import ContactsApp, Contact, Gender, Status
from are.simulation.apps.calendar import CalendarApp
from are.simulation.apps.email_client import EmailClientApp, Email, EmailFolderName
from are.simulation.apps.messaging import MessagingApp, Conversation, Message
from are.simulation.apps.db import DBApp, DBEntry
from are.simulation.apps.apartment_listing import ApartmentListingApp
from are.simulation.apps.cab import CabApp, Ride
from are.simulation.apps.reminder import ReminderApp
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import Action, EventRegisterer, EventType

@register_scenario("ms1")
class ms1(Scenario):
    """
    Multi-app information gathering scenario.
    
    The agent must read across 5 different applications (contacts, calendar, email, 
    messaging, db) to gather information, compare data across steps, and reason 
    before drawing a conclusion about a person's availability.
    
    Relevant apps (should be queried):
    - ContactsApp: Contains contact information
    - CalendarApp: Contains schedule information
    - EmailClientApp: Contains email communications
    - MessagingApp: Contains message history
    - DBApp: Contains additional database entries
    
    Distractor apps (should NOT be queried):
    - ApartmentListingApp: Contains apartment listings (not relevant)
    - CabApp: Contains ride history (not relevant)
    - ReminderApp: Contains reminders (not relevant)
    """
    
    target_contact_id: str | None = None
    target_db_id: str | None = None

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialise apps
        agui = AgentUserInterface()
        contacts = ContactsApp()
        calendar = CalendarApp()
        email = EmailClientApp()
        messaging = MessagingApp()
        db = DBApp()
        apartments = ApartmentListingApp()
        cab = CabApp()
        reminders = ReminderApp()
        
        # Calculate next Tuesday afternoon (2 PM)
        now = datetime.now(timezone.utc)
        days_ahead = (1 - now.weekday()) % 7  # Days until next Tuesday (0=Monday, 1=Tuesday)
        if days_ahead == 0:  # If today is Tuesday, get next Tuesday
            days_ahead = 7
        next_tuesday = now + timedelta(days=days_ahead)
        next_tuesday_afternoon = next_tuesday.replace(hour=14, minute=0, second=0, microsecond=0)
        next_tuesday_evening = next_tuesday_afternoon + timedelta(hours=2)
        
        # === POPULATE RELEVANT APPS ===
        # contacts
        sarah_contact = Contact(
            first_name="Sarah",
            last_name="Johnson",
            email="sarah.johnson@company.com",
            phone="+1-555-0101",
            gender=Gender.FEMALE,
            status=Status.EMPLOYED,
            job="Product Manager",
            city_living="San Francisco",
            country="USA",
            age=32
        )
        self.target_contact_id = contacts.add_contact(sarah_contact)
        
        contacts.add_contact(Contact(
            first_name="Michael",
            last_name="Chen",
            email="michael.chen@company.com",
            phone="+1-555-0102",
            gender=Gender.MALE,
            status=Status.EMPLOYED,
            job="Software Engineer"
        ))
        
        # calendar
        calendar.add_calendar_event(
            title="Team Standup",
            start_datetime=next_tuesday_afternoon.strftime("%Y-%m-%d %H:%M:%S"),
            end_datetime=(next_tuesday_afternoon + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            description="Weekly team sync",
            attendees=["sarah.johnson@company.com"]
        )
        
        calendar.add_calendar_event(
            title="Project Review",
            start_datetime=(next_tuesday_afternoon + timedelta(hours=1, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            end_datetime=next_tuesday_evening.strftime("%Y-%m-%d %H:%M:%S"),
            description="Quarterly project review meeting",
            attendees=["sarah.johnson@company.com", "michael.chen@company.com"]
        )
        
        calendar.add_calendar_event(
            title="Lunch Break",
            start_datetime=(next_tuesday_afternoon - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            end_datetime=next_tuesday_afternoon.strftime("%Y-%m-%d %H:%M:%S"),
            description="Lunch with team",
            attendees=[]
        )
        
        # email
        email.add_email(Email(
            sender="sarah.johnson@company.com",
            recipients=["user@meta.com"],
            subject="Meeting Request - Next Tuesday",
            content="Hi, I'm checking if you're available for a quick sync next Tuesday afternoon around 2 PM. Let me know!",
            timestamp=time.time() - 86400  # 1 day ago
        ))
        
        email.add_email(Email(
            sender="sarah.johnson@company.com",
            recipients=["user@meta.com"],
            subject="Re: Meeting Request - Next Tuesday",
            content="Actually, I just realized I have a conflict. Can we reschedule?",
            timestamp=time.time() - 43200  # 12 hours ago
        ))
        
        email.add_email(Email(
            sender="michael.chen@company.com",
            recipients=["sarah.johnson@company.com", "user@meta.com"],
            subject="Project Review Meeting",
            content="Reminder: Project review meeting scheduled for next Tuesday at 3:30 PM.",
            timestamp=time.time() - 172800  # 2 days ago
        ))
        
        # messaging
        conv_id = messaging.create_conversation(
            participants=["Sarah Johnson"],
            title="Chat with Sarah"
        )
        conversation = messaging.conversations[conv_id]
        conversation.messages.append(Message(
            sender="Sarah Johnson",
            content="Hey! Are you free next Tuesday afternoon? I'd like to discuss the project timeline.",
            timestamp=time.time() - 86400
        ))
        conversation.messages.append(Message(
            sender="Me",
            content="Let me check my schedule and get back to you.",
            timestamp=time.time() - 82800
        ))
        conversation.messages.append(Message(
            sender="Sarah Johnson",
            content="Sounds good! I might have a conflict though, so let me confirm.",
            timestamp=time.time() - 43200
        ))
        
        # db
        self.target_db_id = db.create_db_entry(DBEntry(
            entry_id="sarah_availability",
            name="Sarah Johnson",
            email="sarah.johnson@company.com",
            phone="+1-555-0101",
            address="123 Tech Street, San Francisco, CA",
            city="San Francisco",
            state="CA",
            zip_code="94102",
            country="USA",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        ))
        
        db.create_db_entry(DBEntry(
            entry_id="meeting_notes_1",
            name="Meeting Notes",
            email="notes@company.com",
            phone="N/A",
            address="Internal Document",
            city="N/A",
            state="N/A",
            zip_code="N/A",
            country="N/A",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        ))
        
        # === POPULATE DISTRACTOR APPS (should NOT be queried) ===
        
        # apartments
        apartments.add_new_apartment(
            name="Luxury Downtown Apartment",
            location="San Francisco, CA",
            zip_code="94102",
            price=3500.0,
            number_of_bedrooms=2,
            number_of_bathrooms=1,
            square_footage=1200,
            property_type="Apartment"
        )
        
        apartments.add_new_apartment(
            name="Modern Loft",
            location="Oakland, CA",
            zip_code="94601",
            price=2800.0,
            number_of_bedrooms=1,
            number_of_bathrooms=1,
            square_footage=900,
            property_type="Loft"
        )
        
        # cab
        cab.quotation_history.append(Ride(
            start_location="123 Tech Street",
            end_location="456 Business Ave",
            service_type="Default",
            price=25.50,
            distance_km=5.2,
            duration=15.0,
            time_stamp=time.time() - 86400
        ))
        
        # reminders
        reminders.add_reminder(
            title="Buy groceries",
            due_datetime=(now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            description="Remember to buy groceries for the week"
        )
        
        reminders.add_reminder(
            title="Call dentist",
            due_datetime=(now + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
            description="Schedule dental appointment"
        )
        
        # Register all apps
        self.apps = [agui, contacts, calendar, email, messaging, db, apartments, cab, reminders]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        contacts = self.get_typed_app(ContactsApp)
        calendar = self.get_typed_app(CalendarApp)
        email = self.get_typed_app(EmailClientApp)
        messaging = self.get_typed_app(MessagingApp)
        db = self.get_typed_app(DBApp)

        # Calculate next Tuesday afternoon time range for calendar oracle
        now = datetime.now(timezone.utc)
        days_ahead = (1 - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_tuesday = now + timedelta(days=days_ahead)
        next_tuesday_afternoon = next_tuesday.replace(hour=14, minute=0, second=0, microsecond=0)
        next_tuesday_evening = next_tuesday_afternoon + timedelta(hours=2)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="""Please determine if Sarah Johnson is available for a meeting next Tuesday afternoon (around 2 PM). 
                
To do this, you need to:
1. Find Sarah Johnson's contact information
2. Check her calendar for next Tuesday afternoon
3. Review any relevant emails about meetings
4. Check recent messages with Sarah
5. Look up any relevant database entries

After gathering information from all these sources, compare the data, reason about any conflicts or availability, and provide a comprehensive analysis of her availability.""",
            ).depends_on(None, delay_seconds=2)

            # Oracle: Check that the agent accessed the correct database entry
            oracle1 = (
                contacts.get_contact(self.target_contact_id)
                .oracle()
                .depends_on(event1, delay_seconds=5)
            )

            oracle2 = (
                calendar.get_calendar_events_from_to(
                    start_datetime=next_tuesday_afternoon.strftime("%Y-%m-%d %H:%M:%S"),
                    end_datetime=next_tuesday_evening.strftime("%Y-%m-%d %H:%M:%S")
                )
                .oracle()
                .depends_on(event1, delay_seconds=10)
            )

            oracle3 = (
                email.list_emails(offset=0, limit=5)
                .oracle()
                .depends_on(event1, delay_seconds=15)
            )

            oracle4 = (
                messaging.list_recent_conversations(offset=0, limit=5)
                .oracle()
                .depends_on(event1, delay_seconds=20)
            )

            oracle5 = (
                db.get_db_entry(self.target_db_id)
                .oracle()
                .depends_on(event1, delay_seconds=25)
            )

            self.events = [event1, oracle1, oracle2, oracle3, oracle4, oracle5]

    def validate(self, env) -> ScenarioValidationResult:
        agent_events = [
            event for event in env.event_log.list_view() if event.event_type == EventType.AGENT
        ]
        
        # check app accession is handled correctly
        accessed_apps = set()
        relevant_apps = {"ContactsApp", "CalendarApp", "EmailClientApp", "MessagingApp", "DBApp"}
        distractor_apps = {"ApartmentListingApp", "CabApp", "ReminderApp"}
        
        for event in agent_events:
            if hasattr(event, 'action') and isinstance(event.action, Action):
                class_name = getattr(event.action, 'class_name', '')
                if class_name:
                    accessed_apps.add(class_name)
        
        missing_apps = relevant_apps - accessed_apps
        if missing_apps:
            return ScenarioValidationResult(
                success=False, 
                exception=Exception(f"Agent did not access all required apps. Missing: {missing_apps}. Accessed: {accessed_apps}")
            )
        
        accessed_distractors = distractor_apps & accessed_apps
        if accessed_distractors:
            return ScenarioValidationResult(
                success=False,
                exception=Exception(f"Agent incorrectly accessed distractor apps: {accessed_distractors}")
            )
        
        # check each tool call was correct
        # contacts tool call
        try:
            contacts_event = next(
                event for event in agent_events 
                if hasattr(event, 'action') and 
                   isinstance(event.action, Action) and
                   event.action.class_name == "ContactsApp" and
                   event.action.function_name == "get_contact" and
                   hasattr(event.action, 'args') and
                   event.action.args.get("contact_id") == self.target_contact_id
            )
        except StopIteration:
            return ScenarioValidationResult(
                success=False,
                exception=Exception(f"Agent did not access Sarah Johnson's contact (ID: {self.target_contact_id})")
            )
        
        # calendar tool call
        # calculate target time range
        now = datetime.now(timezone.utc)
        days_ahead = (1 - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_tuesday = now + timedelta(days=days_ahead)
        next_tuesday_afternoon = next_tuesday.replace(hour=14, minute=0, second=0, microsecond=0)
        next_tuesday_evening = next_tuesday_afternoon + timedelta(hours=2)
        
        try:
            # Check if agent queried calendar events that include the target time range
            calendar_event = next(
                event for event in agent_events 
                if hasattr(event, 'action') and 
                   isinstance(event.action, Action) and
                   event.action.class_name == "CalendarApp" and
                   event.action.function_name == "get_calendar_events_from_to" and
                   hasattr(event.action, 'args')
            )
            # Verify the queried range includes the target time range
            args = calendar_event.action.args
            query_start = datetime.strptime(args.get("start_datetime"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            query_end = datetime.strptime(args.get("end_datetime"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            
            if query_start > next_tuesday_afternoon or query_end < next_tuesday_evening:
                return ScenarioValidationResult(
                    success=False,
                    exception=Exception(f"Agent queried calendar events but the time range ({args.get('start_datetime')} to {args.get('end_datetime')}) does not include next Tuesday afternoon ({next_tuesday_afternoon.strftime('%Y-%m-%d %H:%M:%S')} to {next_tuesday_evening.strftime('%Y-%m-%d %H:%M:%S')})")
                )
        except (StopIteration, ValueError, KeyError, TypeError) as e:
            return ScenarioValidationResult(
                success=False,
                exception=Exception(f"Agent did not access calendar events for next Tuesday afternoon ({next_tuesday_afternoon.strftime('%Y-%m-%d %H:%M:%S')} to {next_tuesday_evening.strftime('%Y-%m-%d %H:%M:%S')}): {str(e)}")
            )
        
        # email tool call
        try:
            email_event = next(
                event for event in agent_events 
                if hasattr(event, 'action') and 
                   isinstance(event.action, Action) and
                   event.action.class_name == "EmailClientApp" and
                   event.action.function_name == "get_emails" and
                   hasattr(event.action, 'args')
            )
        except StopIteration:
            return ScenarioValidationResult(
                success=False,
                exception=Exception("Agent did not access emails")
            )
        
        # messaging tool call
        try:
            messaging_event = next(
                event for event in agent_events 
                if hasattr(event, 'action') and 
                   isinstance(event.action, Action) and
                   event.action.class_name == "MessagingApp" and
                   event.action.function_name == "list_recent_conversations" and
                   hasattr(event.action, 'args')
            )
        except StopIteration:
            return ScenarioValidationResult(
                success=False,
                exception=Exception("Agent did not access recent conversations")
            )
        
        # db tool call
        try:
            db_event = next(
                event for event in agent_events 
                if hasattr(event, 'action') and 
                   isinstance(event.action, Action) and
                   event.action.class_name == "DBApp" and
                   event.action.function_name == "get_db_entry" and
                   hasattr(event.action, 'args') and
                   event.action.args.get("entry_id") == self.target_db_id
            )
        except StopIteration:
            return ScenarioValidationResult(
                success=False,
                exception=Exception(f"Agent did not access the target database entry (ID: {self.target_db_id})")
            )
        
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ms1())
