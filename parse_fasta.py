import os
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, TextIO, List, Iterator


@dataclass 
class Sequence():       # Создали класс для хранения последовательностей
    sequence: str
    header: str



@dataclass          # Создали класс для хранения генома
class Genome:
    sequences: List[Sequence] = field(default_factory=list)

    def add_sequence(self, sequence: Sequence):
        self.sequences.append(sequence)

    def get_sequence_by_header(self, header: str) -> Optional[Sequence]:
        for seq in self.sequences:
            if seq.header == header:
                return seq
        return None

    def __len__(self):
        return len(self.sequences)

    def __iter__(self):
        return iter(self.sequences)



class SequenceParser(ABC):      # Создаем абстракный класс, который нужен для других. Его нельзя вызывать отдельно
    def __init__(self, file_path: str | os.PathLike):
        self.file_path = Path(file_path)
        self._handle: Optional[TextIO] = None

    def __enter__(self):
        self._handle = self.file_path.open("r")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._handle:
            self._handle.close()

    def __iter__(self):
        return self

    # @abstractmethod
    # def __next__(self):         # Этот метод мы реализовали в ReadsParser
    #     """Читает и возвращает следующий Sequence.
    #     Должен быть реализован в подклассах."""
    #     pass



class GenomeParser(SequenceParser):
    def __init__(self, file_path):
        super().__init__(file_path)


    def parse(self) -> Genome:
        genome = Genome()
        current_header = None
        current_seq_lines = []

        with self.file_path.open("r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line.startswith(">"):
                    if current_header is not None:
                        sequence_str = "".join(current_seq_lines)
                        genome.add_sequence(Sequence(header=current_header,
                                                     sequence=sequence_str))

                    current_header = line[1:].strip()
                    current_seq_lines = []
                else:
                    current_seq_lines.append(line)

            # добавим последнюю запись
            if current_header is not None:
                sequence_str = "".join(current_seq_lines)
                genome.add_sequence(Sequence(header=current_header, sequence=sequence_str))

        return genome


class ReadsParser(SequenceParser):
    def __iter__(self) -> Iterator[Sequence]:
        if self._handle is None:
            raise ValueError("File is not open. Use 'with' statement.")

        header: Optional[str] = None
        seq_lines: list[str] = []

        for line in self._handle:
            line = line.strip()
            if not line:
                continue  # пропускаем пустые строки

            if line.startswith(">"):
                if header is not None:
                    # Вернуть предыдущую последовательность
                    yield Sequence(header=header, sequence="".join(seq_lines))
                header = line[1:]  # убираем символ ">"
                seq_lines = []
            else:
                seq_lines.append(line)

        # вернуть последнюю последовательность
        if header is not None and seq_lines:
            yield Sequence(header=header, sequence="".join(seq_lines))
