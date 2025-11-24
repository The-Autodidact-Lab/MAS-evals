from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.email_client import Email, EmailClientV2, EmailFolderName
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss9")
class ss9(Scenario):
    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        email = EmailClientV2()
        agui = AgentUserInterface()

        self.apps = [email, agui]

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
    run_and_validate(ss9())

