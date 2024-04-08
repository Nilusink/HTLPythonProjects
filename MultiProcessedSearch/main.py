#! venv/bin/python
"""
main.py
11. January 2024

Finds all occurrences of a string in the fastest way possible

Author:
Nilusink
"""
from concurrent.futures import ProcessPoolExecutor, Future
from progress.bar import ShadyBar
from dataclasses import dataclass
from time import perf_counter
import sys
import os


# if executed on windows, enable terminal colors
if sys.platform == "win32":
    os.system("color")


# define console colors
CLR_RESET = "\033[1;0m"
STL_BOLD = "\033[1;1m"
CLR_RED = "\033[0;31m"
CLR_GREEN = "\033[0;32m"
CLR_BLUE = "\033[0;34m"


def auto_pad(number: int) -> str:
    """
    Automatically scale numbers and add k, m, G, T and P
    """
    n_unit = 0
    units = ["", "k", "m", "G", "T", "P"]

    while number >= 1024:
        number /= 1024
        n_unit += 1

    return f"{number:.2f}{units[n_unit]}"


# dataclasses
@dataclass(frozen=True)
class Occurrence:
    start: int
    term: str
    in_sentence: str

    @property
    def length(self) -> int:
        return len(self.term)

    def __str__(self) -> str:
        first_part = self.in_sentence[:self.in_sentence.find(self.term)]
        second_part = self.in_sentence[
            self.in_sentence.find(self.term) + len(self.term):
        ]
        return f"{first_part}{CLR_GREEN}{self.term}{CLR_RESET}{second_part}"

    def __repr__(self) -> str:
        return f"({self.start}: \"{self.__str__()}\")"


@dataclass(frozen=True)
class PartialOccurrence(Occurrence):
    partial_term: str
    start_end: bool  # false = start, true = end

    def __str__(self) -> str:
        first_part = self.in_sentence[:self.in_sentence.find(self.term)]
        second_part = self.in_sentence[
            self.in_sentence.find(self.term) + len(self.term):
        ]
        return (
            f"{first_part}"
            f"{CLR_GREEN}{self.partial_term}{CLR_RESET}"
            f"{second_part}"
        )


def call_with_extend(args):
    return args[0](*args[1:])


# main class
class FastFinder:
    def __init__(
            self,
            file_path: str,
            n_processes: int = -1,
            max_size_per_process: int = 1024**2
    ) -> None:
        """
        :param file_path: file to search
        :param n_processes: how many processes to use. defaults to n of cpus
        :param max_size_per_process: maximum section size per process.
            defaults to 1m
        """
        self._file_path = file_path
        self.n_processes = n_processes
        self.max_size_per_process = max_size_per_process

        if self.n_processes <= 0:
            self.n_processes = os.cpu_count()

    @staticmethod
    def _find_section(
            file_path: str,
            start: int,
            end: int,
            term: str,
            n_padding: int = 5
    ) -> tuple[list[Occurrence], list[PartialOccurrence]]:
        """
        search a specific section in the file
        """
        with open(file_path, "r") as inp:
            inp.seek(start)
            section = inp.read(end - start)

        # find partial occurrences
        partials: list[PartialOccurrence] = []
        first_part = section[:len(term)-2]
        last_part = section[-len(term)+1:]

        for i in range(len(term)):
            if first_part.startswith(term[i:]):
                word_start = start-i
                partials.append(PartialOccurrence(
                    word_start,
                    term,
                    section[:len(term) + n_padding],
                    term[i:],
                    False
                ))
                break

        for i in range(len(last_part)):
            if term.startswith(last_part[i:]):
                word_start = end - (len(last_part) - i)

                partials.append(PartialOccurrence(
                    word_start,
                    term,
                    section[
                        -n_padding - len(last_part[:i]) - 1:
                        -len(last_part[:i]) - 1
                    ],
                    last_part[i:],
                    True
                ))
                break

        # find full terms
        start_index = 0
        found: list[Occurrence] = []
        for _ in range(len(section)):
            i_found = section.find(term, start_index)

            if i_found == -1:
                break

            found.append(Occurrence(
                start + start_index,
                term,
                section[
                    max(0, i_found - n_padding):i_found + len(term) + n_padding
                ]
            ))

            start_index = i_found + 1

        return found, partials

    def find(self, term: str, n_padding: int = 5) -> None:
        """
        find a term in the file
        """
        start_t = perf_counter()

        file_size = os.path.getsize(self._file_path)
        n_characters = file_size

        n_processes = n_characters // self.max_size_per_process + 1

        # statistics before search
        print(
            f"{auto_pad(n_characters)} characters, "
            f"{auto_pad(self.max_size_per_process)} "
            f"per process, {n_processes} processes"
        )

        # start processes
        processes: list[Future] = []
        with ProcessPoolExecutor(max_workers=self.n_processes) as pool:
            if n_processes > 100:
                bar_size = n_processes
                bar_hops = 1

                while bar_size > 1000:
                    bar_size /= 100
                    bar_hops *= 100

                bar_size = int(bar_size)
            bar = ShadyBar(
                "Starting ",
                max=bar_size,
                width=100,
                suffix='%(percent)d%% - eta: %(eta)ds'
            )
            bar.start()
            bar.next()
            process_end = 0
            process_parts = []
            for i_process in range(n_processes - 1):
                # calculate section range
                process_start = i_process * self.max_size_per_process
                process_end = (i_process + 1) * self.max_size_per_process

                # start process
                process_parts.append((
                    self._find_section,
                    self._file_path,
                    process_start,
                    process_end,
                    term,
                    n_padding,
                ))

                if i_process % bar_hops == 0:
                    bar.next()
            bar.finish()



            # start last process (to end)
            process_parts.append((
                self._find_section,
                self._file_path,
                process_end,
                n_characters,
                term,
                n_padding,
            ))

            # wait for processes to finish and show progress bar
            bar = ShadyBar(
                'Searching',
                max=bar_size,
                width=100,
                suffix='%(percent)d%% - eta: %(eta)ds'
            )
            bar.start()

            i_result = 0
            results: list[Occurrence] = []
            partial_results_end: list[PartialOccurrence] = []
            partial_results_start: list[PartialOccurrence] = []
            for matches, partial_matches in pool.map(call_with_extend, process_parts):
                results.extend(matches)

                # append partial matches to the correct list
                partial_matches: list[PartialOccurrence]
                for match in partial_matches:
                    if match.start_end:
                        partial_results_end.append(match)
                        continue

                    partial_results_start.append(match)

                # iterate progress bar
                if i_result % bar_hops == 0:
                    bar.next()

                i_result += 1

            bar.finish()

        # parse partial results
        for start in partial_results_start:
            for end in partial_results_end:
                if all([
                    start.start == end.start,
                    start.term == end.term
                ]):
                    results.append(Occurrence(
                        start=start.start,
                        term=start.term,
                        in_sentence=start.in_sentence + term + end.in_sentence
                    ))
                    break  # find match for next word

        time_total = perf_counter() - start_t

        # show results
        print(f"\nresults (took {round(time_total, 2)}s):")
        if len(results) > 50:
            if input(f"show {len(results)} results (y/n)? ").lower() != "y":
                return

        for i, result in enumerate(results):
            print(
                f"  {i:04} Character {CLR_BLUE}{auto_pad(result.start)}"
                f"{CLR_RESET} ({result.start}): {str(result)}"
            )


def main() -> None:
    ff = FastFinder(
        sys.argv[2],
        n_processes=-1,
        max_size_per_process=5_000_000
    )
    ff.find(sys.argv[1])


if __name__ == "__main__":
    main()
