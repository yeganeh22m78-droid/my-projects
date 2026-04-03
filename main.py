import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import math
import time
import pygame
import os

# ============================================================================
# DATABASE SETUP
# ============================================================================
class Database:
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            hashed_pw = self.hash_password(password)
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                         (username, hashed_pw))
            conn.commit()
            return True, "Registration successful!"
        except sqlite3.IntegrityError:
            return False, "Username already exists!"
        finally:
            conn.close()

    def authenticate_user(self, username, password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        hashed_pw = self.hash_password(password)
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                      (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()
        return user is not None

# ============================================================================
# LOGIN VIEW
# ============================================================================
class LoginView(tk.Frame):
    def __init__(self, parent, callback):
        super().__init__(parent, bg="#1e1e2e")
        self.parent = parent
        self.callback = callback
        self.db = Database()
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self, text="🔐 Login / Register", 
                              font=("Arial", 24, "bold"), 
                              bg="#1e1e2e", fg="#a78bfa")
        title_label.pack(pady=30)

        # Username
        tk.Label(self, text="Username:", bg="#1e1e2e", fg="white",
                font=("Arial", 12)).pack(pady=5)
        self.username_entry = tk.Entry(self, font=("Arial", 12), 
                                       bg="#2d2d3f", fg="white", width=30)
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(self, text="Password:", bg="#1e1e2e", fg="white",
                font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(self, font=("Arial", 12), 
                                       bg="#2d2d3f", fg="white", width=30, show="•")
        self.password_entry.pack(pady=5)

        # Buttons
        button_frame = tk.Frame(self, bg="#1e1e2e")
        button_frame.pack(pady=20)

        login_btn = tk.Button(button_frame, text="Login", bg="#7c3aed", 
                             fg="white", font=("Arial", 12, "bold"),
                             width=15, command=self.login)
        login_btn.pack(side="left", padx=10)

        register_btn = tk.Button(button_frame, text="Register", bg="#34d399", 
                                fg="white", font=("Arial", 12, "bold"),
                                width=15, command=self.register)
        register_btn.pack(side="left", padx=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        if self.db.authenticate_user(username, password):
            messagebox.showinfo("Success", f"Welcome {username}!")
            self.callback(username)
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        success, message = self.db.register_user(username, password)
        if success:
            messagebox.showinfo("Success", message)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)

# ============================================================================
# MATRIX CALCULATOR VIEW
# ============================================================================
class MatrixCalculatorView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self, text="🔢 Matrix Calculator (3x3)", 
                        font=("Arial", 18, "bold"), bg="#1e1e2e", fg="#a78bfa")
        title.pack(pady=10)

        # Main container
        main_frame = tk.Frame(self, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True)

        # Matrix A
        tk.Label(main_frame, text="Matrix A", bg="#1e1e2e", fg="#a78bfa",
                font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20, pady=5)
        self.matrix_a = [[tk.Entry(main_frame, width=5, font=("Arial", 10),
                                   bg="#2d2d3f", fg="white", justify="center")
                         for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.matrix_a[i][j].insert(0, str(np.random.randint(1, 10)))
                self.matrix_a[i][j].grid(row=i+1, column=j, padx=5, pady=3)

        # Matrix B
        tk.Label(main_frame, text="Matrix B", bg="#1e1e2e", fg="#34d399",
                font=("Arial", 12, "bold")).grid(row=0, column=3, padx=20, pady=5)
        self.matrix_b = [[tk.Entry(main_frame, width=5, font=("Arial", 10),
                                   bg="#2d2d3f", fg="white", justify="center")
                         for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.matrix_b[i][j].insert(0, str(np.random.randint(1, 10)))
                self.matrix_b[i][j].grid(row=i+1, column=j+3, padx=5, pady=3)

        # Buttons
        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(pady=15)

        for text, op in [("➕ Add", "add"), ("➖ Subtract", "sub"), ("✖ Multiply", "mul")]:
            tk.Button(btn_frame, text=text, bg="#7c3aed", fg="white",
                     font=("Arial", 11, "bold"), width=12,
                     command=lambda o=op: self.calculate(o)).pack(side="left", padx=5)

        # Result area
        tk.Label(self, text="Result:", bg="#1e1e2e", fg="white",
                font=("Arial", 12, "bold")).pack(pady=(15, 5))

        self.result_text = tk.Text(self, height=8, width=50, bg="#2d2d3f", 
                                   fg="#34d399", font=("Courier", 11))
        self.result_text.pack(pady=5)

    def get_matrix(self, entries):
        try:
            return np.array([[float(entries[i][j].get()) for j in range(3)] for i in range(3)])
        except:
            messagebox.showerror("Error", "Invalid input! Please enter numbers only.")
            return None

    def calculate(self, operation):
        mat_a = self.get_matrix(self.matrix_a)
        mat_b = self.get_matrix(self.matrix_b)

        if mat_a is None or mat_b is None:
            return

        self.result_text.delete(1.0, tk.END)

        if operation == "add":
            result = mat_a + mat_b
            self.result_text.insert(tk.END, "Matrix A + Matrix B:\n\n")
        elif operation == "sub":
            result = mat_a - mat_b
            self.result_text.insert(tk.END, "Matrix A - Matrix B:\n\n")
        elif operation == "mul":
            result = np.dot(mat_a, mat_b)
            self.result_text.insert(tk.END, "Matrix A × Matrix B:\n\n")

        for row in result:
            self.result_text.insert(tk.END, "  " + "  ".join(f"{val:7.2f}" for val in row) + "\n")

# ============================================================================
# 3D VISUALIZATIONS
# ============================================================================
class Rotating3DView(tk.Frame):
    def __init__(self, parent, shape_type="square"):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.shape_type = shape_type
        self.angle = 0
        self.is_running = True
        self.create_widgets()
        self.animate()

    def create_widgets(self):
        title = "3D Rotating Square" if self.shape_type == "square" else "3D Rotating Cube"
        tk.Label(self, text=f"📐 {title}", font=("Arial", 16, "bold"),
                bg="#1e1e2e", fg="#a78bfa").pack(pady=10)

        self.fig = Figure(figsize=(6, 5), dpi=100, facecolor="#1e1e2e")
        self.ax = self.fig.add_subplot(111, projection="3d", facecolor="#1e1e2e")
        self.ax.set_facecolor("#1e1e2e")
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_zlim(-2, 2)
        self.ax.set_xlabel("X", color="white")
        self.ax.set_ylabel("Y", color="white")
        self.ax.set_zlabel("Z", color="white")
        self.ax.tick_params(colors="white")

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def rotate_point(self, p, angle):
        """Rotate point around all axes"""
        cx, cy, cz = np.cos(angle), np.cos(angle), np.cos(angle)
        sx, sy, sz = np.sin(angle), np.sin(angle), np.sin(angle)

        # Rotation around X
        p = np.array([p[0], p[1] * cx - p[2] * sx, p[1] * sx + p[2] * cx])
        # Rotation around Y
        p = np.array([p[0] * cx + p[2] * sx, p[1], -p[0] * sx + p[2] * cx])
        return p

    def animate(self):
        if not self.is_running:
            return

        self.ax.clear()
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_zlim(-2, 2)
        self.ax.set_facecolor("#1e1e2e")

        if self.shape_type == "square":
            self.draw_square()
        else:
            self.draw_cube()

        self.angle += 0.05
        self.canvas.draw()
        self.after(50, self.animate)

    def draw_square(self):
        points = np.array([[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]])
        rotated = np.array([self.rotate_point(p, self.angle) for p in points])
        rotated = np.vstack([rotated, rotated[0]])
        self.ax.plot(rotated[:, 0], rotated[:, 1], rotated[:, 2], "b-", linewidth=2)
        self.ax.scatter(rotated[:-1, 0], rotated[:-1, 1], rotated[:-1, 2], c="cyan", s=50)

    def draw_cube(self):
        vertices = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                           [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]])
        rotated = np.array([self.rotate_point(v, self.angle) for v in vertices])

        edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4),
                (0,4), (1,5), (2,6), (3,7)]

        for edge in edges:
            points = rotated[list(edge)]
            self.ax.plot(points[:, 0], points[:, 1], points[:, 2], "g-", linewidth=2)

        self.ax.scatter(rotated[:, 0], rotated[:, 1], rotated[:, 2], c="lime", s=50)

    def stop(self):
        self.is_running = False

# ============================================================================
# ROCKET SIMULATION
# ============================================================================
class RocketView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.is_running = False
        self.init_sounds()
        self.create_widgets()

    def init_sounds(self):
        """Initialize pygame mixer and create sound effects"""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            # Create sound effects
            self.launch_sound = self.create_launch_sound()
            self.flying_sound = self.create_flying_sound()
            self.landing_sound = self.create_landing_sound()
        except Exception as e:
            print(f"Sound initialization error: {e}")
            self.launch_sound = None
            self.flying_sound = None
            self.landing_sound = None

    def create_launch_sound(self):
        """Generate a rocket launch sound effect"""
        try:
            sample_rate = 22050
            duration = 2
            frequency = 200
            
            frames = int(sample_rate * duration)
            arr = np.zeros((frames, 2), dtype=np.int16)
            
            for i in range(frames):
                # Increasing frequency over time (pitch up)
                freq = 100 + (300 * i / frames)
                value = int(32767 * 0.3 * np.sin(2 * np.pi * freq * i / sample_rate))
                arr[i] = [value, value]
            
            sound = pygame.sndarray.make_sound(arr)
            return sound
        except:
            return None

    def create_flying_sound(self):
        """Generate rocket flying sound effect"""
        try:
            sample_rate = 22050
            duration = 0.5
            
            frames = int(sample_rate * duration)
            arr = np.zeros((frames, 2), dtype=np.int16)
            
            for i in range(frames):
                # White noise with frequency sweep
                noise = np.random.uniform(-1, 1)
                freq = 150 + (100 * i / frames)
                envelope = 1 - (i / frames)  # Fade out
                value = int(32767 * 0.2 * noise * envelope * np.sin(2 * np.pi * freq * i / sample_rate))
                arr[i] = [value, value]
            
            sound = pygame.sndarray.make_sound(arr)
            return sound
        except:
            return None

    def create_landing_sound(self):
        """Generate moon landing success sound"""
        try:
            sample_rate = 22050
            duration = 1
            
            frames = int(sample_rate * duration)
            arr = np.zeros((frames, 2), dtype=np.int16)
            
            # Play a sweet ascending note sequence
            notes = [440, 494, 523, 587]  # A, B, C, D
            frame_per_note = frames // len(notes)
            
            for n, freq in enumerate(notes):
                start = n * frame_per_note
                end = start + frame_per_note
                for i in range(start, end):
                    envelope = np.sin((i - start) / (end - start) * np.pi)
                    value = int(32767 * 0.3 * envelope * np.sin(2 * np.pi * freq * i / sample_rate))
                    arr[i] = [value, value]
            
            sound = pygame.sndarray.make_sound(arr)
            return sound
        except:
            return None

    def play_sound(self, sound):
        """Play a sound effect safely"""
        try:
            if sound and pygame.mixer.get_init():
                sound.play()
        except:
            pass

    def create_widgets(self):
        tk.Label(self, text="🚀 Rocket Launch Simulation", font=("Arial", 16, "bold"),
                bg="#1e1e2e", fg="#a78bfa").pack(pady=10)

        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor="#1e1e2e")
        self.ax = self.fig.add_subplot(111, facecolor="#1e1e2e")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Distance (km)", color="white")
        self.ax.set_ylabel("Altitude (km)", color="white")
        self.ax.set_title("🌙 Rocket to Moon Trajectory", color="white", fontsize=14)
        self.ax.tick_params(colors="white")
        self.ax.grid(True, alpha=0.3, color="gray")

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Control button
        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(pady=10)

        self.launch_btn = tk.Button(btn_frame, text="🚀 Launch Rocket", 
                                   bg="#7c3aed", fg="white", font=("Arial", 12, "bold"),
                                   width=20, command=self.launch_rocket)
        self.launch_btn.pack()

        # Info label
        self.info_label = tk.Label(self, text="", bg="#1e1e2e", fg="#34d399",
                                  font=("Arial", 10))
        self.info_label.pack(pady=5)

    def launch_rocket(self):
        if self.is_running:
            return

        self.is_running = True
        self.launch_btn.config(state="disabled")
        
        # Play launch sound
        self.play_sound(self.launch_sound)
        
        # Trajectory data
        self.time_points = np.linspace(0, 10, 100)
        self.x = 50 + 30 * np.sin(self.time_points)
        self.y = self.time_points * 10
        self.frame_index = 0
        self.sound_played = False
        
        self.animate_rocket()

    def animate_rocket(self):
        if self.frame_index >= len(self.time_points):
            # Play landing sound and show final message
            self.play_sound(self.landing_sound)
            self.info_label.config(text="✅ Rocket reached the Moon! 🌙")
            self.is_running = False
            self.launch_btn.config(state="normal")
            return

        i = self.frame_index
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_facecolor("#1e1e2e")
        self.ax.set_xlabel("Distance (km)", color="white")
        self.ax.set_ylabel("Altitude (km)", color="white")
        self.ax.set_title("🌙 Rocket to Moon Trajectory", color="white", fontsize=14)
        self.ax.tick_params(colors="white")
        self.ax.grid(True, alpha=0.3, color="gray")

        # Draw trajectory so far
        self.ax.plot(self.x[:i+1], self.y[:i+1], "r-", linewidth=2, label="Trajectory")

        # Draw rocket
        self.ax.scatter(self.x[i], self.y[i], s=200, c="yellow", marker="^", 
                      edgecolors="orange", linewidth=2, label="🚀 Rocket", zorder=5)

        # Draw moon
        self.ax.scatter(50, 100, s=500, c="white", alpha=0.7, label="🌙 Moon", zorder=3)

        # Draw Earth
        self.ax.scatter(50, 0, s=300, c="blue", alpha=0.5, label="🌍 Earth", zorder=3)

        self.ax.legend(loc="upper right", facecolor="#2d2d3f", edgecolor="white")

        altitude = self.y[i]
        distance = abs(self.x[i] - 50)
        status = "Ascending" if i < len(self.time_points) // 2 else "Descending"
        self.info_label.config(text=f"Altitude: {altitude:.1f} km | Distance: {distance:.1f} km | Status: {status}")

        # Play flying sound periodically
        if i % 5 == 0 and not self.sound_played:
            self.play_sound(self.flying_sound)
            self.sound_played = False
        if i % 5 != 0:
            self.sound_played = True

        self.canvas.draw()
        self.frame_index += 1
        self.after(100, self.animate_rocket)

