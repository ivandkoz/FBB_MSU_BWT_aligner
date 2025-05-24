from parse_fasta import GenomeParser, ReadsParser, Genome
from transform_seq_to_bytes import BytesSeq
import os
import gc
from bwt import SuffixArray, BWT, BWTMatch, get_Count, get_FO, thin_Count, CompressedSuffixArray

def find_exact_match(reference_seq_path: os.PathLike | str, 
                     reads_path: os.PathLike | str):
    reference_seq = GenomeParser(reference_seq_path).parse()
    for chr in reference_seq.sequences:
        print(chr.sequence[:25])
        print(len(chr.sequence))
        byte_chr = BytesSeq(chr.sequence + "$")
        del chr
        # print(bin(byte_chr))

        # sa = SuffixArray(byte_chr)
        bwt = BWT(byte_chr)
        FO = get_FO(bwt)
        Count = get_Count(bwt)
        Count_sparse = thin_Count(Count, 128)
        del Count
        CSA = CompressedSuffixArray(byte_chr, 6)
        # print(sa, bwt)
        with ReadsParser(reads_path) as parser:
            for read in parser:
                byte_read = BytesSeq(read.sequence)
                print(read)
                # print(byte_read.bytes_seq)
                del read
                result = BWTMatch(byte_read, bwt, FO, Count_sparse, CSA, rate=128)
                print(f'Coords:{result}')
        del bwt, CSA  # Явное удаление
            
        gc.collect()
        

# def find_exact_match