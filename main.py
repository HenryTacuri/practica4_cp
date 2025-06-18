import multiprocessing
import tkinter as tk

from TrafficGUI import TrafficGUI
from Semaforo import Semaforo
from ControladorTrafico import ControladorTrafico

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    directions = ['Norte', 'Sur', 'Este', 'Oeste']

    # Pipes para control de semáforos
    pipes = {}
    for d in directions:
        parent_conn, child_conn = multiprocessing.Pipe()
        pipes[d] = parent_conn
        pipes[f'{d}_child'] = child_conn

    # Cola para estados y para movimientos
    state_queue = multiprocessing.Queue()
    moving_queue = multiprocessing.Queue()

    # Estadísticas compartidas y sincronización
    manager = multiprocessing.Manager()
    stats = manager.dict()
    lock = multiprocessing.Lock()
    for d in directions:
        stats[f'{d}_waiting'] = 0
        stats[f'{d}_crossed'] = 0
        stats[f'{d}_total_wait'] = 0.0
    barrier = multiprocessing.Barrier(len(directions) + 1)

    # Crear y arrancar semáforos
    semaforos = []
    for d in directions:
        p = Semaforo(
            d,
            pipes[f'{d}_child'],
            moving_queue,
            stats,
            lock,
            barrier
        )
        p.start()
        semaforos.append(p)

    # Crear y arrancar controlador
    controller = ControladorTrafico(
        {d: pipes[d] for d in directions},
        state_queue,
        stats,
        lock,
        barrier
    )
    controller.start()

    # Iniciar GUI
    root = tk.Tk()
    root.title("Simulación de Tráfico")
    gui = TrafficGUI(
        root,
        state_queue,
        stats,
        moving_queue,
        semaforos,
        controller
    )
    root.mainloop()
