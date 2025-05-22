from typing import Optional


class BytesSeq():
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


    def __init__(self, sequence: str,
                 encode_mask: Optional[dict] = None):
        self.bytes_seq = bytearray()
        if encode_mask is None:
            self.encode_mask = {'a': 0b00, 'c': 0b01,
                                'g': 0b10, 't': 0b11}
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
        pad_value = 0b11
        # В цикле будем перескакивать через 4 символа за раз. Смотрим пачками по 4 буквы
        # Пришлось использовать while и прыжки через 4, чтобы избавиться от срезов
        while i < self.seq_length:
            byte = 0  # Инициализируем новый байт для 4 букв
            # в этом подцикле записываем 4 буквы в один байт
            for j in range(4):
                if i + j < self.seq_length:       # проверка, что мы не вышли за последовательность
                    ch = sequence[i + j]
                    # кодируем символ в 2 бита и размещаем в нужной позиции байта
                    # сдвигаем на (6 - 2*j) бит, чтобы распределить 4 символа по 8 битам:
                    # 1-й символ: биты 6-7
                    # 2-й символ: биты 4-5
                    # 3-й символ: биты 2-3
                    # 4-й символ: биты 0-1
                    byte |= self.encode_mask[ch] << (6 - 2 * j)
                else:
                    byte |= pad_value << (6 - 2 * j)    # если последний блок не из 4 букв, заполняем буквами t
            self.bytes_seq.append(byte)
            # Переходим к следующим 4 символам
            i += 4


    def get_bytes_seq(self):
        return self.bytes_seq


    def transform_to_seq(self):
        # decoded_seq = []
        # for byte in self.bytes_seq:
        #     for shift in (6, 4, 2, 0):
        #         decoded_seq.append(self.decode_mask[(byte >> shift) & 0b11])
        # return ''.join(decoded_seq)

        decoded_seq = []
        for idx in range(self.seq_length):
            byte_index = idx // 4
            bit_offset = 6 - 2 * (idx % 4)
            byte = self.bytes_seq[byte_index]
            code = (byte >> bit_offset) & 0b11
            decoded_seq.append(self.decode_mask[code])

        return ''.join(decoded_seq)