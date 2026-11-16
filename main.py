from services.delivery_service import DeliveryService
from ui.console_ui import ConsoleUI


def main() -> None:
    """Точка входа в приложение симулятора службы доставки."""
    service = DeliveryService()
    app = ConsoleUI(service)
    app.run()


if __name__ == "__main__":
    main()

