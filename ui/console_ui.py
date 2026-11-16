from services.delivery_service import DeliveryService
from models.delivery import StandardDelivery, ExpressDelivery, PickupDelivery
from models.enums import OrderStatus
class ConsoleUI:
    """Компонент консольного пользовательского интерфейса."""

    def __init__(self, service: DeliveryService) -> None:
        self._service: DeliveryService = service

    def run(self) -> None:
        """Запускает главный цикл консольного меню."""
        print("Добро пожаловать в симулятор службы доставки!")
        while True:
            has_orders = bool(self._service.get_all_orders())
            self._print_menu(has_orders)
            max_choice = 6 if has_orders else 1
            choice = input(f"Выберите действие (0-{max_choice}): ").strip()

            try:
                if choice == "1":
                    self._handle_create_order()
                elif choice == "0":
                    print("Работа программы завершена. До свидания!")
                    break
                elif not has_orders and choice in ("2", "3", "4", "5", "6"):
                    print("\n[Внимание]: Сначала создайте хотя бы один заказ (пункт 1).")
                elif choice == "2":
                    self._handle_list_orders()
                elif choice == "3":
                    self._handle_select_delivery()
                elif choice == "4":
                    self._handle_assign_courier()
                elif choice == "5":
                    self._handle_change_status()
                elif choice == "6":
                    self._handle_add_item_to_existing_order()
                else:
                    print(f"Ошибка: выберите пункт меню от 0 до {max_choice}.")
            except ValueError as error:
                print(f"\n[Ошибка операции]: {error}")
            except Exception as error:
                print(f"\n[Непредвиденная ошибка]: {error}")

    def _print_menu(self, has_orders: bool) -> None:
        print("\n" + "=" * 40)
        print("МЕНЮ СЛУЖБЫ ДОСТАВКИ:")
        print("1. Создать новый заказ")
        if has_orders:
            print("2. Показать список существующих заказов")
            print("3. Изменить способ доставки для заказа")
            print("4. Назначить или сменить курьера")
            print("5. Изменить статус заказа")
            print("6. Добавить позицию в существующий заказ")
        print("0. Выход")
        print("=" * 40)

    def _read_int(self, prompt: str) -> int:
        """Безопасно считывает целое число с консоли."""
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            raise ValueError(f"Ожидалось целое число, получено: '{raw}'.")

    def _read_float(self, prompt: str) -> float:
        """Безопасно считывает дробное число с консоли."""
        raw = input(prompt).strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            raise ValueError(f"Ожидалось число, получено: '{raw}'.")

    def _prompt_existing_order(self):
        """Запрашивает номер заказа и сразу проверяет, существует ли он."""
        orders = self._service.get_all_orders()
        available_ids = ", ".join(f"#{o.order_id}" for o in orders)
        order_id = self._read_int(f"\nВведите номер заказа (доступны: {available_ids}): ")
        return self._service.get_order_by_id(order_id)

    def _handle_create_order(self) -> None:
        print("\n--- Создание нового заказа ---")
        while True:
            name = input("Введите имя клиента: ")
            if name.strip() and all(ch.isalpha() or ch in " -" for ch in name.strip()):
                break
            print("Ошибка: имя должно содержать только буквы.")

        while True:
            phone = input("Введите телефон клиента (+7XXXXXXXXXX или 8XXXXXXXXXX): ").strip()
            if (phone.startswith("+7") and len(phone) == 12 and phone[1:].isdigit()) or (
                phone.startswith("8") and len(phone) == 11 and phone.isdigit()
            ):
                break
            print("Ошибка: введите телефон в формате +7XXXXXXXXXX или 8XXXXXXXXXX.")

        address = input("Введите адрес доставки: ")
        order = self._service.create_order(name, phone, address)
        print(f"Заказ #{order.order_id} создан. Теперь добавьте позиции.")

        while True:
            self._add_item_prompt(order.order_id)
            more = input("Добавить еще один товар? (д/н): ").strip().lower()
            if more not in ("д", "y", "yes", "да"):
                break

        updated_order = self._select_delivery_for_order(order.order_id)

        if updated_order.delivery_method and updated_order.delivery_method.requires_courier:
            updated_order = self._assign_courier_for_order(order.order_id)

        print("\nЗаказ полностью оформлен:")
        print(updated_order)

    def _select_delivery_for_order(self, order_id: int):
        """Пошагово запрашивает и устанавливает способ доставки для заказа."""
        print("\n--- Выбор способа доставки ---")
        print("1. Стандартная доставка курьером (300 руб., бесплатно от 2000 руб., 1-2 дня)")
        print("2. Экспресс-доставка (500 руб. + 10% от суммы, 2-3 часа)")
        print("3. Самовывоз из пункта выдачи (0 руб., сегодня через 1 час)")

        while True:
            choice = input("Выберите способ доставки (1-3): ").strip()
            if choice == "1":
                method = StandardDelivery()
                break
            elif choice == "2":
                method = ExpressDelivery()
                break
            elif choice == "3":
                method = PickupDelivery()
                break
            print("Ошибка: выберите вариант от 1 до 3.")

        updated_order = self._service.set_delivery_method(order_id, method)
        print(f"Способ доставки установлен: {method.name} (стоимость: {updated_order.get_delivery_cost():.2f} руб.).")
        return updated_order

    def _assign_courier_for_order(self, order_id: int):
        """Пошагово запрашивает и назначает свободного курьера на заказ."""
        couriers = self._service.get_available_couriers()
        if not couriers:
            print("\n[Внимание]: Сейчас нет свободных курьеров. Вы сможете назначить его позже через меню.")
            return self._service.get_order_by_id(order_id)

        print("\n--- Назначение курьера ---")
        print("Свободные курьеры:")
        for courier in couriers:
            print(f"  {courier}")

        while True:
            try:
                courier_id = self._read_int("Введите ID курьера для назначения: ")
                updated_order = self._service.assign_courier_to_order(order_id, courier_id)
                print(f"Курьер успешно назначен на заказ #{order_id}.")
                return updated_order
            except ValueError as error:
                print(f"[Ошибка]: {error} Попробуйте снова.")

    def _handle_add_item_to_existing_order(self) -> None:
        order = self._prompt_existing_order()
        self._add_item_prompt(order.order_id)
        updated_order = self._service.get_order_by_id(order.order_id)
        print("\nОбновленный заказ:")
        print(updated_order)

    def _add_item_prompt(self, order_id: int) -> None:
        menu = self._service.get_menu()
        print("\nДоступное меню:")
        for item_id, (title, price) in menu.items():
            print(f"  {item_id}. {title} — {price:.2f} руб.")

        while True:
            try:
                menu_choice = self._read_int("Выберите номер блюда из меню: ")
                quantity = self._read_int("Введите количество (от 1 до 10 шт.): ")
                self._service.add_menu_item_to_order(order_id, menu_choice, quantity)
                print("Позиция успешно добавлена в заказ.")
                break
            except ValueError as error:
                print(f"[Ошибка]: {error} Попробуйте снова.")

    def _handle_list_orders(self) -> None:
        orders = self._service.get_all_orders()
        if not orders:
            print("\nСписок заказов пока пуст.")
            return

        print("\n--- Список всех заказов ---")
        for order in orders:
            print(order)
            print("-" * 40)

    def _handle_select_delivery(self) -> None:
        order = self._prompt_existing_order()
        updated_order = self._select_delivery_for_order(order.order_id)
        if updated_order.delivery_method and updated_order.delivery_method.requires_courier and not updated_order.courier:
            updated_order = self._assign_courier_for_order(order.order_id)
        print(f"Итоговая сумма заказа: {updated_order.get_total_cost():.2f} руб.")

    def _handle_assign_courier(self) -> None:
        order = self._prompt_existing_order()
        updated_order = self._assign_courier_for_order(order.order_id)
        print("\nОбновленный заказ:")
        print(updated_order)

    def _handle_change_status(self) -> None:
        order = self._prompt_existing_order()
        print(f"Текущий статус заказа #{order.order_id}: {order.status.value}")

        statuses = list(OrderStatus)
        print("Выберите новый статус:")
        for idx, status in enumerate(statuses, start=1):
            print(f"{idx}. {status.value}")

        choice = self._read_int("Номер статуса: ")
        if choice < 1 or choice > len(statuses):
            raise ValueError("Некорректный номер статуса.")

        selected_status = statuses[choice - 1]
        updated_order = self._service.change_order_status(order.order_id, selected_status)
        print("\nСтатус заказа успешно обновлен:")
        print(updated_order)

