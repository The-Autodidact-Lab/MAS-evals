from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.email_client import Email, EmailClientV2, EmailFolderName
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss4")
class ss4(Scenario):
    target_email_id: str | None = None

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        email = EmailClientV2()
        agui = AgentUserInterface()
        
        # initial population of emails
        email1 = Email(
            sender="sender1@example.com",
            recipients=["user@meta.com"],
            subject="First Email",
            content="This is the first email",
        )
        email.add_email(email1, EmailFolderName.INBOX)

        target_email = Email(
            sender="sender2@example.com",
            recipients=["user@meta.com"],
            subject="Important Meeting",
            content="Please attend the meeting tomorrow at 3pm",
        )
        self.target_email_id = email.add_email(target_email, EmailFolderName.INBOX)

        email3 = Email(
            sender="sender3@example.com",
            recipients=["user@meta.com"],
            subject="Third Email",
            content="This is the third email",
        )
        email.add_email(email3, EmailFolderName.INBOX)

        self.apps = [email, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        email = self.get_typed_app(EmailClientV2)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please get the content of the email with subject 'Important Meeting'",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                email.get_email_by_id(self.target_email_id, EmailFolderName.INBOX.value)
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        agent_events = [
            event for event in env.event_log.list_view() if event.event_type == EventType.AGENT
        ]

        # ensure that agent called the get_email_by_id tool
        try:
            target_event = next(event for event in agent_events if event.action.function_name == "get_email_by_id" and event.action.args["email_id"] == self.target_email_id)
        except StopIteration:
            return ScenarioValidationResult(success=False, exception=Exception("Target event not found"))
        
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss4())

