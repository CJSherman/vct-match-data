# checks if a choice was an acceptable option
def choice_check(question: str, options: list[str | int]) -> str:
    while True:
        choice = input(question).lower()
        if choice in str(options) and len(choice) > 0:
            break

    return choice


# checks if data is valid
def data_check(question: str, options: list[str], data: str) -> str:
    while data not in options:
        data = input(question).upper()
    return data


# checks if an expected integer input is an integer
def int_input(quantity: str, result=None) -> int:
    msg = "Please Enter an Integer Value For " + quantity + "\n"
    if not result:
        result = input(msg)
    while True:
        try:
            result = int(result)
            break
        except ValueError:
            result = input(msg)
    return result


# divides 2 numbers, returning 0 if denominator is 0
def divide(numerator: int, denominator: int, offset=0) -> float:
    try:
        result = numerator / denominator + offset
    except ZeroDivisionError:
        result = 0
    return result
