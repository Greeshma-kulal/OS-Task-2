import random, threading, time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from event_recorder import EventRecorder

ROUNDS = 2
reader_count = 0
reader_count_lock = threading.Semaphore(1)
resource_lock = threading.Semaphore(1)
shared_value = 0
rec = EventRecorder("Readers–Writers — Semaphore", "rw", ["R1","R2","R3","W1","W2"], [])

def reader(name):
    global reader_count
    for _ in range(ROUNDS):
        time.sleep(random.uniform(.08,.22))
        rec.record(name,"waiting",f"{name} requests read access",value=shared_value)
        reader_count_lock.acquire()
        reader_count += 1
        if reader_count == 1:
            resource_lock.acquire()
        rec.record(name,"reading",f"{name} starts reading",value=shared_value)
        reader_count_lock.release()
        time.sleep(random.uniform(.10,.22))
        rec.record(name,"leaving",f"{name} finishes reading",value=shared_value)
        reader_count_lock.acquire()
        reader_count -= 1
        if reader_count == 0:
            resource_lock.release()
        reader_count_lock.release()

def writer(name):
    global shared_value
    for _ in range(ROUNDS):
        time.sleep(random.uniform(.10,.28))
        rec.record(name,"waiting",f"{name} requests write access",value=shared_value)
        resource_lock.acquire()
        old=shared_value
        time.sleep(.02)
        shared_value=old+1
        rec.record(name,"writing",f"{name} changes value {old} to {shared_value}",value=shared_value)
        time.sleep(random.uniform(.10,.20))
        rec.record(name,"leaving",f"{name} finishes writing",value=shared_value)
        resource_lock.release()

if __name__=="__main__":
    threads=[threading.Thread(target=reader,args=(f"R{i}",)) for i in range(1,4)]
    threads += [threading.Thread(target=writer,args=(f"W{i}",)) for i in range(1,3)]
    for t in threads:t.start()
    for t in threads:t.join()
    rec.write_html("readers_writers_semaphore.html",shared_value)
