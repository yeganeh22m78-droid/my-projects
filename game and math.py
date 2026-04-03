
from tkinter import ttk, messagebox
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import sqlite3
import hashlib
import math

# ==================== DATABASE CONFIG ====================
DB_FILE = 'users.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ==================== MAIN APP ====================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        init_db()  # Initialize database
        self.title("Multi-View App")
        self.geometry("900x700")
        self.configure(bg="#1e1e2e")
        self.current_user = None
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        LoginView(self)

    def show_menu(self):
        self.clear()
        MenuView(self)

# ==================== 1. LOGIN / REGISTER ====================
class LoginView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e2e")
        self.master = master
        self.pack(fill="both", expand=True)

        tk.Label(self, text="🔐 Login / Register", font=("Arial", 24, "bold"),
                 bg="#1e1e2e", fg="white").pack(pady=30)

        tk.Label(self, text="Username", bg="#1e1e2e", fg="white").pack()
        self.username = tk.Entry(self, font=("Arial", 14))
        self.username.pack(pady=5)

        tk.Label(self, text="Password", bg="#1e1e2e", fg="white").pack()
        self.password = tk.Entry(self, font=("Arial", 14), show="*")
        self.password.pack(pady=5)

        tk.Button(self, text="Login", bg="#7c3aed", fg="white",
                  font=("Arial", 13), command=self.login).pack(pady=10)
        tk.Button(self, text="Register", bg="#059669", fg="white",
                  font=("Arial", 13), command=self.register).pack()

    def login(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (self.username.get(), hash_password(self.password.get()))
            )
            user = cursor.fetchone()
            if user:
                self.master.current_user = self.username.get()
                self.master.show_menu()
            else:
                messagebox.showerror("Error", "Invalid credentials!")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def register(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (self.username.get(), hash_password(self.password.get()))
            )
            conn.commit()
            messagebox.showinfo("Success", "Registered successfully!")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

# ==================== MENU ====================
class MenuView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e2e")
        self.master = master
        self.pack(fill="both", expand=True)

        tk.Label(self, text=f"👋 Welcome, {master.current_user}!",
                 font=("Arial", 20, "bold"), bg="#1e1e2e", fg="white").pack(pady=20)

        buttons = [
            ("🔢 Matrix Calculator",  MatrixView),
            ("🔲 Rotate Square 3D",   SquareView),
            ("📦 Rotate Cube 3D",     CubeView),
            ("🚀 Rockets to Moon",    RocketView),
        ]

        for text, view in buttons:
            tk.Button(self, text=text, font=("Arial", 14),
                      bg="#7c3aed", fg="white", width=25,
                      command=lambda v=view: self.open_view(v)).pack(pady=8)

        tk.Button(self, text="🚪 Logout", font=("Arial", 12),
                  bg="#dc2626", fg="white",
                  command=master.show_login).pack(pady=20)

    def open_view(self, view_class):
        win = tk.Toplevel(self.master)
        win.configure(bg="#1e1e2e")
        view_class(win)

