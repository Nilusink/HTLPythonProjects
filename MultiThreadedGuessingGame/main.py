#! venv/bin/python
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import typing as tp


def read_and_split_file(
        fname: str,
        n: int,
        encoding: str = "utf-8"
) -> tp.Generator[list[str]]:
    """
    Read a file and split it in n equal length parts
    (by line)
    """
    # get number of lines
    with open(fname, "rb") as f:
        num_lines = sum(1 for _ in f)

        lines_per_part = num_lines // n + 1

        current_lines = []
        for i in f:
            current_lines.append(i.decode(encoding))

            if i % lines_per_part == 0:
                yield current_lines

                current_lines = []


parts = list(read_and_split_file("./"))