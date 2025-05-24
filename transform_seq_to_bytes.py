from typing import Optional


class BytesSeq:
    """A class for compact storage and manipulation of DNA sequences.

    This class provides efficient storage of DNA sequences by encoding each nucleotide
    ('a', 'c', 'g', 't') into 2 bits and packing them into bytes (4 nucleotides per byte).
    The class supports encoding, decoding and accessing the compressed sequence.

    Attributes:
        encode_mask (dict): A dictionary mapping nucleotides to their 2-bit codes.
        decode_mask (dict): A dictionary mapping 2-bit codes back to nucleotides.
        bytes_seq (bytearray): The compressed byte sequence storing the DNA data.
        seq_length (int): The length of the original DNA sequence.
    """

    encode_mask: dict
    decode_mask: dict
    bytes_seq: bytearray
    seq_length: int
    # sequence: str
    # Мы решили не использовать атрибут sequence, чтобы избежать
    # использования лишней памяти. У класса реализован метод,
    # позволяющий налету декодировать битовую последовательность в строку

    def __init__(self, sequence: str, encode_mask: Optional[dict] = None):
        self.bytes_seq = bytearray()
        if encode_mask is None:
            # self.encode_mask = {"a": 0b00, "c": 0b01, "g": 0b10, "t": 0b11}
            self.encode_mask = self.encode_mask = {
                                            "a": 0b000,  # 0
                                            "c": 0b001,  # 1
                                            "g": 0b010,  # 2
                                            "t": 0b011,  # 3
                                            "n": 0b100,  # 4
                                            "$": 0b101,  # 5 терминатор
                                        }
        self.decode_mask = {v: k for k, v in self.encode_mask.items()}

        # for i in range(0, len(sequence), 4):
        #     chunk = sequence.lower()[i:i+4]
        #     byte = 0
        #     for j, ch in enumerate(chunk):
        #         byte |= self.encode_mask[ch] << (6 - 2 * j)
        #     self.bytes_seq.append(byte)
        sequence = sequence.lower()
        self.seq_length = len(sequence)
        i = 0  # Индекс текущего положения в последовательности
        pad_value = self.encode_mask["$"]  # для щаполенения в случае нечетности последовательности
        # В цикле будем перескакивать через 4 символа за раз. Смотрим пачками по 4 буквы
        # Пришлось использовать while и прыжки через 4, чтобы избавиться от срезов
        while i < self.seq_length:
            byte = 0  # Инициализируем новый байт для 2 букв
            # в этом подцикле записываем 2 буквы в один байт
            for j in range(2):
                if i + j < self.seq_length:
                    ch = sequence[i + j]
                    code = self.encode_mask[ch]
                else:
                    code = pad_value
                shift = 5 - 3 * j  # для j=0 сдвиг 5 (биты 7-5), для j=1 сдвиг 2 (биты 4-2)
                byte |= code << shift
            self.bytes_seq.append(byte)
            i += 2

    def get_bytes_seq(self) -> bytearray:
        return self.bytes_seq

    def transform_to_seq(self) -> str:
        # decoded_seq = []
        # for byte in self.bytes_seq:
        #     for shift in (6, 4, 2, 0):
        #         decoded_seq.append(self.decode_mask[(byte >> shift) & 0b11])
        # return ''.join(decoded_seq)

        decoded_seq = []
        for idx in range(self.seq_length):
            byte_index = idx // 2
            bit_offset = 5 - 3 * (idx % 2)
            byte = self.bytes_seq[byte_index]
            code = (byte >> bit_offset) & 0b111  # теперь 3 бита
            decoded_seq.append(self.decode_mask[code])
        return "".join(decoded_seq)

    def __len__(self) -> int:
        return self.seq_length

    def __getitem__(self, index: int | slice) -> bytes | bytearray:
        if isinstance(index, int):
            if index < 0:
                index += self.seq_length
            if index < 0 or index >= self.seq_length:
                raise IndexError("Index out of range")
            byte_index = index // 2
            bit_offset = 5 - 3 * (index % 2)
            byte = self.bytes_seq[byte_index]
            code = (byte >> bit_offset) & 0b111
            return code

        elif isinstance(index, slice):      # реализуем поддержку слайсов
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else self.seq_length
            step = index.step if index.step is not None else 1

            # поддержка отрицательных индексов
            if start < 0:
                start += self.seq_length
            if stop < 0:
                stop += self.seq_length

            # явная проверка на выход за границы
            if not (0 <= start <= self.seq_length):
                raise IndexError("Index out of range")
            if not (0 <= stop <= self.seq_length):
                raise IndexError("Index out of range")
            if step == 0:
                raise ValueError("Index out of range")
            result = []
            for idx in range(start, stop, step):
                result.append(self[idx])     # рекурсивно вызываем __getitem__ для int
            return result

        else:
            raise TypeError("Index must be int or slice")
