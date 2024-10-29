import os
import re
import time
from objectproxypool import ProxyPool


class MyClass:
    def find_matching_sequences_main(self, chunk):
        num, pattern, chunk_start = chunk
        matches = []
        match_iter = re.finditer(pattern, num)
        num_matches = 0
        for match in match_iter:
            num_matches += 1
            matches.append(f"{int(match.group())} {match.start() + chunk_start + 1} {match.end() + chunk_start}\n")
        return ''.join(matches), num_matches

    def read_file(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()


def read_data(father_path):
    file_paths = [os.path.join(root, file) for root, _, files in os.walk(father_path) for file in files]
    with ProxyPool(MyClass, numWorkers=os.cpu_count(), separateProcesses=True) as myObject:
        all_data = myObject.read_file(file_paths, map_args=True)
    return ''.join(all_data)


def find_matching_sequences(all_data, patterns, parallel=False):
    sequences = ''
    count_numbers = {}
    print('主计算开始')
    for pat in patterns:
        if parallel:
            num_processes = os.cpu_count()
            chunks = chunk_data(all_data, pat, num_processes)

            with ProxyPool(MyClass, numWorkers=os.cpu_count(), separateProcesses=True) as myObject:
                results = myObject.find_matching_sequences_main(chunks, map_args=True)
            print('主计算完成')
            sub_sequences = ''.join(result[0] for result in results)
            num_matches = sum(int(result[1]) for result in results)
        else:
            sub_sequences, num_matches = myObject.find_matching_sequences_main((all_data, pat, 0))
            print('主计算完成')
        count_numbers[pat] = num_matches
        sequences += sub_sequences

    return sequences, count_numbers


def chunk_data(all_data, pattern, num_chunks):
    chunk_size = len(all_data) // num_chunks
    chunks = [(all_data[i * chunk_size:(i + 1) * chunk_size], pattern, i * chunk_size) for i in range(num_chunks)]
    return chunks


def Cal_fin(patterns, all_data):
    t1 = time.perf_counter()
    parallel = len(all_data) > 100000  # 根据数据量决定是否并行处理
    sequences, count_numbers = find_matching_sequences(all_data, patterns, parallel=parallel)
    t2 = time.perf_counter()
    time_cal = t2 - t1
    return sequences, time_cal, count_numbers, len(all_data)


# 在主函数中调用 Cal_fin
if __name__ == '__main__':
    sequences, time_cal, count_numbers, len_data = Cal_fin(['1'], read_data('Data'))
