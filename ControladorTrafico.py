import multiprocessing
import time


class ControladorTrafico(multiprocessing.Process):
    def __init__(
        self, pipes, state_queue, stats_dict, stats_lock, barrier,
        green_duration=10, yellow_duration=3, all_red_duration=2
    ):
        super().__init__()
        self.pipes = pipes
        self.state_queue = state_queue
        self.stats = stats_dict
        self.lock = stats_lock
        self.green = green_duration
        self.yellow = yellow_duration
        self.all_red = all_red_duration
        self.barrier = barrier
        with self.lock:
            self.stats['cycles_completed'] = 0

    def run(self):
        # Esperar a semáforos
        self.barrier.wait()
        ns = ['Norte', 'Sur']
        ew = ['Este', 'Oeste']
        while True:
            # Fase Norte-Sur
            for d in ns:
                self.pipes[d].send('green')
                self.state_queue.put((d, 'green'))
            for d in ew:
                self.pipes[d].send('red')
                self.state_queue.put((d, 'red'))
            time.sleep(self.green)
            for d in ns:
                self.pipes[d].send('yellow')
                self.state_queue.put((d, 'yellow'))
            time.sleep(self.yellow)
            for d in ns + ew:
                self.pipes[d].send('red')
                self.state_queue.put((d, 'red'))
            time.sleep(self.all_red)
            # Fase Este-Oeste
            for d in ew:
                self.pipes[d].send('green')
                self.state_queue.put((d, 'green'))
            for d in ns:
                self.pipes[d].send('red')
                self.state_queue.put((d, 'red'))
            time.sleep(self.green)
            for d in ew:
                self.pipes[d].send('yellow')
                self.state_queue.put((d, 'yellow'))
            time.sleep(self.yellow)
            for d in ns + ew:
                self.pipes[d].send('red')
                self.state_queue.put((d, 'red'))
            time.sleep(self.all_red)
            with self.lock:
                self.stats['cycles_completed'] += 1

