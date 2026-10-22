import random, threading, time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from event_recorder import EventRecorder

N=4
ROUNDS=2
room=threading.Semaphore(N-1)
forks=[threading.Semaphore(1) for _ in range(N)]
owners=[None]*N
owners_lock=threading.Lock()
rec=EventRecorder("Dining Philosophers — Semaphore","dp",[f"P{i}" for i in range(1,N+1)],[f"F{i}" for i in range(1,N+1)])

def record(name,state,message):
    with owners_lock:
        snapshot={f"F{i+1}":owners[i] for i in range(N) if owners[i]}
    rec.record(name,state,message,owners=snapshot)

def philosopher(i):
    name=f"P{i+1}";left=i;right=(i+1)%N
    for _ in range(ROUNDS):
        time.sleep(random.uniform(.08,.22))
        record(name,"thinking",f"{name} is thinking")
        record(name,"hungry",f"{name} becomes hungry")
        room.acquire()
        record(name,"acquiring",f"{name} enters room and requests forks")
        forks[left].acquire()
        with owners_lock: owners[left]=name
        record(name,"acquiring",f"{name} acquires F{left+1}")
        forks[right].acquire()
        with owners_lock: owners[right]=name
        record(name,"eating",f"{name} eats using F{left+1} and F{right+1}")
        time.sleep(random.uniform(.10,.20))
        record(name,"releasing",f"{name} finishes eating")
        with owners_lock: owners[left]=owners[right]=None
        forks[right].release();forks[left].release();room.release()
        record(name,"thinking",f"{name} releases both forks")

if __name__=="__main__":
    threads=[threading.Thread(target=philosopher,args=(i,)) for i in range(N)]
    for t in threads:t.start()
    for t in threads:t.join()
    rec.write_html("dining_philosophers_semaphore.html")
