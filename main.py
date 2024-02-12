import math
import secrets
import sys
import threading
import timeit

import tiger
from console import Writer

test_messages: [dict[str, str]] = [
    {
        'given': 'The quick brown fox jumps over the lazy dog',
        'expected': '6d12a41e72e644f017b6f0e2f7b44c6285f06dd5d2c5b075',
    },
    {
        'given': 'The quick brown fox jumps over the lazy cog',
        'expected': 'a8f04b0f7201a0d728101c9d26525b31764a3493fcd8458f',
    },
    {
        'given': '',
        'expected': '3293ac630c13f0245f92bbb1766e16167a4e58492dde73f3',
    },
    {
        'given': 'tAcXkDwH3k9exMq5gZsXc1hi95k32qBBzpG2MjICteT7HydlGbTOlwWBlgYJ8uEM',
        'expected': 'ad43d904a3aeac48e38c7195a5179f090f4c9790c8e801cf',
    },
    {
        'given': 'O2GvNDsjLT8ZKvnopZAeEtzUJrk1Se54yedT529zAtXxbeoROyWWMW6hfA0auiXJgrBAUhWc5hkZ1l5q2InR3OXtc57weaV0GvzwBHePZyIU2F9txiYoAaHIr8DEIFM6U2b0nMQfvSAG3q6TE4YGrn8ZADGwT2NDYdiI3jff8P9YC7Pj7kuLtAjftYzxDkCYprhQzudYAJoRqvRYULu4dePX9WigMmgK6vyrJoafQx9qPewse16Xc0JGb0kdKZUd3aJXStIiDq16k8389MepoSyf5pxBT5CM0bzP80G7vT6zqU5j4FTgS6jjp7QIIVy5GmVqc14crUFdDlEty4sgOlHkGtjTCyoeDqGA4ogA4J3DYfeLkAnPmjR4vFCqZi8JjEzTR4DML9ohZvtHOnBD3ORtPyu08CsmJZSV5BdYXgYP1mnV3MpllGB3fXmu8l3lPBEAr1ZPqBi576GLkFcXPDUX7raA2dPJoTDfSNsduyRoFFC1mstENbvKVdeCVgFF9r4ILJeTtQIpphAiCFJIfmETtSEVnVzf9HHvYEnZgRXOmdMla8LXxgF1DBnJ1fklkOpd7WtYUB86m4tqPOdmI4qdd4fUCUTYDWrmB1Mm6nu44TMtDdBDbFhydHHL7Ekk07NwMvejX4xNWA9t4D1aRwyhS2WqKVDamlIOt5lMSYgcf3jEZxBGAbCl5NuWCT0HdrlWKLeJ3OoQBJk0fWwy40vvwMvUDSlKegGkz9RQ6T1Aj8BQtztwTNPdi4Vcfok6baeLknxCGC8LRqa7lZVw8t2EC7VghRm6KjjtVG78BqYGycu9H63Rdzs5Ce75NqATURAJTWYjvItX4KoKaIIutsu8uQv9eGFhfxec4IoEZS4cY05sRBzfdQ5h4TgTBjjDCC031zg1ygCWFuQhiXqCGkdgN2R93V5KR1o9CEQFv2FC66YSRN8qK3IU9WMjsx3cbiOAXjsSknSPo1M3EkFYK2czHPpfVic2MkHyWVFb',
        'expected': 'a4b7c24d6a10b7433fe3706e506c7fe026e81a06d4393107',
    }
]

test_files: [dict[str, str]] = [
    {
        # 'bytes': 0,
        'given': 'file_b_0.txt',
        'expected': '3293ac630c13f0245f92bbb1766e16167a4e58492dde73f3',
    },
    {
        'bytes': 100,
        'given': 'file_b_100.txt',
        'expected': '8aa2e10bc3a43cda149815dcff05b3e6acb15aada68fcbe4',
    },
    {
        'bytes': 1024,
        'given': 'file_kb_1.txt',
        'expected': '28cbd3dc2e55d0341aca55d9c6cd71ca18485fcf0efac2c7',
    },
    {
        'bytes': 1048576,
        'given': 'file_mb_1.txt',
        'expected': '6df1b6adc2e94415720f74f1dbc8ec3a734c5736a52db740',
    },
]


def run_test_case(test: dict) -> None:
    print(f"{''.join(['-' for _ in range(96)])}")
    message = test['given']
    preview: str = f'{message[:24]}[...]{message[-24:]}' if len(message) > 48 else message
    Writer.info(preview, before='Input: ')
    Writer.info('%d bytes' % len(message), before='Length: ')

    def func() -> None:
        result = tiger.TigerHash().hash(test['given'])
        Writer.info(result, 'Hash: ')
        if result == test['expected']:
            Writer.success('Passed!', before='Result: ')
        else:
            Writer.error('Failed!', before='Result: ')

    elapsed_time = timeit.timeit(stmt=func, number=1)
    if 'bytes' in test:
        Writer.info('%d bytes/s' % math.floor(test["bytes"] / elapsed_time), before='Throughput: ')
    else:
        Writer.info('%d bytes/s' % math.floor(len(test["given"]) / elapsed_time), before='Throughput: ')
    Writer.info('%.10f seconds' % elapsed_time, before='Elapsed time: ')


def run_tests() -> None:
    print("Running tests...")

    for test_config in test_messages:
        run_test_case(test_config)

    for test_config in test_files:
        with open(test_config['given'], 'r', encoding='latin-1') as f:
            contents = f.read()
            test_config['given'] = contents
            run_test_case(test_config)


