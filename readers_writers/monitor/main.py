import random, threading, time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from event_recorder import EventRecorder

ROUNDS=2
condition=threading.Condition()
active_readers=0
active_writer=False
waiting_writers=0
shared_value=0
rec=EventRecorder("Readers–Writers — Monitor","rw",["R1","R2","R3","W1","W2"],[])

def reader(name):
    global active_readers
    for _ in range(ROUNDS):
        time.sleep(random.uniform(.08,.22))
        rec.record(name,"waiting",f"{name} requests read access",value=shared_value)
        with condition:
            while active_writer or waiting_writers>0:
                condition.wait()
            active_readers+=1
            rec.record(name,"reading",f"{name} starts reading",value=shared_value)
        time.sleep(random.uniform(.10,.22))
        with condition:
            active_readers-=1
            rec.record(name,"leaving",f"{name} finishes reading",value=shared_value)
            if active_readers==0: condition.notify_all()

def writer(name):
    global active_writer,waiting_writers,shared_value
    for _ in range(ROUNDS):
        time.sleep(random.uniform(.10,.28))
        rec.record(name,"waiting",f"{name} requests write access",value=shared_value)
        with condition:
            waiting_writers+=1
            while active_writer or active_readers>0: condition.wait()
            waiting_writers-=1
            active_writer=True
            old=shared_value
            time.sleep(.02)
            shared_value=old+1
            rec.record(name,"writing",f"{name} changes value {old} to {shared_value}",value=shared_value)
        time.sleep(random.uniform(.10,.20))
        with condition:
            rec.record(name,"leaving",f"{name} finishes writing",value=shared_value)
            active_writer=False
            condition.notify_all()

if __name__=="__main__":
    threads=[threading.Thread(target=reader,args=(f"R{i}",)) for i in range(1,4)]
    threads += [threading.Thread(target=writer,args=(f"W{i}",)) for i in range(1,3)]
    for t in threads:t.start()
    for t in threads:t.join()
    rec.write_html("readers_writers_monitor.html",shared_value)
