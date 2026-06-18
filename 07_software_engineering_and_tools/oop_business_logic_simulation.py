# ==============================================================================
# BORDER CONTROL SIMULATION & STATE MANAGEMENT
# An OOP-based simulation of a customs border checkpoint utilizing custom 
# Queue data structures, data filtering, and automated audit logging.
# ==============================================================================

import datetime

class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        else:
            return None  # Або можна кидати виключення

    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    def get_items(self):
        return self.queue

    def createFromList(self, items):
        for item in items:
            self.enqueue(item)




# Список ключів для митних декларацій
listkey = [
    "марка", "номер", "компанія", "дата",
    "походження", "призначення", "товари",
    "вартість", "кількість", "договір перевезення"
]

# Список митних декларацій
declarations = [
    dict(zip(listkey, ["Volvo", "D1093AH", "Clear Floor", datetime.datetime(2024, 1, 15),
                       ("Польща", "Вроцлав"), ("Україна", "Вінниця"), "побутова техніка", 250, 3, True])),

    dict(zip(listkey, ["Toyota", "AA1234BB", "Toyota Japan", datetime.datetime(2024, 2, 20),
                       ("Японія", "Токіо"), ("Україна", "Київ"), "автозапчастини", 1500, 10, False])),

    dict(zip(listkey, ["BMW", "BC5678CD", "TreeGarden", datetime.datetime(2024, 3, 5),
                       ("Німеччина", "Мюнхен"), ("Україна", "Львів"), "меблі", 2000, 5, True])),

    dict(zip(listkey, ["Mercedes", "CD2345EF", "Bosh", datetime.datetime(2024, 4, 10),
                       ("Німеччина", "Штутгарт"), ("Україна", "Одеса"), "електроніка", 3000, 4, True])),

    dict(zip(listkey, ["Audi", "EF3456GH", "Adidas", datetime.datetime(2024, 5, 18),
                       ("США", "Атланта"), ("Україна", "Запоріжжя"), "одяг", 500, 15, True])),

    dict(zip(listkey, ["Peugeot", "GH4567IJ", "Mr.Proper", datetime.datetime(2024, 6, 22),
                       ("Франція", "Париж"), ("Україна", "Харків"), "побутова хімія", 800, 7, True])),

    dict(zip(listkey, ["Skoda", "IJ5678JK", "SunRise", datetime.datetime(2024, 7, 30),
                       ("Чехія", "Млада-Болеслав"), ("Україна", "Дніпро"), "книги", 100, 20, False])),

    dict(zip(listkey, ["Nissan", "JK6789KL", "CocaCola", datetime.datetime(2024, 8, 15),
                       ("Японія", "Осака"), ("Україна", "Суми"), "харчові продукти", 50, 100, True])),

    dict(zip(listkey, ["Kia", "KL7890MN", "ZEROStain", datetime.datetime(2024, 9, 12),
                       ("Південна Корея", "Сеул"), ("Україна", "Миколаїв"), "автохімія", 300, 8, True])),

    dict(zip(listkey, ["Hyundai", "MN8901OP", "JOYkid", datetime.datetime(2024, 10, 2),
                       ("Південна Корея", "Пусан"), ("Україна", "Черкаси"), "дитячі іграшки", 120, 12, True])),

    dict(zip(listkey, ["Fiat", "OP9012QR", "DELL", datetime.datetime(2024, 11, 19),
                       ("Італія", "Турин"), ("Україна", "Луцьк"), "техніка", 900, 6, False])),

    dict(zip(listkey, ["Renault", "QR0123ST", "Woar", datetime.datetime(2024, 12, 25),
                       ("Франція", "Ліон"), ("Україна", "Рівне"), "сантехніка", 400, 9, True])),

    dict(zip(listkey, ["Subaru", "ST1234UV", "StillDesk", datetime.datetime(2024, 3, 1),
                       ("Японія", "Саппоро"), ("Україна", "Полтава"), "меблі", 3500, 2, False])),

    dict(zip(listkey, ["Lexus", "UV2345WX", "RAZOR", datetime.datetime(2024, 4, 3),
                       ("Японія", "Токіо"), ("Україна", "Чернівці"), "електроніка", 2000, 5, True])),
]


