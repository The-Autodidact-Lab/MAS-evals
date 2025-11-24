from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.messaging_v2 import ConversationV2, MessageV2, MessagingAppV2, MessagingAppMode
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss6")
class ss6(Scenario):
    target_conversation_id: str | None = None

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        messaging = MessagingAppV2(
            current_user_id="user1",
            current_user_name="User",
            mode=MessagingAppMode.NAME,
        )
        agui = AgentUserInterface()
        
        # Add users
        messaging.add_users(["Alice", "Bob", "Charlie"])

        # initial population of conversations
        conv1 = ConversationV2(
            participant_ids=["user1", messaging.get_user_id("Alice")],
            title="Alice",
        )
        conv1.messages.append(MessageV2(
            sender_id=messaging.get_user_id("Alice"),
            content="Hello, how are you?",
        ))
        messaging.add_conversation(conv1)

        target_conv = ConversationV2(
            participant_ids=["user1", messaging.get_user_id("Bob")],
            title="Bob",
        )
        target_conv.messages.append(MessageV2(
            sender_id=messaging.get_user_id("Bob"),
            content="Can we meet tomorrow?",
        ))
        self.target_conversation_id = target_conv.conversation_id
        messaging.add_conversation(target_conv)

        conv3 = ConversationV2(
            participant_ids=["user1", messaging.get_user_id("Charlie")],
            title="Charlie",
        )
        conv3.messages.append(MessageV2(
            sender_id=messaging.get_user_id("Charlie"),
            content="Thanks for the help!",
        ))
        messaging.add_conversation(conv3)

        self.apps = [messaging, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        messaging = self.get_typed_app(MessagingAppV2)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please read the conversation with Bob",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                messaging.read_conversation(self.target_conversation_id, offset=0, limit=10)
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        agent_events = [
            event for event in env.event_log.list_view() if event.event_type == EventType.AGENT
        ]

        # ensure that agent called the read_conversation tool
        try:
            target_event = next(event for event in agent_events if event.action.function_name == "read_conversation" and event.action.args["conversation_id"] == self.target_conversation_id)
        except StopIteration:
            return ScenarioValidationResult(success=False, exception=Exception("Target event not found"))
        
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss6())

