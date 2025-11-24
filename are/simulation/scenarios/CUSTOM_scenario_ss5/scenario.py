from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.calendar import CalendarApp, CalendarEvent
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss5")
class ss5(Scenario):
    target_event_id: str | None = None

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        calendar = CalendarApp()
        agui = AgentUserInterface()
        
        # initial population of calendar events
        event1_id = calendar.add_calendar_event(
            title="Team Meeting",
            start_datetime="2024-01-15 10:00:00",
            end_datetime="2024-01-15 11:00:00",
        )

        self.target_event_id = calendar.add_calendar_event(
            title="Doctor Appointment",
            start_datetime="2024-01-16 14:00:00",
            end_datetime="2024-01-16 15:00:00",
            description="Annual checkup",
        )

        event3_id = calendar.add_calendar_event(
            title="Lunch",
            start_datetime="2024-01-17 12:00:00",
            end_datetime="2024-01-17 13:00:00",
        )

        self.apps = [calendar, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        calendar = self.get_typed_app(CalendarApp)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please get the details of the 'Doctor Appointment' event",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                calendar.get_calendar_event(self.target_event_id)
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        agent_events = [
            event for event in env.event_log.list_view() if event.event_type == EventType.AGENT
        ]

        # ensure that agent called the get_calendar_event tool
        try:
            target_event = next(event for event in agent_events if event.action.function_name == "get_calendar_event" and event.action.args["event_id"] == self.target_event_id)
        except StopIteration:
            return ScenarioValidationResult(success=False, exception=Exception("Target event not found"))
        
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss5())

