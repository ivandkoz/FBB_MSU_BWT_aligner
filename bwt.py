import bisect

def SuffixArray(s):
    return sorted(range(len(s)), key=lambda i: s[i:])


# def SuffixArrayBytes(s: BytesSeq) -> list[int]:
#     return sorted(range(len(s)), key=lambda i: s[i:])

def CompressedSuffixArray(s, step):
    sa = SuffixArray(s)
    return {i: sa[i] for i in range(len(sa)) if sa[i] % step == 0}


def thin_Count(Count, rate):
    return {k: v for k, v in Count.items() if k % rate == 0}


def get_Count_value(k, symbol, bwt, count_sparse, rate=128):
    keys = sorted(count_sparse.keys())
    pos = bisect.bisect_right(keys, k) - 1
    base = keys[pos]
    base_count = count_sparse[base][symbol]

    if k == base:
        return base_count
    elif k > base:
        delta = bwt[base:k].count(symbol)
        return base_count + delta
    else:
        delta = bwt[k:base].count(symbol)
        return base_count - delta
    

def get_SA_value(k, bwt, FO, Count_sparse, CSA, rate=128):
    steps = 0
    while k not in CSA:
        char = bwt[k]
        count_k_char = get_Count_value(k, char, bwt, Count_sparse, rate)
        k = FO[char] + count_k_char - 1
        steps += 1
    return CSA[k] + steps


def BWT(s):
    sa = SuffixArray(s)
    n = len(s)
    bwt = []
    for i in range(n):      # O(n)
        ind_ = (sa[i] - 1)  # O(1)
        x = s[ind_ % n]     # O(1)
        # Подумай про использование chr('letter') и RLE для такого
        # Подумай про поиск одинаковых строк разом  
        bwt.append(x)
    return bwt


def get_FO(bwt):
    # Для подсчёта FirstOccurrence вам нужно
    # отсортировать BWT и в нём определить индекс
    # первого вхождения каждого уникального символа.
    # Это можно сделать за один проход по sortBWT,
    # не используя метод .index
    sortBWT = sorted(bwt)
    total = 0
    FO = {}
    for char in sorted(set(bwt)):
      FO[char] = total
      total += sortBWT[total:].count(char)

    return FO


def get_Count(bwt):
    # Для подсчёта массива Count стоит завести словарь,
    # обновляемый на каждом новом шаге цикла. Словари в питоне,
    # как и списки, можно копировать методом .copy
    all_chars = sorted(set(bwt))
    cache_dt = {c: 0 for c in all_chars}
    result = {}
    result[0] = cache_dt.copy()
    for i in range(1, len(bwt)+1):
      cache_dt[bwt[i-1]] += 1
      result[i] = cache_dt.copy()
    return result


# def get_LF(bwt):
#     # Массив LF можно получить по соотношению, указанному в задании
#     LF = []
#     FO = get_FO(bwt)
#     cnt = get_Count(bwt)
#     for i, char in enumerate(bwt):
#       lf_val = FO[char] + cnt[i][char]
#       LF.append(lf_val)
    # return LF


def get_BWT_indices(pattern, bwt, FO, Count_sparse, rate=128):
    top, bottom = 0, len(bwt) - 1
    for char in reversed(pattern):
        # Используем get_Count_value для получения количества символов в Count_sparse
        if get_Count_value(bottom + 1, char, bwt, Count_sparse, rate)\
            - get_Count_value(top, char, bwt, Count_sparse, rate) <= 0:
            return []
        top = FO[char] + get_Count_value(top, char, bwt, Count_sparse, rate)
        bottom = FO[char] + get_Count_value(bottom + 1, char, bwt, Count_sparse, rate) - 1
    return list(range(top, bottom + 1))


def BWTMatch(pattern, bwt, FO, Count_sparse, CSA, rate=128):
    idxs = get_BWT_indices(pattern, bwt, FO, Count_sparse, rate)
    results = set()
    for i in idxs:
        pos = i
        steps = 0
        # Попытаемся найти SA[i] в CSA, если нет — идём по LF-функции назад
        while pos not in CSA:
            char = bwt[pos]
            pos = FO[char] + get_Count_value(pos, char, bwt, Count_sparse, rate) - 1
            steps += 1
        results.add(CSA[pos] + steps)
    return results



# def get_BWT_indices(pattern, bwt):
#     FO = get_FO(bwt)
#     Count = get_Count(bwt)
#     # инициализируйте указатели
#     top, bottom = 0, len(bwt) - 1
#     for char in reversed(pattern):
#         # по чему мы итерируемся на каждом шаге поиска в FM-индексе?
#         # обработайте случай, когда паттерна в BWT нет.
#         # затем, обновите указатели так, как мы обсуждали в лекции
#         if bwt[top:bottom+1].count(char) == 0:
#             return []
#         top = FO[char] + Count[top][char]
#         bottom = FO[char] + Count[bottom+1][char] - 1
#     # вернуть нужно множество индексов вхождения
#     indices = [*range(top, bottom + 1)]


#     return indices

# def BWTMatch(pattern, bwt, SA):
    # idxs = get_BWT_indices(pattern, bwt)
    # получите индексы вхождения паттерна в массив Барроуза-Уилера
    # преобразуйте их в индексы вхождения в строку, имея суффиксный массив
    # return set(SA[i] for i in idxs) 

# def BWT_match(reads: dict, g_part: seq):
#     byte_g_part = BytesSeq(g_part).bytes_seq
#     sa = SuffixArray(byte_g_part)
#     bwt = BWT(byte_g_part)
#     reads_coords = {}
#     for read_id, read_seq in reads.items():
#         byte_read = BytesSeq(read_seq).bytes_seq
#         coords = BWT_find_match(byte_read, bwt, sa)
#         reads_coords[read_id] = coords
#     return reads_coords
