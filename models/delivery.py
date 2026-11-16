from abc import ABC, abstractmethod


class DeliveryMethod(ABC):
    """Абстрактный базовый класс для всех способов доставки."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Возвращает человекочитаемое название способа доставки."""
        pass

    @property
    @abstractmethod
    def requires_courier(self) -> bool:
        """Указывает, требуется ли назначение курьера для этого способа."""
        pass

    @abstractmethod
    def calculate_cost(self, items_total: float) -> float:
        """Рассчитывает стоимость доставки на основе суммы товаров."""
        pass

    @abstractmethod
    def get_estimated_time(self) -> str:
        """Возвращает ориентировочный срок доставки."""
        pass

    def __str__(self) -> str:
        return f"{self.name} (срок: {self.get_estimated_time()})"


class StandardDelivery(DeliveryMethod):
    """Стандартная курьерская доставка (бесплатна при заказе от 2000 руб.)."""

    BASE_COST = 300.0
    FREE_THRESHOLD = 2000.0

    @property
    def name(self) -> str:
        return "Стандартная доставка курьером"

    @property
    def requires_courier(self) -> bool:
        return True

    def calculate_cost(self, items_total: float) -> float:
        if items_total >= self.FREE_THRESHOLD:
            return 0.0
        return self.BASE_COST

    def get_estimated_time(self) -> str:
        return "1-2 дня"


class ExpressDelivery(DeliveryMethod):
    """Ускоренная курьерская доставка (фиксированная ставка + 10% от суммы)."""

    BASE_COST = 500.0
    PERCENT_FEE = 0.10

    @property
    def name(self) -> str:
        return "Экспресс-доставка"

    @property
    def requires_courier(self) -> bool:
        return True

    def calculate_cost(self, items_total: float) -> float:
        return round(self.BASE_COST + items_total * self.PERCENT_FEE, 2)

    def get_estimated_time(self) -> str:
        return "2-3 часа"


class PickupDelivery(DeliveryMethod):
    """Самовывоз из пункта выдачи (бесплатно и без назначения курьера)."""

    @property
    def name(self) -> str:
        return "Самовывоз из пункта выдачи"

    @property
    def requires_courier(self) -> bool:
        return False

    def calculate_cost(self, items_total: float) -> float:
        return 0.0

    def get_estimated_time(self) -> str:
        return "Сегодня, через 1 час"
