from are.simulation.apps.agent_user_interface import AgentUserInterface
from are.simulation.apps.shopping import Item, Product, ShoppingApp
from are.simulation.scenarios.scenario import Scenario, ScenarioValidationResult
from are.simulation.scenarios.utils.registry import register_scenario
from are.simulation.types import EventRegisterer, EventType

@register_scenario("ss12")
class ss12(Scenario):
    target_item_id: str | None = None

    def init_and_populate_apps(self, *args, **kwargs) -> None:
        # initialize apps
        shopping = ShoppingApp()
        agui = AgentUserInterface()
        
        # Create products with items
        product1 = Product(name="Laptop", product_id="prod1")
        item1 = Item(item_id="item1", price=999.99, available=True)
        product1.variants["default"] = item1
        shopping.products["prod1"] = product1

        product2 = Product(name="Mouse", product_id="prod2")
        self.target_item_id = "item2"
        item2 = Item(item_id=self.target_item_id, price=29.99, available=True)
        product2.variants["default"] = item2
        shopping.products["prod2"] = product2

        product3 = Product(name="Keyboard", product_id="prod3")
        item3 = Item(item_id="item3", price=79.99, available=True)
        product3.variants["default"] = item3
        shopping.products["prod3"] = product3

        self.apps = [shopping, agui]

    def build_events_flow(self) -> None:
        agui = self.get_typed_app(AgentUserInterface)
        shopping = self.get_typed_app(ShoppingApp)

        with EventRegisterer.capture_mode():
            event1 = agui.send_message_to_agent(
                content="Please add a Mouse to the cart with quantity 2",
            ).depends_on(None, delay_seconds=2)

            oracle1 = (
                shopping.add_to_cart(self.target_item_id, quantity=2)
                .oracle()
                .depends_on(event1, delay_seconds=2)
            )

            self.events = [event1, oracle1]

    def validate(self, env) -> ScenarioValidationResult:
        return ScenarioValidationResult(success=True)

if __name__ == "__main__":
    from are.simulation.scenarios.utils.cli_utils import run_and_validate
    run_and_validate(ss12())