def run_avalanche_effect_test() -> None:
    k = input('Enter bit number to be flipped (1-192): ')
    if not 1 <= int(k) <= 192:
        print('Invalid bit number')
        return
    k = int(k) - 1

    output_file = "dieharder.txt"

    tiger_hash = tiger.TigerHash()
    m = tiger_hash.hash('')

    with open(output_file, 'wb') as file:
        r = math.ceil(pow(2, 30) * 8 / 192)
        start = timeit.default_timer()
        for i in range(r):
            # for i in range(1):

            H_m = tiger_hash.hash(m)
            m_prim = int(m, 16)
            m_prim ^= (1 << (192 - k - 1))
            m_prim = hex(m_prim)[2:]

            H_m_prim = tiger_hash.hash(m_prim)

            XOR = hex(int(H_m, 16) ^ int(H_m_prim, 16))[2:]
            # file.write(bytes.fromhex(XOR.zfill(48)))
            file.write(XOR.encode('latin-1'))

            m = H_m_prim

            if i != 0 and (i % 10000 == 0 or i == r - 1):
                end = timeit.default_timer()
                elapsed_time = end - start
                current = i * 100 / (r - 1)
                remaining = elapsed_time * (100 - current) / current
                print(f'Progress: %02.2f%% Remaining: %.10f seconds' % (current, remaining))

    print(f'Dieharder input file saved to {output_file}')
    return


class MyThread(threading.Thread):
    def __init__(self, thread_id, hash_length, h, counts: dict, result: dict, threads: list):
        super(MyThread, self).__init__()
        self.thread_id = thread_id
        self.hash_length = hash_length
        self.h = h
        self.counts = counts
        self.result = result
        self.threads = threads
        self.do_run = True

    def run(self):
        while self.do_run:
            success = False
            solution = None
            msg = None
            counter = 0

            tiger_hash = tiger.TigerHash()
            binary_result = bin(int(self.h, 16))[2:][:int(self.hash_length) * 8]
            result_h = hex(int(binary_result, 2))[2:]

            start = timeit.default_timer()
            elapsed_time = 0

            while elapsed_time < 3600 and self.result.get('solution') is None:
                counter = counter + 1
                msg = str(secrets.token_bytes(100))
                h_m = tiger_hash.hash(msg)
                binary_h_m = bin(int(h_m, 16))[2:][:int(self.hash_length) * 8]
                h_m = hex(int(binary_h_m, 2))[2:]

                end = timeit.default_timer()
                elapsed_time = end - start

                if counter % 10000 == 0:
                    print(f"Thread {self.thread_id} counter: {counter} current hash: {h_m}")

                if h_m == result_h:
                    success = True
                    solution = result_h
                    break

            if success:
                self.counts[self.thread_id] = counter
                self.result["solution"] = solution
                print(f"Thread {self.thread_id} found solution: {result_h} == {solution}")
                print(f"Message: {msg}")
                print(f"Elapsed time: {elapsed_time}")
                # Zatrzymujemy pozostałe wątki
                print("Stopping threads...")
                for thread in self.threads:
                    assert isinstance(thread, MyThread)
                    if thread != threading.current_thread():
                        thread.stop()
                self.do_run = False
                for thread in self.threads:
                    print(f"Thread {thread.thread_id} is alive: {thread.is_alive()}")
            else:
                for thread in threading.enumerate():
                    if thread == threading.current_thread():
                        thread.do_run = False

    def stop(self):
        self.do_run = False
        self.join()


def ataki() -> None:
    # Tworzymy i uruchamiamy 10 wątków
    counts: dict = {}
    result: dict = {}
    threads = []
    tiger_hash = tiger.TigerHash()

    hash_length = 1
    message = str(secrets.token_bytes(100))
    h = tiger_hash.hash(message)

    while 1:
        print('Starting threads...')
        for i in range(8):
            thread = MyThread(i, hash_length, h, counts, result, threads)
            thread.start()
            threads.append(thread)

        # Czekamy na zakończenie wszystkich wątków
        for thread in threads:
            thread.join()

        print('ALL FINISHED')

        if result.get('solution'):
            Writer.success('Passed!', before='Result: ')
            Writer.info('%d' % hash_length, before='Hash length: ')
            Writer.info(message, before='Message: ')
            print(counts)
            print(result)
            # Writer.info('%d' % counts, before='Counter: ')
            hash_length = hash_length + 1
            counts: dict = {}
            result: dict = {}
            threads = []
            result = {}

        else:
            print("No solution found")
            break


def main() -> None:
    hash_length = input('Enter hash length in bytes (1-24): ')
    if not hash_length.isdigit() or not 1 <= int(hash_length) <= 24:
        print('Invalid hash length.')
        return
    filename = input('Enter filename: ')
    with open(filename, 'r', encoding='latin-1') as f:
        print(f'Hashing {filename}...')
        Writer.info(f"{hash_length} {'byte' if hash_length == '1' else 'bytes'}", before='Hash length: ')
        contents = f.read()
        result = tiger.TigerHash().hash(contents)
        binary_result = bin(int(result, 16))[2:][:int(hash_length) * 8]
        result = hex(int(binary_result, 2))[2:]
        Writer.info(result, before='Hash: ')
        open('hash.txt', 'w', encoding='latin-1').write(f'{result}\n')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == 'avalanche_effect_test':
        run_avalanche_effect_test()
    elif len(sys.argv) > 1 and sys.argv[1] == 'atak':
        ataki()
    else:
        main()
