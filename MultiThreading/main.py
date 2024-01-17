#! venv/bin/python
from concurrent.futures import ThreadPoolExecutor
import time


def do(name: str) -> None:
    print(f"hello {name}")
    time.sleep(2)
    print(f"servas {name}")


def main() -> None:
    pool = ThreadPoolExecutor(max_workers=2)
    res = pool.map(do, ("seppl", "josefine"))

    pool.shutdown(wait=True)


if __name__ == "__main__":
    main()
