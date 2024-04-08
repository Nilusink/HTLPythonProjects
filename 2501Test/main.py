"""
main.py
25. January 2024

Uses distributed work do calculate a series of squares
(needs python 3.12 to work)

Author:
Nilusink
"""
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter
import typing as tp


def ask_with_constraint[T](
    text: str,
    on_error: str,
    value_type: tp.Type[T],
    constraint: tp.Callable[[T], bool]
) -> T:
    """
    fancy user input
    """
    while True:
        value = input(text)

        # try to convert the value
        try:
            converted_value = value_type(value)

        except Exception:
            print(on_error)
            continue

        # check for constraint
        if not constraint(converted_value):
            print(on_error)
            continue

        # value correct, return
        return converted_value


def calculate_squares(numbers: list[float]) -> tuple[list[float]]:
    """
    [single process] calculates the square for each given number

    :param numbers: the numbers to square
    :returns: (input numbers, calculated squares)
    """
    out = []
    for num in numbers:
        out.append(num**2)

    return numbers, out


def main() -> int:
    """
    main function
    """
    # user input
    start = ask_with_constraint(
        "start value: ",
        "please enter a number!",
        int,
        lambda *_: True
    )
    end = ask_with_constraint(
        "end value: ",
        f"pleaes enter a number higher than {start}!",
        int,
        lambda v: v > start
    )
    n_processes = ask_with_constraint(
        "number of processes: ",
        "please enter a number higher than 0!",
        int,
        lambda v: v > 0
    )

    # start timer
    start_time = perf_counter()

    # distribute data
    nums = list(range(start, end+1))

    per_process = (end-start) // n_processes

    process_parts = [
        nums[per_process*i:per_process*(i+1)] for i in range(n_processes-1)
    ]

    # assign whatever is left to the last process
    process_parts.append(nums[(n_processes-1) * per_process:])

    # create thread pool
    pool = ProcessPoolExecutor(max_workers=n_processes)

    # start processes and ppend results to square_per_number
    square_per_number: list[tuple[int, int]] = []
    for result in pool.map(calculate_squares, process_parts):
        for number, square in zip(*result):
            square_per_number.append((number, square))

    # stop timer
    end_time = perf_counter()

    # print result
    print(f"\ntook {round(end_time - start_time, 2)}s")

    ans = ask_with_constraint(
        f"Show {len(square_per_number)} results (y/n)? ",
        "please enter either \"y\" or \"n\"",
        str,
        lambda v: v.lower() in ("y", "n", "yes", "no")
    )

    if ans.lower() in ("y", "yes"):
        for number, square in square_per_number:
            print(f" {number}^2 = {square}")

    return 0


if __name__ == "__main__":
    exit(main())
