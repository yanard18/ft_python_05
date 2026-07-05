#!/usr/bin/env python3

import abc
from typing import Any, Union

class DataProcessor(abc.ABC):
    
    def __init__(self) -> None:
        self._storage: list[tuple[int, str]] = []
        self._current_rank: int = 0

    @abc.abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abc.abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        if not self._storage:
            raise IndexError("No data left to output.")
        return self._storage.pop(0)


class NumericProcessor(DataProcessor):
    
    def validate(self, data: Any) -> bool:
        if isinstance(data, (int, float)) and not isinstance(data, bool):
            return True
        if isinstance(data, list):
            return all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in data)
        return False

    def ingest(self, data: Union[int, float, list[Union[int, float]]]) -> None:
        if not self.validate(data):
            raise ValueError("Improper numeric data")
        
        items = data if isinstance(data, list) else [data]
        for item in items:
            self._storage.append((self._current_rank, str(item)))
            self._current_rank += 1


class TextProcessor(DataProcessor):
    
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True
        if isinstance(data, list):
            return all(isinstance(x, str) for x in data)
        return False

    def ingest(self, data: Union[str, list[str]]) -> None:
        if not self.validate(data):
            raise ValueError("Improper text data")
        
        items = data if isinstance(data, list) else [data]
        for item in items:
            self._storage.append((self._current_rank, item))
            self._current_rank += 1


class LogProcessor(DataProcessor):
    
    def validate(self, data: Any) -> bool:
        def is_valid_dict(d: Any) -> bool:
            if not isinstance(d, dict):
                return False
            return all(isinstance(k, str) and isinstance(v, str) for k, v in d.items())

        if is_valid_dict(data):
            return True
        if isinstance(data, list):
            return all(isinstance(x, dict) and is_valid_dict(x) for x in data)
        return False

    def ingest(self, data: Union[dict[str, str], list[dict[str, str]]]) -> None:
        if not self.validate(data):
            raise ValueError("Improper log data")
        
        items = data if isinstance(data, list) else [data]
        for item in items:
            formatted_string = ": ".join(item.values())
            self._storage.append((self._current_rank, formatted_string))
            self._current_rank += 1


class DataStream:

    def __init__(self) -> None:
        self._procs: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self._procs.append(proc)

    def process_stream(self, stream: list[Any]) -> None:
        for item in stream:
            processed = False
            for proc in self._procs:
                if proc.validate(item):
                    proc.ingest(item)
                    processed = True
                    break
            
            if not processed:
                print(f"DataStream error - Can't process element in stream: {item}")

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")
        if not self._procs:
            print("No processor found, no data")
        else:
            for proc in self._procs:
                name = proc.__class__.__name__.replace("Processor", " Processor")
                total = proc._current_rank
                remaining = len(proc._storage)
                print(f"{name}: total {total} items processed, remaining {remaining} on processor")


if __name__ == "__main__":
    print("=== Code Nexus - Data Stream ===\n")
    print("Initialize Data Stream...")
    ds = DataStream()
    ds.print_processors_stats()
    print()

    print("Registering Numeric Processor\n")
    np = NumericProcessor()
    ds.register_processor(np)

    batch_data = [
        'Hello world',
        [3.14, -1, 2.71],
        [{'log_level': 'WARNING', 'log_message': 'Telnet access! Use ssh instead'},
         {'log_level': 'INFO', 'log_message': 'User wil is connected'}],
        42,
        ['Hi', 'five']
    ]

    print(f"Send first batch of data on stream: {batch_data}")
    ds.process_stream(batch_data)
    ds.print_processors_stats()
    print()

    print("Registering other data processors")
    tp = TextProcessor()
    lp = LogProcessor()
    ds.register_processor(tp)
    ds.register_processor(lp)

    print("Send the same batch again")
    ds.process_stream(batch_data)
    ds.print_processors_stats()

    print("Consume some elements from the data processors: Numeric 3, Text 2, Log 1")
    for _ in range(3):
        np.output()
    for _ in range(2):
        tp.output()
    for _ in range(1):
        lp.output()

    ds.print_processors_stats()
