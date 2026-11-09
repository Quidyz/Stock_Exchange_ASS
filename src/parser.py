from src.exchange import Exchange
from src.order import Order, ActionType, OrderType, OrderStatus

class Parser:
    """Парсинг входных данных и передача в главный орган"""
    def __init__(self, core: Exchange):
        self.core = core
        self.commands = {
            'BUY': self.trade_command,
            'SELL': self.trade_command,
            'QUOTE': self.quote_command,
            'VIEW': self.view_command
        }

    def _command_parser(self, user_input: list) -> tuple:
        if not user_input:
            raise ValueError("Укажите тикер и параметры заявки.")
        stock = user_input[0]

        match user_input[1:]:
            case ["LMT", price_str, quantity_str]:
                if not price_str.startswith('$'):
                    raise ValueError("Цена должна начинаться с '$'.")

                self._int_check(price_str.lstrip('$'))
                self._int_check(quantity_str)

                price = float(price_str.lstrip('$'))
                quantity = int(quantity_str)
                return stock, ActionType.LIMIT, price, quantity

            case ["MKT", quantity_str]:
                self._int_check(quantity_str)
                quantity = int(quantity_str)
                return stock, ActionType.MARKET, None, quantity

            case ["LMT", *another]:
                raise ValueError("Для LMT заявки требуются: Продажа/Покупка, LMT, Цена, Кол-во")

            case ["MKT", *another]:
                raise ValueError("Для MKT заявки требуются: Продажа/Покупка, MKT, Кол-во")

            case _:
                raise ValueError("Указанного вида заявки не существует.")

    def trade_command(self, action, parts):
        try:
            action_enum = OrderType[action]
            stock, action_type, price, quantity = self._command_parser(parts)

            order = self.core.place_order(action_enum, stock, action_type, price, quantity)
            print(order.action, order.stock, order.action_type, order.price, order.quantity)
            buy_type = "покупку" if order.action == OrderType.BUY else "продажу"
            if order.status == OrderStatus.CANCELLED:
                msg = (
                    f"Рыночная заявка отменена: не исполнено "
                    f"{order.get_quantity()} из {order.quantity} акций {order.stock}."
                )
            elif action_type == ActionType.LIMIT:
                msg = f"Вы разместили лимитную заявку на {buy_type} {order.quantity} акций {order.stock} по цене ${order.price} за штуку."
            else:
                msg = f"Вы разместили рыночную заявку на {buy_type} {order.quantity} акций {order.stock}."

            print(msg)
        except (ValueError, TypeError) as e:
            print(f'Ошибка - {e}')
        except RuntimeError as e:
            print(f'Ошибка обработки заявки - {e}')

    def quote_command(self, action, parts):
        if len(parts) != 1:
            print("Формат команды: QUOTE <тикер>")
            return
        stock = parts[0]
        if stock not in self.core.books:
            print(f"Акция - {stock}. Сейчас отсутствует на рынке.")
            return
        bid, ask, last_trade_price = self.core.books[stock].get_quote()

        bid_str = float(bid) if bid is not None else "0.0"
        ask_str = float(ask) if ask is not None else "0.0"
        last_trade_price = float(last_trade_price) if last_trade_price is not None else "0.0"

        print(f"SNAP BID: ${bid_str} ASK: ${ask_str} LAST: ${last_trade_price}")

    def view_command(self, action, parts):
        if len(parts) == 1 and action == 'VIEW' and parts[0] == 'ORDERS':
            output = []
            sorted_list = self.core.get_sorted_orders_list()
            if not sorted_list:
                print("Список на данный момент пуст")
                return

            for i, order in enumerate(sorted_list, 1):
                if order.execution_price is not None:
                    price = f"${order.execution_price}"
                elif order.price is not None:
                    price = f"${order.price}"
                else:
                    price = "—"
                line = f'{i}. {order.stock} {order.action_type.value} {order.action.value} {price} {order.quantity} {order.filled_quantity}/{order.quantity} {order.status.value}'
                output.append(line)
            msg = '\n'.join(output)
            print(msg)
        else:
            print("Может вы имели ввиду VIEW ORDERS ?")
            return

    def run(self):
        print('SEASS started. QUIT for exit')
        while True:
            user_input = input('Action: ').upper().split()
            if not user_input:
                continue

            action, parts = user_input[0], user_input[1:]

            if action == 'QUIT':
                return
            self.commands[action](action, parts) if action in self.commands else print(f"Неизвестная команда: {action}.")

    @staticmethod
    def _int_check(value):
        try:
            float(value)
        except ValueError:
            raise ValueError(f"Значение {value} должно быть числом")