# ==================== 2. MATRIX CALCULATOR ====================
class MatrixView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e2e")
        self.master = master
        master.title("Matrix Calculator")
        master.geometry("700x600")
        self.pack(fill="both", expand=True)

        tk.Label(self, text="🔢 Matrix Calculator", font=("Arial", 18, "bold"),
                 bg="#1e1e2e", fg="white").pack(pady=10)

        frame = tk.Frame(self, bg="#1e1e2e")
        frame.pack()

        tk.Label(frame, text="Matrix A", bg="#1e1e2e", fg="#a78bfa",
                 font=("Arial", 13, "bold")).grid(row=0, column=0, padx=20)
        tk.Label(frame, text="Matrix B", bg="#1e1e2e", fg="#34d399",
                 font=("Arial", 13, "bold")).grid(row=0, column=1, padx=20)

        self.entries_a = self.make_matrix(frame, 0)
        self.entries_b = self.make_matrix(frame, 1)

        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(pady=10)

        for text, op in [("➕ Add", "add"), ("➖ Sub", "sub"), ("✖ Mul", "mul")]:
            tk.Button(btn_frame, text=text, bg="#7c3aed", fg="white",
                      font=("Arial", 12),
                      command=lambda o=op: self.calculate(o)).pack(side="left", padx=8)

        tk.Label(self, text="Result:", bg="#1e1e2e", fg="white",
                 font=("Arial", 13, "bold")).pack()
        self.result = tk.Text(self, height=6, width=40, bg="#2d2d3f", fg="white",
                              font=("Courier", 12))
        self.result.pack(pady=5)

    def make_matrix(self, frame, col):
        entries = []
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(frame, width=5, font=("Arial", 12),
                             bg="#2d2d3f", fg="white", justify="center")
                e.insert(0, "0")
                e.grid(row=i+1, column=col, padx=5+j*35, pady=3)
                row.append(e)
            entries.append(row)
        return entries

    def get_matrix(self, entries):
        return np.array([[float(entries[i][j].get())
                          for j in range(3)] for i in range(3)])

    def calculate(self, op):
        try:
            A = self.get_matrix(self.entries_a)
            B = self.get_matrix(self.entries_b)
            if op == "add": R = A + B
            elif op == "sub": R = A - B
            else: R = A @ B
            self.result.delete("1.0", "end")
            self.result.insert("end", str(R))
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ==================== 3. ROTATE SQUARE 3D ====================
class SquareView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e2e")
        master.title("Rotate Square 3D")
        master.geometry("600x600")
        self.pack(fill="both", expand=True)

        self.fig = plt.Figure(figsize=(5, 5), facecolor="#1e1e2e")
        self.ax  = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.angle = 0
        self.animate()

    def animate(self):
        self.ax.cla()
        self.ax.set_facecolor("#1e1e2e")
        self.ax.set_title("Rotating Square", color="white")

        a = self.angle * math.pi / 180
        pts = np.array([[1,1,0],[-1,1,0],[-1,-1,0],[1,-1,0],[1,1,0]])

        Ry = np.array([[math.cos(a),0,math.sin(a)],
                       [0,1,0],
                       [-math.sin(a),0,math.cos(a)]])
        rotated = pts @ Ry.T

        self.ax.plot(rotated[:,0], rotated[:,1], rotated[:,2], color="#a78bfa", lw=2)
        self.ax.set_xlim(-2,2); self.ax.set_ylim(-2,2); self.ax.set_zlim(-2,2)
        self.canvas.draw()

        self.angle += 2
        self.after(30, self.animate)

# ==================== 4. ROTATE CUBE 3D ====================
class CubeView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e2e")
        master.title("Rotate Cube 3D")
        master.geometry("600x600")
        self.pack(fill="both", expand=True)

        self.fig = plt.Figure(figsize=(5, 5), facecolor="#1e1e2e")
        self.ax  = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.vertices = np.array([
            [-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
            [-1,-1, 1],[1,-1, 1],[1,1, 1],[-1,1, 1]
        ])
        self.edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]
        self.angle = 0
        self.animate()

    def animate(self):
        self.ax.cla()
        self.ax.set_facecolor("#1e1e2e")
        self.ax.set_title("Rotating Cube", color="white")

        a = self.angle * math.pi / 180
        Rx = np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
        Ry = np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
        R  = Rx @ Ry
        v  = self.vertices @ R.T

        for e in self.edges:
            xs = [v[e[0],0], v[e[1],0]]
            ys = [v[e[0],1], v[e[1],1]]
            zs = [v[e[0],2], v[e[1],2]]
            self.ax.plot(xs, ys, zs, color="#34d399", lw=2)

        self.ax.set_xlim(-2,2); self.ax.set_ylim(-2,2); self.ax.set_zlim(-2,2)
        self.canvas.draw()
        self.angle += 2
        self.after(30, self.animate)

