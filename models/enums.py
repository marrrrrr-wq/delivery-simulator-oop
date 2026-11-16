from enum import Enum
class OrderStatus(Enum):
    """Перечисление допустимых статусов заказа."""

    CREATED = "Создан"
    PROCESSING = "В обработке"
    COURIER_ASSIGNED = "Назначен курьер"
    IN_DELIVERY = "Передан в доставку"
    DELIVERED = "Доставлен"
    CANCELLED = "Отменен"
