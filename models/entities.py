import re


class Person:
    """Базовый класс для представления человека в системе."""

    NAME_PATTERN = re.compile(r"^[А-Яа-яЁёA-Za-z\s-]+$")
    PHONE_PATTERN = re.compile(r"^(\+7|8)\d{10}$")

    def __init__(self, name: str, phone: str) -> None:
        if not name or not name.strip():
            raise ValueError("Имя не может быть пустым.")
        clean_name = name.strip()
        if not self.NAME_PATTERN.match(clean_name):
            raise ValueError(
                "Имя должно состоять только из букв (допускаются пробел и дефис)."
            )

        if not phone or not phone.strip():
            raise ValueError("Телефон не может быть пустым.")
        clean_phone = phone.strip()
        if not self.PHONE_PATTERN.match(clean_phone):
            raise ValueError(
                "Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX (11 цифр)."
            )

        self._name: str = clean_name
        self._phone: str = clean_phone

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone



class Client(Person):

    def __str__(self) -> str:
        return f"Клиент: {self._name} (тел: {self._phone})"


class Courier(Person):

    def __init__(self, courier_id: int, name: str, phone: str) -> None:
        super().__init__(name, phone)
        self._courier_id: int = courier_id
        self._is_busy: bool = False

    @property
    def courier_id(self) -> int:
        return self._courier_id

    @property
    def is_busy(self) -> bool:
        return self._is_busy

    def assign(self) -> None:
        """Отмечает курьера как занятого."""
        if self._is_busy:
            raise ValueError(f"Курьер {self._name} уже занят другим заказом.")
        self._is_busy = True

    def release(self) -> None:
        """Освобождает курьера после завершения или отмены заказа."""
        self._is_busy = False

    def __str__(self) -> str:
        status = "Занят" if self._is_busy else "Свободен"
        return f"Курьер #{self._courier_id}: {self._name} ({status})"


class OrderItem:

    def __init__(self, title: str, quantity: int, price: float) -> None:
        if not title or not title.strip():
            raise ValueError("Название товара не может быть пустым.")
        if quantity <= 0:
            raise ValueError("Количество товара должно быть больше нуля.")
        if price <= 0:
            raise ValueError("Цена товара должна быть больше нуля.")

        self._title: str = title.strip()
        self._quantity: int = quantity
        self._price: float = float(price)

    @property
    def title(self) -> str:
        return self._title

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def price(self) -> float:
        return self._price

    def get_total_price(self) -> float:
        """Возвращает общую стоимость позиции."""
        return self._quantity * self._price

    def __str__(self) -> str:
        return f"{self._title} — {self._quantity} шт. x {self._price:.2f} руб. = {self.get_total_price():.2f} руб."
