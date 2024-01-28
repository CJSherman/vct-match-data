# checks if a choice was an acceptable option
def choice_check(question: str, options: list[str | int]) -> str:
    """Function to check if an input is in a given set.

    Parameters
    ----------
    question : str
    options : list[str | int]

    Returns
    -------
    str
        The Result."""

    while True:
        choice = input(question).lower()
        if choice in str(options) and len(choice) > 0:
            break

    return choice


# checks if data is valid
def data_check(question: str, options: list[str], data: str) -> str:
    """Function to check if an input is in a given set.

    Parameters
    ----------
    question : str
    options : list[str]
    data : str
        The initial input.

    Returns
    -------
    str
        The Result."""

    while data not in options:
        data = input(question).upper()
    return data


# checks if an expected integer input is an integer
def int_input(quantity: str, result=None) -> int:
    """Function to confirm an input is an integer.

    Parameter
    ---------
    quantity : str
        The question to be asked.
    result
        The current given answer.

    Returns
    -------
    int
        The answer to the question."""

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
    """Function to divide two values and return 0 if the denominator is 0 (e.g. K/D for 10/0 is 10).

    Parameters
    ----------
    numerator : int
    denominator : int
    offset : float, default: 0
        How much to shift the result by.

    Returns
    -------
    result : float"""

    try:
        result = numerator / denominator + offset
    except ZeroDivisionError:
        result = 0
    return result