class Border:
    def __init__(self, initialQueue):
        self.initialQueue = initialQueue
        self.green_path = Queue()
        self.red_path = Queue()

    def addCarToInspection(self, car):
        if car["from"][0] in ["Росія", "Білорусь"]:
            print("\n Допоміжний список для пункту 1 (інспекція зеленої черги) \n")
            print(f"Автомобіль {car['model']} було відхилено під час провікри через країну походження: {car['from'][0]}")
            return  # Виходимо з методу, якщо автомобіль відхилено
        elif not car["withCarriageContract"]:
            print(f"Автомобіль {car['model']} було відхилено під час провікри через відсутність договору перевезення")
            return  # Виходимо з методу, якщо автомобіль без договору

        # Якщо автомобіль пройшов перевірку, додаємо його до зеленої черги
        self.green_path.enqueue(car)

    def finishInspectionAndCrossBorder(self):
        finished_cars = []
        while not self.green_path.is_empty():
            finished_cars.append(self.green_path.dequeue())
        return finished_cars  # Повертаємо список всіх автомобілів

    def removeCarsWithoutPermit(self):
        removed_cars = []
        # Створюємо тимчасовий список для зберігання автомобілів, які залишаться в черзі
        temp_queue = []

        # Ітеруємо через всі автомобілі в загальній черзі
        while not self.initialQueue.is_empty():
            car = self.initialQueue.dequeue()  # Декюємо автомобіль для перевірки
            if not car["withCarriageContract"]:
                removed_cars.append(car)  # Додаємо авто без договору до списку видалених
            else:
                temp_queue.append(car)  # Зберігаємо авто з договором у тимчасовий список

        # Повертаємо всі автомобілі з тимчасового списку назад в чергу
        for car in temp_queue:
            self.initialQueue.enqueue(car)

        return removed_cars  # Повертаємо список видалених автомобілів

    def listCarsWithGoods(self, goods):
        return [car for car in self.initialQueue.get_items() if car['goods'] == goods]

    def carWithHighestValue(self):
        highest_value = 0
        highest_value_car = None

        for car in self.initialQueue.get_items():  # Використовуємо get_items для загальної черги
            total_value = car['price'] * car['amount']  # Загальна вартість автомобіля
            if total_value > highest_value:
                highest_value = total_value
                highest_value_car = car  # Зберігаємо автомобіль з найбільшою вартістю

        return highest_value_car  # Повертаємо автомобіль з найбільшою вартістю

    def listCarsGoingToOdesa(self):
        return [car for car in self.initialQueue.get_items() if car['to'][1] == 'Одеса']

    def checkForIllegalGoods(self):
        illegal_goods = ['наркотики', 'вибухові речовини']
        return [car for car in self.initialQueue.get_items() if car['goods'] in illegal_goods]

    # Додаткові операції :

    def countCarsInQueue(self, queue):
        return len(queue.get_items())

    def listCarsByCompany(self, company):
        return [car for car in self.initialQueue.get_items() if car['company'] == company]

    def getTotalValueOfCars(self):
        return sum(
            car['price'] * car['amount'] for car in self.initialQueue.get_items())  # Обчислюємо загальну вартість

    def findCarsAboveValue(self, value):
        return [car for car in self.initialQueue.get_items() if car['price'] > value]

    # Метод для переводу авто з декларацій до загальної черги
    def transferDeclarationsToQueue(self, declarations, count):
        added_cars = []
        for i in range(min(count, len(declarations))):
            # Отримуємо декларацію
            declaration = declarations[i]

            # Створюємо автомобіль у потрібному форматі
            car = {
                'model': declaration['марка'],
                'number': declaration['номер'],
                'company': declaration['компанія'],
                'date': declaration['дата'],
                'from': declaration['походження'],
                'to': declaration['призначення'],
                'goods': declaration['товари'],
                'price': declaration['вартість'],
                'amount': declaration['кількість'],
                'withCarriageContract': declaration['договір перевезення']
            }

            # Додаємо автомобіль до черги
            self.initialQueue.enqueue(car)
            added_cars.append(car)

        return added_cars


