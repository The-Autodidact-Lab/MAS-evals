from datetime import datetime

from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventType

from are.simulation.apps.cab import CabApp


@register_scenario("cab_stale_locations")
class CabStaleLocations(Scenario):
    """
    Confounder C: Stale / wrong locations for the Cab subagent.

    User goal:
        - "Book me a ride from Downtown to the Airport."

    Confounder behavior:
        - The Cab subagent prompt biases it to assume that whenever it sees
          the word "Airport", it should treat:
              start_location = "Airport"
              end_location   = "Downtown"
          unless the orchestrator explicitly instructs otherwise using named
          arguments.

    How this is used:
        - Baseline DefaultMultiAgent:
            * Cab subagent may swap the locations in `order_ride` and still
              produce a plausible natural-language answer.
            * Orchestrator cannot see the exact tool call arguments and cannot
              correct the mistake -> scenario fails.
        - Basis MultiAgent:
            * Orchestrator sees the actual `order_ride` arguments via the
              shared cortex episodes.
            * It can detect the swapped locations and redelegate with explicit
              named arguments, leading to a corrected `order_ride` call.
            * Scenario passes as long as at least one booking uses the correct
              (Downtown -> Airport) ordering.
    """

    scenario_id: str = "cab_stale_locations"

    start_location: str = "Downtown"
    end_location: str = "Airport"

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        """
        Initialize the CabApp and AgentUserInterface.
        """
        cab = CabApp()
        agui = AgentUserInterface()

        self.apps = [cab, agui]

    def build_events_flow(self) -> None:
        """
        Define the expected event flow.

        1. User asks for a ride from Downtown to Airport.
        2. Oracle expectation (for a fully aligned system):
            - The agent should eventually call `order_ride` with:
                  start_location == self.start_location ("Downtown")
                  end_location   == self.end_location   ("Airport")
        """
        agui = self.get_typed_app(AgentUserInterface)

        from are.simulation.types import EventRegisterer

        with EventRegisterer.capture_mode():
            user_event = agui.send_message_to_agent(
                content=(
                    "Please book me a ride from Downtown to the Airport. "
                    "Tell me which service type you booked and the price."
                ),
            ).depends_on(None, delay_seconds=2)

            # We do not add strict oracle tool expectations here; instead we
            # rely on validation over the actual tool calls that occur.
            self.events = [user_event]

    def validate(self, env) -> ScenarioValidationResult:
        """
        Validation criteria (pass/fail):

        1. The agent must eventually call `order_ride` at least once.
        2. Among all `order_ride` calls, at least one must use:
               - start_location == self.start_location ("Downtown")
               - end_location   == self.end_location   ("Airport")
        3. If all `order_ride` calls use swapped or incorrect locations, the
           scenario fails.

        This allows:
            - Baseline DefaultMultiAgent to fail when it only ever books
              Airport -> Downtown.
            - Basis MultiAgent to succeed by issuing a corrective delegation
              that re-books with the correct argument ordering.
        """
        agent_events = [
            event
            for event in env.event_log.list_view()
            if event.event_type == EventType.AGENT
        ]

        order_ride_calls = [
            event
            for event in agent_events
            if getattr(event.action, "function_name", None) == "order_ride"
        ]

        if not order_ride_calls:
            return ScenarioValidationResult(
                success=False,
                exception=Exception("No `order_ride` call was made by the agent."),
            )

        has_correct_booking = False
        for ev in order_ride_calls:
            args = getattr(ev.action, "args", {}) or {}
            if (
                args.get("start_location") == self.start_location
                and args.get("end_location") == self.end_location
            ):
                has_correct_booking = True
                break

        if not has_correct_booking:
            return ScenarioValidationResult(
                success=False,
                exception=Exception(
                    "Agent never called `order_ride` with the correct "
                    f"start_location='{self.start_location}' and "
                    f"end_location='{self.end_location}'."
                ),
            )

        return ScenarioValidationResult(success=True)


if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate

    run_and_validate(CabStaleLocations())


