import threading
import time
import random
from queue import Queue

# ---------------- TOKEN CLASS ----------------
class Token:
    def __init__(self, n):
        self.LN = [0] * n        # Last request served
        self.queue = Queue()    # FIFO queue of waiting processes


# ---------------- PROCESS CLASS ----------------
class Process(threading.Thread):
    def __init__(self, pid, n, processes, token_holder):
        super().__init__()
        self.pid = pid
        self.n = n
        self.RN = [0] * n
        self.processes = processes
        self.token_holder = token_holder
        self.has_token = False

    # Broadcast request
    def request_cs(self):
        self.RN[self.pid] += 1
        print(f"P{self.pid} broadcasts request RN[{self.pid}] = {self.RN[self.pid]}")
        for p in self.processes:
            p.receive_request(self.pid, self.RN[self.pid])

    # Receive request
    def receive_request(self, j, rn):
        self.RN[j] = max(self.RN[j], rn)
        if self.has_token and j != self.pid:
            token = self.token_holder["token"]
            if self.RN[j] == token.LN[j] + 1:
                token.queue.put(j)

    # Enter critical section
    def enter_cs(self):
        print(f"🔥 P{self.pid} ENTERS critical section")
        time.sleep(random.uniform(1, 2))
        print(f"✅ P{self.pid} EXITS critical section")

    # Release critical section
    def release_cs(self):
        token = self.token_holder["token"]
        token.LN[self.pid] = self.RN[self.pid]

        for j in range(self.n):
            if self.RN[j] == token.LN[j] + 1 and j not in list(token.queue.queue):
                token.queue.put(j)

        if not token.queue.empty():
            next_pid = token.queue.get()
            print(f"🔁 Token passed from P{self.pid} to P{next_pid}")
            self.has_token = False
            self.processes[next_pid].has_token = True
        else:
            print(f"🪙 Token remains with P{self.pid}")

    def run(self):
        time.sleep(random.uniform(1, 3))
        self.request_cs()

        while not self.has_token:
            time.sleep(0.1)

        self.enter_cs()
        self.release_cs()


# ---------------- MAIN SIMULATION ----------------
def main():
    n = 4  # Number of processes
    token = Token(n)

    token_holder = {"token": token}
    processes = []

    for i in range(n):
        processes.append(Process(i, n, processes, token_holder))

    # Initially P0 has the token
    processes[0].has_token = True
    print("🪙 Initial token with P0\n")

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print("\n🎯 Simulation completed")


if __name__ == "__main__":
    main()
