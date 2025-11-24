from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.contacts import Contact, ContactsApp, Gender, Status
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss3")
class ss3(Scenario):
    target_contact_id: str | None = None

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        contacts = ContactsApp()
        agui = AgentUserInterface()
        
        # initial population of contacts
        contacts.add_contact(Contact(
            contact_id="1",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            gender=Gender.MALE,
            status=Status.EMPLOYED,
        ))

        self.target_contact_id = contacts.add_contact(Contact(
            contact_id="2",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="0987654321",
            gender=Gender.FEMALE,
            status=Status.EMPLOYED,
        ))

        contacts.add_contact(Contact(
            contact_id="3",
            first_name="Jim",
            last_name="Brown",
            email="jim.brown@example.com",
            phone="1112223333",
            gender=Gender.MALE,
            status=Status.STUDENT,
        ))

        self.apps = [contacts, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        contacts = self.get_typed_app(ContactsApp)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please get the email address of Jane Smith",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                contacts.search_contacts("Jane Smith")
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        agent_events = [
            event for event in env.event_log.list_view() if event.event_type == EventType.AGENT
        ]

        # ensure that agent called the search_contacts tool
        try:
            target_event = next(event for event in agent_events if event.action.function_name == "search_contacts" and "Jane Smith" in event.action.args.get("query", ""))
        except StopIteration:
            return ScenarioValidationResult(success=False, exception=Exception("Target event not found"))
        
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss3())