# ============================================================================
# MAIN APPLICATION
# ============================================================================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚀 Advanced GUI Application - Matrix & 3D Visualizations")
        self.geometry("1000x700")
        self.configure(bg="#1e1e2e")
        self.current_user = None
        self.current_view = None
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
        except:
            pass
        self.show_login()

    def show_login(self):
        self.clear_frame()
        LoginView(self, self.on_login_success)

    def on_login_success(self, username):
        self.current_user = username
        self.show_menu()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_frame()

        # Header
        header = tk.Frame(self, bg="#0f0f1e")
        header.pack(fill="x", padx=0, pady=0)

        tk.Label(header, text=f"👤 Welcome, {self.current_user}!", 
                font=("Arial", 14, "bold"), bg="#0f0f1e", fg="#a78bfa").pack(side="left", padx=15, pady=10)

        logout_btn = tk.Button(header, text="Logout", bg="#f87171", fg="white",
                              font=("Arial", 10, "bold"), command=self.logout)
        logout_btn.pack(side="right", padx=15, pady=10)

        # Sidebar with buttons
        sidebar = tk.Frame(self, bg="#16213e", width=150)
        sidebar.pack(side="left", fill="y")

        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🔢 Matrix Calc", self.show_matrix),
            ("📐 3D Square", self.show_square),
            ("🧊 3D Cube", self.show_cube),
            ("🚀 Rocket", self.show_rocket),
        ]

        for text, command in buttons:
            tk.Button(sidebar, text=text, bg="#0f3460", fg="white",
                     font=("Arial", 11, "bold"), width=15, anchor="w",
                     command=command, relief="flat",
                     activebackground="#533483", activeforeground="white").pack(fill="x", padx=5, pady=5)

        # Content area
        self.content_frame = tk.Frame(self, bg="#1e1e2e")
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.show_dashboard()

    def show_dashboard(self):
        self.clear_content()
        dashboard = tk.Frame(self.content_frame, bg="#1e1e2e")
        dashboard.pack(fill="both", expand=True)

        title = tk.Label(dashboard, text="📊 Dashboard", font=("Arial", 20, "bold"),
                        bg="#1e1e2e", fg="#a78bfa")
        title.pack(pady=20)

        info_text = f"""
Welcome to your Advanced GUI Application!

Current User: {self.current_user}

Features Available:
  ✓ User Authentication (Login/Register)
  ✓ Matrix Calculator (3x3 operations)
  ✓ 3D Visualizations:
    - Rotating Square
    - Rotating Cube
  ✓ Rocket Launch Simulation
  ✓ Dark Modern Theme

Select a feature from the sidebar to get started!
        """

        tk.Label(dashboard, text=info_text, font=("Arial", 12), bg="#1e1e2e",
                fg="#34d399", justify="left").pack(padx=20, pady=20)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_matrix(self):
        self.clear_content()
        MatrixCalculatorView(self.content_frame)

    def show_square(self):
        self.clear_content()
        self.current_view = Rotating3DView(self.content_frame, "square")

    def show_cube(self):
        self.clear_content()
        self.current_view = Rotating3DView(self.content_frame, "cube")

    def show_rocket(self):
        self.clear_content()
        RocketView(self.content_frame)

    def logout(self):
        if self.current_view:
            self.current_view.stop()
        self.current_user = None
        self.show_login()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
