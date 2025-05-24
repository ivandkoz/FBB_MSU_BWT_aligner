from parse_fasta import GenomeParser, ReadsParser, Genome
from transform_seq_to_bytes import BytesSeq
import numpy as np
import os
import gc
from bwt import BWT, BWTMatch, get_Count, get_FO, thin_Count, CompressedSuffixArray


def find_exact_match(g_part:str, 
                     reads_path: os.PathLike | str):
    
    byte_chr = BytesSeq(g_part + "$")
    del g_part
    # print(bin(byte_chr))

    # sa = SuffixArray(byte_chr)
    bwt, sa = BWT(byte_chr)
    FO = get_FO(bwt)
    Count = get_Count(bwt)
    Count_sparse = thin_Count(Count, 128)
    del Count
    CSA = CompressedSuffixArray(sa, 6)
    reads_coords = {}
    with ReadsParser(reads_path) as parser:
        for read in parser:
            byte_read = BytesSeq(read.sequence)
            reads_coords[read.header] = BWTMatch(byte_read, bwt, FO,
                                                    Count_sparse, CSA, rate=128)
            del read
    del bwt, CSA
    gc.collect()
    return reads_coords

def seq_cutter(seq, step=500000): #принимает последовательность в формате str 
    pieces = {}
    start = 0
    id = 0

    while start < len(seq):
        pieces[str(id)] = seq[start:start + step]
        start += step
        id += 1

    return pieces #выдает словарь формата {'id': subseq}


def mapping(reference_seq_path: os.PathLike, reads_path: os.PathLike, step=10000):
    reads_idx_global = {}
    reference_seq = GenomeParser(reference_seq_path).parse()
    previous_chr_len = 0
    for chr in reference_seq.sequences:
        cutted_genome = seq_cutter(chr.sequence, step=step)
        for genom_id in cutted_genome.keys():
            reads_idx_local = find_exact_match(cutted_genome[genom_id], reads_path)

            for read_id in reads_idx_local.keys():
                reads_idx_local[read_id] = np.array(list(reads_idx_local[read_id])) + int(genom_id)*step + previous_chr_len
                reads_idx_local[read_id] = set(reads_idx_local[read_id])
                if read_id in reads_idx_global.keys():
                    reads_idx_global[read_id] = reads_idx_global[read_id].union((reads_idx_local[read_id]))
                else:
                    reads_idx_global[read_id] = reads_idx_local[read_id]
        previous_chr_len = len(chr.sequence)
    return reads_idx_global
