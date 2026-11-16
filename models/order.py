from typing import List, Optional
from models.enums import OrderStatus
from models.entities import Client, Courier, OrderItem
from models.delivery import DeliveryMethod


class Order:
    """Класс заказа, объединяющий клиента, товары, доставку, курьера и статусы."""

    ALLOWED_TRANSITIONS = {
        OrderStatus.CREATED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
        OrderStatus.PROCESSING: [
            OrderStatus.COURIER_ASSIGNED,
            OrderStatus.IN_DELIVERY,
            OrderStatus.CANCELLED,
        ],
        OrderStatus.COURIER_ASSIGNED: [
            OrderStatus.IN_DELIVERY,
            OrderStatus.CANCELLED,
        ],
        OrderStatus.IN_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: [],
    }

    def __init__(self, order_id: int, client: Client, address: str) -> None:
        if not address or not address.strip():
            raise ValueError("Адрес доставки не может быть пустым.")

        self._order_id: int = order_id
        self._client: Client = client
        self._address: str = address.strip()
        self._items: List[OrderItem] = []
        self._delivery_method: Optional[DeliveryMethod] = None
        self._courier: Optional[Courier] = None
        self._status: OrderStatus = OrderStatus.CREATED

    @property
    def order_id(self) -> int:
        return self._order_id

    @property
    def client(self) -> Client:
        return self._client

    @property
    def address(self) -> str:
        return self._address

    @property
    def items(self) -> List[OrderItem]:
        return list(self._items)

    @property
    def delivery_method(self) -> Optional[DeliveryMethod]:
        return self._delivery_method

    @property
    def courier(self) -> Optional[Courier]:
        return self._courier

    @property
    def status(self) -> OrderStatus:
        return self._status

    def add_item(self, item: OrderItem) -> None:
        """Добавляет позицию в заказ, если он еще не передан в доставку."""
        if self._status not in (OrderStatus.CREATED, OrderStatus.PROCESSING):
            raise ValueError(
                f"Нельзя добавлять товары в заказ со статусом '{self._status.value}'."
            )
        self._items.append(item)

    def set_delivery_method(self, method: DeliveryMethod) -> None:
        """Устанавливает способ доставки и сбрасывает курьера, если он больше не нужен."""
        if self._status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise ValueError("Нельзя изменить способ доставки для завершенного заказа.")

        if not method.requires_courier and self._courier is not None:
            self._courier.release()
            self._courier = None

        self._delivery_method = method

    def assign_courier(self, courier: Courier) -> None:
        """Назначает курьера на заказ с проверкой способа доставки и статуса."""
        if self._delivery_method is None:
            raise ValueError("Сначала выберите способ доставки для заказа.")
        if not self._delivery_method.requires_courier:
            raise ValueError(
                f"Способ '{self._delivery_method.name}' не требует назначения курьера."
            )
        if self._status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise ValueError("Нельзя назначить курьера на завершенный или отмененный заказ.")

        if self._courier is not None:
            self._courier.release()

        courier.assign()
        self._courier = courier

        if self._status in (OrderStatus.CREATED, OrderStatus.PROCESSING):
            self._status = OrderStatus.COURIER_ASSIGNED

    def change_status(self, new_status: OrderStatus) -> None:
        """Переводит заказ в новый статус, проверяя допустимость перехода и условия."""
        if new_status == self._status:
            raise ValueError(f"Заказ уже находится в статусе '{new_status.value}'.")

        allowed = self.ALLOWED_TRANSITIONS.get(self._status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Недопустимый переход статуса: '{self._status.value}' -> '{new_status.value}'."
            )

        if new_status != OrderStatus.CANCELLED:
            if not self._items:
                raise ValueError("Нельзя обработать пустой заказ без товаров.")
            if self._delivery_method is None:
                raise ValueError("Нельзя перевести заказ дальше без выбранного способа доставки.")

        if new_status == OrderStatus.IN_DELIVERY:
            if self._delivery_method and self._delivery_method.requires_courier and not self._courier:
                raise ValueError("Для отправки этого заказа сначала назначьте курьера.")

        self._status = new_status

        if new_status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED) and self._courier:
            self._courier.release()

    def get_items_total(self) -> float:
        """Считает стоимость только товаров в заказе."""
        return sum(item.get_total_price() for item in self._items)

    def get_delivery_cost(self) -> float:
        """Считает стоимость доставки полиморфно без проверок типа доставки."""
        if self._delivery_method is None:
            return 0.0
        return self._delivery_method.calculate_cost(self.get_items_total())

    def get_total_cost(self) -> float:
        """Возвращает итоговую стоимость заказа (товары + доставка)."""
        return round(self.get_items_total() + self.get_delivery_cost(), 2)

    def __str__(self) -> str:
        delivery_info = (
            f"{self._delivery_method.name} ({self.get_delivery_cost():.2f} руб., "
            f"срок: {self._delivery_method.get_estimated_time()})"
            if self._delivery_method
            else "Не выбран"
        )
        courier_info = str(self._courier) if self._courier else "Не назначен"
        items_str = (
            "\n    ".join(str(item) for item in self._items)
            if self._items
            else "Нет позиций"
        )

        return (
            f"=== Заказ #{self._order_id} [{self._status.value}] ===\n"
            f"  {self._client}\n"
            f"  Адрес: {self._address}\n"
            f"  Позиции:\n    {items_str}\n"
            f"  Доставка: {delivery_info}\n"
            f"  Курьер: {courier_info}\n"
            f"  Итого к оплате: {self.get_total_cost():.2f} руб."
        )