def printCar(car):
    try:
        return (
            f'{car["model"]} ({car["number"]}):\n'
            f'\t Компанія: {car["company"]}\n'
            f'\t Дата: {car["date"]}\n'
            f'\t Звідки: {car["from"][0]}, {car["from"][1]}\n'
            f'\t Куди: {car["to"][0]}, {car["to"][1]}\n'
            f'\t Товари: {car["goods"]}\n'
            f'\t Вартість одного товару: {car["price"]}\n'
            f'\t Кількість: {car["amount"]}\n'
            f'\t З договором перевезення: {"Так" if car["withCarriageContract"] else "Ні"}\n'
        )
    except KeyError as e:
        return f"Error: Missing key {e} in car dictionary."


def write_protocol_to_file(protocol, filename='protocol.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for record in protocol:
            file.write(f"{record}\n")


def scenario(border, declarations, count):
    protocol = []

    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')
    # 0. Додавання автомобілів з декларацій до початкової черги
    try:
        added_cars = border.transferDeclarationsToQueue(declarations, count)
        # Протоколювання результату
        protocol.append(f'{len(added_cars)} автомобілів додано з декларацій до початкової черги.')

        # Виведення деталей доданих автомобілів
        if added_cars:
            protocol.append("Додані автомобілі:")
            for car in added_cars:
                protocol.append(printCar(car))  # Використання функції printCar для виведення деталей
    except Exception as e:
        protocol.append(f'Помилка при додаванні автомобілів з декларацій: {e}')

    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # Операції митного контролю

    # 1. Додати автомобіль до огляду
    try:
        car_to_inspect1 = border.initialQueue.dequeue()
        if car_to_inspect1:  # Перевірка на None
            border.addCarToInspection(car_to_inspect1)
            protocol.append(f'Автомобіль {car_to_inspect1["model"]} тимчасово додано до огляду в зелену чергу.')
    except Exception as e:
        protocol.append(f'Помилка при додаванні автомобіля до огляду: {e}')

    try:
        car_to_inspect2 = border.initialQueue.dequeue()
        if car_to_inspect2:  # Перевірка на None
            border.addCarToInspection(car_to_inspect2)
            protocol.append(f'Автомобіль {car_to_inspect2["model"]} тимчасово додано до огляду в зелену чергу.')
    except Exception as e:
        protocol.append(f'Помилка при додаванні автомобіля до огляду: {e}')

    try:
        car_to_inspect3 = border.initialQueue.dequeue()
        if car_to_inspect3:  # Перевірка на None
            border.addCarToInspection(car_to_inspect3)
            protocol.append(f'Автомобіль {car_to_inspect3["model"]} тимчасово додано до огляду в зелену чергу.')
    except Exception as e:
        protocol.append(f'Помилка при додаванні автомобіля до огляду: {e}')

    try:
        car_to_inspect4 = border.initialQueue.dequeue()
        if car_to_inspect4:  # Перевірка на None
            border.addCarToInspection(car_to_inspect4)
            protocol.append(f'Автомобіль {car_to_inspect4["model"]} тимчасово додано до огляду в зелену чергу.')
    except Exception as e:
        protocol.append(f'Помилка при додаванні автомобіля до огляду: {e}')

    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # 2.  Завершити огляд та дозволити перетин кордону
    try:
        finished_cars = border.finishInspectionAndCrossBorder()
        if finished_cars:  # Перевірка на непустий список
            for car in finished_cars:
                protocol.append(f'Автомобіль {car["model"]} перетнув кордон.')
        else:
            protocol.append('Немає автомобілів для перетину кордону (всі автомобілі перевірені).')
    except Exception as e:
        protocol.append(f'Помилка при завершенні огляду: {e}')
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')


    # 3. Викреслити автомобіль без дозволу
    try:
        removed_cars = border.removeCarsWithoutPermit()
        if removed_cars:
            protocol.append("Автомобілі без договору перевезення видалені з черги:")
            for car in removed_cars:
                protocol.append(f"{car['model']} ({car['number']})")
        else:
            protocol.append("Немає автомобілів без договору перевезення для видалення.")
    except Exception as e:
        protocol.append(f'Помилка при видаленні автомобілів без договору: {e}')

    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # 4. Скласти перелік автомобілів, що везуть товар "ноутбук"
    cars_with_goods = border.listCarsWithGoods("ноутбук")
    protocol.append(f'Автомобілі, що везуть "ноутбук": {len(cars_with_goods)} автомобілів.')
    protocol.extend([printCar(car) for car in cars_with_goods])
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # 5. Знайти автомобіль з найбільшою вартістю
    highest_value_car = border.carWithHighestValue()  # Виклик без параметрів
    if highest_value_car:
        protocol.append(f'Автомобіль з найбільшою вартістю: {highest_value_car["model"]}.')
        protocol.append(printCar(highest_value_car))
    else:
        protocol.append('Автомобіль з найбільшою вартістю не знайдено у зеленій черзі.')
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # 6. Список автомобілів, що прямують до Одеси
    cars_to_odessa = border.listCarsGoingToOdesa()
    protocol.append(f'Автомобілі, що прямують до Одеси: {len(cars_to_odessa)} автомобілів.')
    protocol.extend([printCar(car) for car in cars_to_odessa])
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # 7. Перевірка на наявність заборонених товарів
    illegal_cars = border.checkForIllegalGoods()
    protocol.append(f'Автомобілі з забороненими товарами: {len(illegal_cars)} автомобілів.')
    protocol.extend([printCar(car) for car in illegal_cars])
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # Нові операції
    # 8. Підрахунок автомобілів у черзі
    total_cars_in_initial_queue = border.countCarsInQueue(border.initialQueue)
    protocol.append(f'Загальна кількість автомобілів у початковій черзі: {total_cars_in_initial_queue} автомобілів.')
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # 9. Список автомобілів за компанією
    cars_by_company = border.listCarsByCompany('Huawei')
    protocol.append(f'Автомобілі компанії Huawei: {len(cars_by_company)} автомобілів.')
    protocol.extend([printCar(car) for car in cars_by_company])
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # 10. Загальна вартість автомобілів у черзі
    total_value = border.getTotalValueOfCars()
    protocol.append(f'Загальна вартість автомобілів у початковій черзі: {total_value} гривень.')
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    # 11. Список автомобілів, що перевищують певну вартість
    expensive_cars = border.findCarsAboveValue(1000)
    protocol.append(f'Автомобілі з вартістю вище 1000 гривень: {len(expensive_cars)} автомобілів.')
    protocol.extend([printCar(car) for car in expensive_cars])
    protocol.append('\n/////////////////////////////////////////////////////////////////////////\n')

    return protocol




def main():
    # Створення початкової черги
    initialQueue = Queue()

    initialQueue.createFromList([
        {
            'model': 'BMW',
            'number': 'BC 1823 АТ',
            'company': 'Huawei',
            'date': datetime.datetime.strptime('04.10.2023', '%d.%m.%Y'),
            'from': ('Росія', 'Москва'),
            'to': ('Україна', 'Одеса'),
            'goods': 'ноутбук',
            'price': 1000,
            'amount': 5,
            'withCarriageContract': True
        },
        {
            'model': 'Mercedes',
            'number': 'AB 3245 BA',
            'company': 'Samsung',
            'date': datetime.datetime.strptime('02.10.2023', '%d.%m.%Y'),
            'from': ('Південна Корея', 'Сеул'),
            'to': ('Україна', 'Одеса'),
            'goods': 'телефон',
            'price': 500,
            'amount': 10,
            'withCarriageContract': True
        },
        {
            'model': 'Audi',
            'number': 'AA 5678 ВК',
            'company': 'Apple',
            'date': datetime.datetime.strptime('01.10.2023', '%d.%m.%Y'),
            'from': ('США', 'Нью-Йорк'),
            'to': ('Україна', 'Одеса'),
            'goods': 'телефон',
            'price': 10000,
            'amount': 10,
            'withCarriageContract': False
        },
        {
            'model': 'Toyota',
            'number': 'AA 1234 BB',
            'company': 'Reverance',
            'date': datetime.datetime.strptime('20.09.2023', '%d.%m.%Y'),
            'from': ('Японія', 'Токіо'),
            'to': ('Україна', 'Київ'),
            'goods': 'вибухові речовини',
            'price': 1500,
            'amount': 10,
            'withCarriageContract': True
        },
        {
            'model': 'Fiat',
            'number': 'XY 7890 CD',
            'company': 'Philips',
            'date': datetime.datetime.strptime('15.09.2023', '%d.%m.%Y'),
            'from': ('Італія', 'Турин'),
            'to': ('Україна', 'Львів'),
            'goods': 'техніка',
            'price': 1200,
            'amount': 3,
            'withCarriageContract': False
        },
        {
            'model': 'Nissan',
            'number': 'JK 6789 KL',
            'company': 'Nestle',
            'date': datetime.datetime.strptime('05.09.2023', '%d.%m.%Y'),
            'from': ('США', 'Нью-Йорк'),
            'to': ('Україна', 'Харків'),
            'goods': 'харчові продукти',
            'price': 600,
            'amount': 20,
            'withCarriageContract': True
        },
        {
            'model': 'Peugeot',
            'number': 'GH 4567 IJ',
            'company': 'Dr.Broom',
            'date': datetime.datetime.strptime('10.08.2023', '%d.%m.%Y'),
            'from': ('Франція', 'Париж'),
            'to': ('Україна', 'Одеса'),
            'goods': 'побутова хімія',
            'price': 800,
            'amount': 5,
            'withCarriageContract': True
        },
        {
            'model': 'Hyundai',
            'number': 'MN 8901 OP',
            'company': 'BookiToy',
            'date': datetime.datetime.strptime('02.09.2023', '%d.%m.%Y'),
            'from': ('Південна Корея', 'Пусан'),
            'to': ('Україна', 'Черкаси'),
            'goods': 'дитячі іграшки',
            'price': 120,
            'amount': 12,
            'withCarriageContract': True
        },
        {
            'model': 'Subaru',
            'number': 'ST 1234 UV',
            'company': 'SolidOak',
            'date': datetime.datetime.strptime('15.08.2023', '%d.%m.%Y'),
            'from': ('Японія', 'Саппоро'),
            'to': ('Україна', 'Полтава'),
            'goods': 'меблі',
            'price': 3500,
            'amount': 2,
            'withCarriageContract': False
        },
        {
            'model': 'BMW',
            'number': 'BC 1823 АТ',
            'company': 'Huawei',
            'date': datetime.datetime.strptime('04.10.2023', '%d.%m.%Y'),
            'from': ('Польща', 'Краків'),
            'to': ('Україна', 'Львів'),
            'goods': 'телефон',
            'price': 2500,
            'amount': 5,
            'withCarriageContract': True
        },
        {
            'model': 'BMW',
            'number': 'XP 584NK',
            'company': 'BetterSilver',
            'date': datetime.datetime.strptime('23.09.2023', '%d.%m.%Y'),
            'from': ('Італія', 'Венеція'),
            'to': ('Україна', 'Житомир'),
            'goods': 'наркотики',
            'price': 3000,
            'amount': 5,
            'withCarriageContract': False
        },
        {
            'model': 'Volvo',
            'number': 'RD ZS 120',
            'company': 'Рошен',
            'date': datetime.datetime.strptime('01.10.2023', '%d.%m.%Y'),
            'from': ('Німеччина', 'Гамбург'),
            'to': ('Україна', 'Ужгород'),
            'goods': 'солодощі',
            'price': 100,
            'amount': 12,
            'withCarriageContract': False
        },
        {
            'model': 'Nissan',
            'number': 'CZ 007NF',
            'company': 'SilverLine',
            'date': datetime.datetime.strptime('29.09.2023', '%d.%m.%Y'),
            'from': ('Італія', 'Мілан'),
            'to': ('Україна', 'Чернівці'),
            'goods': 'прикраса',
            'price': 10000,
            'amount': 8,
            'withCarriageContract': True
        },
        {
            'model': 'Toyota',
            'number': 'OK TE 749',
            'company': 'Honor',
            'date': datetime.datetime.strptime('05.10.2023', '%d.%m.%Y'),
            'from': ('Німеччина', 'Берлін'),
            'to': ('Україна', 'Київ'),
            'goods': 'ноутбук',
            'price': 3800,
            'amount': 16,
            'withCarriageContract': True
        },
        {
            'model': 'Skoda',
            'number': '3R6 9710',
            'company': 'KOBI',
            'date': datetime.datetime.strptime('01.10.2023', '%d.%m.%Y'),
            'from': ('Чехія', 'Брно'),
            'to': ('Україна', 'Херсон'),
            'goods': 'вибухові речовини',
            'price': 3000,
            'amount': 25,
            'withCarriageContract': True
        },
        {
            'model': 'Renault',
            'number': 'OKT 63RA',
            'company': 'Gorenje',
            'date': datetime.datetime.strptime('15.09.2023', '%d.%m.%Y'),
            'from': ('Польща', 'Лодзь'),
            'to': ('Україна', 'Київ'),
            'goods': 'наркотики',
            'price': 15000,
            'amount': 3,
            'withCarriageContract': True
        },
        {
            'model': 'Audi',
            'number': 'ERA 75TM',
            'company': 'HP',
            'date': datetime.datetime.strptime('27.09.2023', '%d.%m.%Y'),
            'from': ('Польща', 'Ярослав'),
            'to': ('Україна', 'Хмельницький'),
            'goods': 'ноутбук',
            'price': 2500,
            'amount': 2,
            'withCarriageContract': False
        },
        {
            'model': 'Volvo',
            'number': 'ZH 445789',
            'company': 'Apple',
            'date': datetime.datetime.strptime('28.09.2023', '%d.%m.%Y'),
            'from': ('Швейцарія', 'Цюрих'),
            'to': ('Україна', 'Київ'),
            'goods': 'телефон',
            'price': 4000,
            'amount': 12,
            'withCarriageContract': True
        },
        {
            'model': 'Nissan',
            'number': '1A2 3000',
            'company': 'Bosch',
            'date': datetime.datetime.strptime('04.10.2023', '%d.%m.%Y'),
            'from': ('Чехія', 'Прага'),
            'to': ('Україна', 'Черкаси'),
            'goods': 'мікрохвильовка',
            'price': 2600,
            'amount': 1,
            'withCarriageContract': False
        },
        {
            'model': 'Opel',
            'number': 'PO 567841',
            'company': 'Gorenje',
            'date': datetime.datetime.strptime('05.10.2023', '%d.%m.%Y'),
            'from': ('Швейцарія', 'Женева'),
            'to': ('Україна', 'Харків'),
            'goods': 'наркотики',
            'price': 6000,
            'amount': 1,
            'withCarriageContract': False
        },
        {
            'model': 'Audi',
            'number': 'E 77 PKW',
            'company': 'Lenovo',
            'date': datetime.datetime.strptime('24.09.2023', '%d.%m.%Y'),
            'from': ('Румунія', 'Бухарест'),
            'to': ('Україна', 'Запоріжжя'),
            'goods': 'планшет',
            'price': 2300,
            'amount': 15,
            'withCarriageContract': True
        }
    ])

    border = Border(initialQueue)

    count = 2  # кількість автомобілів для переведення з декларацій

    protocol = scenario(border, declarations, count)

    # Write the protocol to a text file
    write_protocol_to_file(protocol)

    # Output the protocol to console
    print("\nПротокол операцій митного контролю:")
    for record in protocol:
        print(record)


if __name__ == '__main__':
    main()
