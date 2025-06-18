import tkinter as tk


class TrafficGUI:
    def __init__(
        self, root, state_queue, stats_dict, moving_queue, semaforos, controller
    ):
        self.root = root
        self.state_q = state_queue
        self.stats = stats_dict
        self.moving_q = moving_queue
        self.semaforos = semaforos
        self.controller = controller
        self.colors = {d: 'red' for d in ['Norte','Sur','Este','Oeste']}
        self.local_moving = []

        self.canvas = tk.Canvas(root, width=600, height=600, bg='lightgray')
        self.canvas.pack()
        self.draw_intersection()
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_gui()

    def draw_intersection(self):
        self.canvas.create_rectangle(250, 0, 350, 600, fill='gray')
        self.canvas.create_rectangle(0, 250, 600, 350, fill='gray')
        self.canvas.create_line(0, 300, 600, 300, fill='white', dash=(4, 4), width=2)
        self.canvas.create_line(300, 0, 300, 600, fill='white', dash=(4, 4), width=2)
        self.light_coords = {
            'Norte': (300, 260), 'Sur': (300, 340),
            'Este': (340, 300), 'Oeste': (260, 300)
        }
        self.lights = {}
        for d, (x, y) in self.light_coords.items():
            self.lights[d] = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill='red')

    def update_gui(self):
        while not self.state_q.empty():
            d, c = self.state_q.get()
            self.colors[d] = c
        for d, oval in self.lights.items():
            self.canvas.itemconfig(oval, fill=self.colors[d])

        # Procesar vehículos en movimiento
        while not self.moving_q.empty():
            vid, frm, to = self.moving_q.get()
            self.local_moving.append({'from': frm, 'to': to, 'progress': 0.0})

        self.canvas.delete('mov')
        wait_pos = {
            'Norte': (290, 240), 'Sur': (310, 360),
            'Este': (360, 310), 'Oeste': (240, 290),
        }
        exit_pos = {
            'Norte': (295, 360), 'Sur': (305, 240),
            'Este': (240, 305), 'Oeste': (360, 295),
        }

        finished = []
        for mv in self.local_moving:
            mv['progress'] += 0.05
            p = mv['progress']
            sx, sy = wait_pos[mv['from']]
            ex, ey = exit_pos[mv['from']]
            x = sx + (ex - sx) * p
            y = sy + (ey - sy) * p

            offset = 5
            if mv['from'] in ['Norte', 'Sur']:
                x += -offset if mv['from'] == 'Norte' else offset
            else:
                y += -offset if mv['from'] == 'Oeste' else offset

            self.canvas.create_rectangle(x-5, y-5, x+5, y+5, fill='blue', tags='mov')
            if p >= 1.0:
                finished.append(mv)
        for mv in finished:
            self.local_moving.remove(mv)

        self.canvas.delete('veh')
        for d, (x, y) in wait_pos.items():
            count = self.stats.get(f'{d}_waiting', 0)
            for i in range(min(count, 5)):
                if d == 'Norte':
                    yoff = y - i * 15; xoff = x
                elif d == 'Sur':
                    yoff = y + i * 15; xoff = x
                elif d == 'Este':
                    xoff = x + i * 15; yoff = y
                else:
                    xoff = x - i * 15; yoff = y
                self.canvas.create_rectangle(xoff-5, yoff-5, xoff+5, yoff+5, fill='blue', tags='veh')

        self.root.after(100, self.update_gui)

    def on_closing(self):
        for p in self.semaforos + [self.controller]:
            p.terminate()
            p.join()
        print("=== Reporte de tráfico ===")
        for d in ['Norte', 'Sur', 'Este', 'Oeste']:
            crossed = self.stats.get(f'{d}_crossed', 0)
            total_wait = self.stats.get(f'{d}_total_wait', 0.0)
            avg = total_wait / crossed if crossed > 0 else 0.0
            print(f"{d}: cruzados={crossed}, espera_promedio={avg:.2f}s")
        print(f"Ciclos completados: {self.stats.get('cycles_completed', 0)}")
        self.root.destroy()


