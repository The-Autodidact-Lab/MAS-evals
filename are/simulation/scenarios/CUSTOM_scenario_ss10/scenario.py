from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.calendar import CalendarApp
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss10")
class ss10(Scenario):
    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        calendar = CalendarApp()
        agui = AgentUserInterface()

        self.apps = [calendar, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        calendar = self.get_typed_app(CalendarApp)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please add a calendar event titled 'Team Standup' from 2024-01-20 09:00:00 to 2024-01-20 09:30:00",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                calendar.add_calendar_event(
                    title="Team Standup",
                    start_datetime="2024-01-20 09:00:00",
                    end_datetime="2024-01-20 09:30:00",
                )
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss10())

