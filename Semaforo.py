import multiprocessing
import time
import random


class Semaforo(multiprocessing.Process):
    opposite = {'Norte': 'Sur', 'Sur': 'Norte', 'Este': 'Oeste', 'Oeste': 'Este'}

    def __init__(
        self, direccion, cmd_conn, moving_queue, stats_dict, stats_lock, barrier,
        arrival_rate=0.2, departure_interval=1
    ):
        super().__init__()
        self.direccion = direccion
        self.cmd_conn = cmd_conn
        self.moving_queue = moving_queue
        self.stats = stats_dict
        self.lock = stats_lock
        self.arrival_rate = arrival_rate
        self.departure_interval = departure_interval
        self.pending = []
        self.color = 'red'
        self.barrier = barrier

    def run(self):
        random.seed()
        # Esperar a que todos los procesos estén listos
        self.barrier.wait()
        next_arrival = time.time() + random.expovariate(self.arrival_rate)

        while True:
            # Revisar cambio de estado del semáforo
            if self.cmd_conn.poll():
                self.color = self.cmd_conn.recv()

            now = time.time()

            # Procesar cruce si hay vehículos en espera y semáforo en verde
            if self.color == 'green' and self.pending:
                arrival = self.pending.pop(0)
                wait = now - arrival
                with self.lock:
                    self.stats[f'{self.direccion}_waiting'] -= 1
                    self.stats[f'{self.direccion}_crossed'] += 1
                    self.stats[f'{self.direccion}_total_wait'] += wait
                target = Semaforo.opposite[self.direccion]
                vid = f"{self.direccion}_{int(time.time() * 1000)}"
                self.moving_queue.put((vid, self.direccion, target))
                time.sleep(self.departure_interval)

            # Generar nuevo vehículo si es momento
            if now >= next_arrival:
                self.pending.append(now)
                with self.lock:
                    self.stats[f'{self.direccion}_waiting'] += 1
                next_arrival = now + random.expovariate(self.arrival_rate)

            time.sleep(0.1)

