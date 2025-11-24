from datetime import datetime, timezone
from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.shopping import CartItem, Order, ShoppingApp
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss7")
class ss7(Scenario):
    target_order_id: str | None = None

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        shopping = ShoppingApp()
        agui = AgentUserInterface()
        
        # Create some orders
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

        self.apps = [shopping, agui]

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
    run_and_validate(ss7())

