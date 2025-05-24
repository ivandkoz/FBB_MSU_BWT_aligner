import math

def write_sam(mappings, reads_dict, output_filename='output.sam', rname='ref', reference_length=1000000):

    with open(output_filename, 'w') as sam_file:
        # Заголовок SAM
        sam_file.write(f'@HD\tVN:1.6\tSO:unsorted\n')
        sam_file.write(f'@SQ\tSN:{rname}\tLN:{reference_length}\n')
        
        # Запись выравниваний
        for read_id, positions in mappings.items():
            if read_id not in reads_dict:
                continue  # Пропускаем риды без данных о последовательности
                
            read_length = len(reads_dict[read_id])
            n_hits = len(positions)
            
            # Расчет MAPQ
            if n_hits == 1:
                mapq = 60  # Уникальное выравнивание
            else:
                mapq = int(-10 * math.log10((n_hits - 1) / n_hits)) if n_hits > 1 else 0
            
            # Запись каждого хита
            for i, pos in enumerate(positions):
                flag = 0 if i == 0 else 256  # 256 = вторичное выравнивание
                pos_1based = pos + 1
                cigar = f'{read_length}M'
                
                sam_line = (
                    f'{read_id}\t{flag}\t{rname}\t{pos_1based}\t{mapq}\t{cigar}\t'
                    f'*\t0\t0\t*\t*\n'
                )
                sam_file.write(sam_line)
