#!/usr/bin/env python3

import abc
from typing import Any, Union, Protocol

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




class ExportPlugin(Protocol):
    def process_output(self, data: list[tuple[int, str]]) -> None:
        pass


class CSVPlugin:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        print("CSV Output:")
        values = [val for rank, val in data]
        print(",".join(values))


class JSONPlugin:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        print("JSON Output:")
        json_parts = [f'"item_{rank}": "{val}"' for rank, val in data]
        json_string = "{" + ", ".join(json_parts) + "}"
        print(json_string)

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

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        for proc in self._procs:
            extracted_data: list[tuple[int, str]] = []
            for _ in range(nb):
                try:
                    extracted_data.append(proc.output())
                except IndexError:
                    break
            
            if extracted_data:
                plugin.process_output(extracted_data)   



if __name__ == "__main__":
    print("=== Code Nexus - Data Pipeline ===\n")
    print("Initialize Data Stream...\n")
    ds = DataStream()
    ds.print_processors_stats()
    print()

    print("Registering Processors\n")
    np = NumericProcessor()
    tp = TextProcessor()
    lp = LogProcessor()
    ds.register_processor(np)
    ds.register_processor(tp)
    ds.register_processor(lp)

    batch_data = [
        'Hello world', 
        [3.14, -1, 2.71], 
        [{'log_level': 'WARNING', 'log_message': 'Telnet access! Use ssh instead'}, 
         {'log_level': 'INFO', 'log_message': 'User wil is connected'}], 
        42, 
        ['Hi', 'five']
    ]

    print(f"Send first batch of data on stream: {batch_data}\n")
    ds.process_stream(batch_data)
    ds.print_processors_stats()

    print("Send 3 processed data from each processor to a CSV plugin:")
    csv_plugin = CSVPlugin()
    ds.output_pipeline(3, csv_plugin)
    ds.print_processors_stats()
    print()

    batch_2 = [
        21, 
        ['I love AI', 'LLMs are wonderful', 'Stay healthy'], 
        [{'log_level': 'ERROR', 'log_message': '500 server crash'}, 
         {'log_level': 'NOTICE', 'log_message': 'Certificate expires in 10 days'}], 
        [32, 42, 64, 84, 128, 168], 
        'World hello'
    ]

    print(f"Send another batch of data: {batch_2}\n")
    ds.process_stream(batch_2)
    ds.print_processors_stats()
    print()

    print("Send 5 processed data from each processor to a JSON plugin:")
    json_plugin = JSONPlugin()
    ds.output_pipeline(5, json_plugin)
    ds.print_processors_stats()

