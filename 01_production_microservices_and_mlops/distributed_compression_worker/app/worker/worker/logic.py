import math
from decimal import Decimal, getcontext
from crud.crud_functions import get_task_by_id
from dependencies import get_db


class ArithmeticEncoder:
    def __init__(self, symbol_probabilities):
        self.symbol_probabilities = symbol_probabilities

    def encode(self, data, task_id):
        low = Decimal(0.0)
        high = Decimal(1.0)

        prec = math.ceil(len(data) * len(self.symbol_probabilities.keys()) * 0.13)
        if prec < 10000000000:
            getcontext().prec = prec
        else:
            getcontext().prec = 10000000000

        check = len(data)
        step = int(check / 100)

        if step <= 0:
            step = 1
        counter = 0
        for symbol in data:
            symbol_range = Decimal(high - low)
            high = low + symbol_range * self.symbol_probabilities[symbol][1]
            low = low + symbol_range * self.symbol_probabilities[symbol][0]

            counter += 1

            if counter % step == 0:
                db = next(get_db())
                task = get_task_by_id(task_id=task_id, db=db)
                task.percentage = int(counter / step) if int(counter / step) < 100 else 100
                db.commit()

                if task.status == "Cancelled":
                    db.close()
                    return 0

                db.close()

        result = (low + high) / Decimal(2.0)

        return result


class ArithmeticDecoder:
    def __init__(self, symbol_probabilities):
        self.symbol_probabilities = symbol_probabilities

    def decode(self, encoded_data, length):
        low = Decimal(0.0)
        high = Decimal(1.0)
        result = ""

        for _ in range(length):
            for symbol, (symbol_low, symbol_high) in self.symbol_probabilities.items():

                symbol_range = high - low
                symbol_low_in_range = Decimal(symbol_low) * symbol_range
                symbol_high_in_range = Decimal(symbol_high) * symbol_range

                if low + symbol_low_in_range <= encoded_data <= low + symbol_high_in_range:
                    result += symbol
                    high = low + symbol_range * symbol_high
                    low = low + symbol_range * symbol_low
                    break

        return result


def encode(string: str, task_id: int):
    letter_probabilities = {}

    for letter in string:
        if letter in letter_probabilities:
            letter_probabilities[letter] += 1
        else:
            letter_probabilities[letter] = 1

    letter_probabilities = dict(sorted(letter_probabilities.items(), key=lambda item: item[1], reverse=True))

    total_length = len(string)
    probabilities = {}
    low_range = Decimal(0.0)

    for letter, frequency in letter_probabilities.items():
        high_range = low_range + Decimal(frequency) / Decimal(total_length)
        probabilities[letter] = [low_range, high_range]
        low_range = Decimal(high_range)

    coder = ArithmeticEncoder(probabilities)
    result = {
        "code": str(coder.encode(string, task_id)),
        "probabilities": {key: str([float(num) for num in value]) for key, value in probabilities.items()},
        "length": len(string)
    }
    return result


def decode(number: float, length: int, probabilities: dict) -> str:
    decoder = ArithmeticDecoder(probabilities)

    return decoder.decode(number, length)


