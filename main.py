import random, threading, time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from event_recorder import EventRecorder

N=4
ROUNDS=2
condition=threading.Condition()
eating=[False]*N
owners=[None]*N
rec=EventRecorder("Dining Philosophers — Monitor","dp",[f"P{i}" for i in range(1,N+1)],[f"F{i}" for i in range(1,N+1)])

def owner_snapshot():
    return {f"F{i+1}":owners[i] for i in range(N) if owners[i]}

def philosopher(i):
    name=f"P{i+1}";left=i;right=(i+1)%N
    for _ in range(ROUNDS):
        time.sleep(random.uniform(.08,.22))
        rec.record(name,"thinking",f"{name} is thinking",owners=owner_snapshot())
        rec.record(name,"hungry",f"{name} becomes hungry",owners=owner_snapshot())
        with condition:
            while eating[(i-1)%N] or eating[(i+1)%N]:
                condition.wait()
            eating[i]=True
            owners[left]=name;owners[right]=name
            rec.record(name,"eating",f"{name} acquires F{left+1} and F{right+1} and eats",owners=owner_snapshot())
        time.sleep(random.uniform(.10,.20))
        with condition:
            eating[i]=False
            owners[left]=None;owners[right]=None
            rec.record(name,"thinking",f"{name} releases both forks",owners=owner_snapshot())
            condition.notify_all()

if __name__=="__main__":
    threads=[threading.Thread(target=philosopher,args=(i,)) for i in range(N)]
    for t in threads:t.start()
    for t in threads:t.join()
    rec.write_html("dining_philosophers_monitor.html")
