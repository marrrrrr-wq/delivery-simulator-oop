from typing import List, Optional
from models.entities import Client, Courier, OrderItem
from models.delivery import DeliveryMethod
from models.order import Order
from models.enums import OrderStatus


class DeliveryService:
    """Сервис для управления заказами и курьерами в памяти."""

    def __init__(self) -> None:
        self._orders: List[Order] = []
        self._couriers: List[Courier] = []
        self._next_order_id: int = 1
        self._seed_couriers()

    def _seed_couriers(self) -> None:
        """Добавляет тестовый список курьеров при запуске программы."""
        self._couriers.extend([
            Courier(1, "Алексей Смирнов", "+7 (999) 111-22-33"),
            Courier(2, "Мария Иванова", "+7 (999) 444-55-66"),
            Courier(3, "Дмитрий Кузнецов", "+7 (999) 777-88-99"),
        ])

    def create_order(self, client_name: str, client_phone: str, address: str) -> Order:
        """Создает новый заказ и сохраняет его в системе."""
        client = Client(client_name, client_phone)
        order = Order(self._next_order_id, client, address)
        self._orders.append(order)
        self._next_order_id += 1
        return order

    def add_item_to_order(
        self, order_id: int, title: str, quantity: int, price: float
    ) -> Order:
        """Добавляет товарную позицию в существующий заказ."""
        order = self.get_order_by_id(order_id)
        item = OrderItem(title, quantity, price)
        order.add_item(item)
        return order

    def get_all_orders(self) -> List[Order]:
        """Возвращает список всех созданных заказов."""
        return list(self._orders)

    def get_order_by_id(self, order_id: int) -> Order:
        """Находит заказ по номеру или выбрасывает ошибку, если его нет."""
        for order in self._orders:
            if order.order_id == order_id:
                return order
        raise ValueError(f"Заказ с номером #{order_id} не найден.")

    def get_all_couriers(self) -> List[Courier]:
        """Возвращает список всех курьеров."""
        return list(self._couriers)

    def get_available_couriers(self) -> List[Courier]:
        """Возвращает список только свободных курьеров."""
        return [courier for courier in self._couriers if not courier.is_busy]

    def set_delivery_method(self, order_id: int, method: DeliveryMethod) -> Order:
        """Устанавливает способ доставки для заказа."""
        order = self.get_order_by_id(order_id)
        order.set_delivery_method(method)
        return order

    def assign_courier_to_order(self, order_id: int, courier_id: int) -> Order:
        """Назначает свободного курьера на указанный заказ."""
        order = self.get_order_by_id(order_id)
        courier = self._get_courier_by_id(courier_id)
        order.assign_courier(courier)
        return order

    def change_order_status(self, order_id: int, new_status: OrderStatus) -> Order:
        """Изменяет статус указанного заказа."""
        order = self.get_order_by_id(order_id)
        order.change_status(new_status)
        return order

    def _get_courier_by_id(self, courier_id: int) -> Courier:
        """Вспомогательный метод поиска курьера по ID."""
        for courier in self._couriers:
            if courier.courier_id == courier_id:
                return courier
        raise ValueError(f"Курьер с ID #{courier_id} не найден.")