# ==================== 5. ROCKETS TO MOON ====================
class RocketView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#0a0a1a")
        master.title("🚀 Rockets to Moon")
        master.geometry("700x750")
        self.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self, bg="#0a0a1a", width=700, height=700)
        self.canvas.pack()

        self.countdown = 5
        self.launched  = False
        self.r1_y = 620
        self.r2_y = 650
        self.r1_x = 250
        self.r2_x = 450
        self.moon_y = 80

        self.draw_stars()
        self.draw_moon()
        self.draw_rockets()
        self.show_countdown()
        self.init_music()

    def init_music(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("space.mp3")  # add your mp3 file
            pygame.mixer.music.play(-1)
        except:
            pass  # music file not found, skip

    def draw_stars(self):
        import random
        for _ in range(150):
            x = random.randint(0, 700)
            y = random.randint(0, 700)
            self.canvas.create_oval(x, y, x+2, y+2, fill="white", outline="")

    def draw_moon(self):
        self.moon = self.canvas.create_oval(300, self.moon_y, 400,
                                             self.moon_y+100,
                                             fill="#f5f3c1", outline="#e5e3a1", width=2)
        self.canvas.create_text(350, self.moon_y+50, text="🌕",
                                font=("Arial", 40))

    def draw_rocket(self, x, y, color, tag):
        self.canvas.create_polygon(
            x, y-40, x-15, y, x+15, y,
            fill=color, outline="white", tags=tag
        )
        self.canvas.create_rectangle(x-15, y, x+15, y+40,
                                      fill=color, outline="white", tags=tag)
        self.canvas.create_polygon(
            x-15, y+40, x-25, y+60, x+25, y+60, x+15, y+40,
            fill="#f97316", tags=tag
        )

    def draw_rockets(self):
        self.draw_rocket(self.r1_x, self.r1_y, "#7c3aed", "r1")
        self.draw_rocket(self.r2_x, self.r2_y, "#059669", "r2")

    def show_countdown(self):
        self.cd_text = self.canvas.create_text(350, 350, text=f"🚀 {self.countdown}",
                                               font=("Arial", 60, "bold"),
                                               fill="white")
        self.tick()

    def tick(self):
        if self.countdown > 0:
            self.canvas.itemconfig(self.cd_text, text=f"🚀 {self.countdown}")
            self.countdown -= 1
            self.after(1000, self.tick)
        else:
            self.canvas.itemconfig(self.cd_text, text="🔥 LAUNCH!")
            self.after(800, lambda: self.canvas.delete(self.cd_text))
            self.launched = True
            self.launch()

    def launch(self):
        if not self.launched:
            return

        # Move rockets up
        self.r1_y -= 3
        self.r2_y -= 3

        # Collision detection
        if abs(self.r1_x - self.r2_x) < 35 and abs(self.r1_y - self.r2_y) < 60:
            self.r1_x -= 2
            self.r2_x += 2

        self.canvas.delete("r1")
        self.canvas.delete("r2")
        self.draw_rocket(self.r1_x, self.r1_y, "#7c3aed", "r1")
        self.draw_rocket(self.r2_x, self.r2_y, "#059669", "r2")

        # Check if hit moon
        hit1 = self.r1_y <= self.moon_y + 100
        hit2 = self.r2_y <= self.moon_y + 100

        if hit1 and hit2:
            self.canvas.create_text(350, 350,
                                    text="🌕 Both Rockets Hit the Moon! 🎉",
                                    font=("Arial", 22, "bold"), fill="#fbbf24")
            messagebox.showinfo("🚀 Mission Complete!",
                                "Both rockets have reached the Moon! 🌕🎉")
            self.launched = False
            return
        elif hit1:
            self.canvas.create_text(200, 300, text="🚀 Rocket 1 Hit Moon!",
                                    font=("Arial", 14), fill="#a78bfa")
        elif hit2:
            self.canvas.create_text(500, 300, text="🚀 Rocket 2 Hit Moon!",
                                    font=("Arial", 14), fill="#34d399")

        if not (hit1 and hit2):
            self.after(16, self.launch)

# ==================== RUN ====================
if __name__ == "__main__":
    app = App()
    app.mainloop()