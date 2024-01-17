#! venv/bin/python
import threading
import time


def worker(sem, worker_id: int) -> None:
    print(f"Worker {worker_id} waiting for semathore")

    sem.acquire()
    
    print(f"Worker {worker_id} is working with the semaphore")
    time.sleep(3)

    sem.release()
    print(f"Worker {worker_id} is finished and released the semaphore")



num_resources = 2
semaphore = threading.Semaphore(num_resources)

threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(semaphore, i))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

print("Finished")

print(f"Threads: {threads}")
time.sleep(1)


