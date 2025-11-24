from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.messaging_v2 import MessagingAppV2, MessagingAppMode
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss11")
class ss11(Scenario):
    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        messaging = MessagingAppV2(
            current_user_id="user1",
            current_user_name="User",
            mode=MessagingAppMode.NAME,
        )
        agui = AgentUserInterface()
        
        # Add users
        messaging.add_users(["Alice", "Bob"])

        self.apps = [messaging, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        messaging = self.get_typed_app(MessagingAppV2)

        alice_id = messaging.get_user_id("Alice")
        
        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content=f"Please send a message to user {alice_id} saying 'Hello, how are you?'",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                messaging.send_message(
                    user_id=alice_id,
                    content="Hello, how are you?",
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

