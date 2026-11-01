import subprocess, os, sys, threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "titan.exe")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TitanDefender")
        self.geometry("900x600")
        self.configure(bg="#0a0e1a")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._build()
        self.running = False

    def _build(self):
        top = tk.Frame(self, bg="#0a0e1a")
        top.pack(fill="x", padx=20, pady=20)
        tk.Label(top, text="TitanDefender", font=("Segoe UI", 28, "bold"), fg="#a78bfa", bg="#0a0e1a").pack(side="left")
        tk.Label(top, text="Modern Antivirus", font=("Segoe UI", 11), fg="#94a3b8", bg="#0a0e1a").pack(side="left", padx=12)

        btns = tk.Frame(self, bg="#0a0e1a")
        btns.pack(fill="x", padx=20, pady=10)
        self.mkbtn(btns, "Быстрое сканирование", self.quick_scan, 0)
        self.mkbtn(btns, "Выбрать папку", self.custom_scan, 1)
        self.mkbtn(btns, "Сигнатуры", self.list_sigs, 2)
        self.mkbtn(btns, "Карантин", self.quarantine_list, 3)

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=20, pady=10)

        self.log = tk.Text(self, bg="#111827", fg="#e2e8f0", font=("Consolas", 10), relief="flat", borderwidth=0)
        self.log.pack(fill="both", expand=True, padx=20, pady=10)

        self.status = tk.Label(self, text="Готов", bg="#0a0e1a", fg="#22c55e", font=("Segoe UI", 10))
        self.status.pack(pady=5)

    def mkbtn(self, parent, text, cmd, col):
        b = tk.Button(parent, text=text, command=cmd, bg="#7c3aed", fg="white", font=("Segoe UI", 10, "bold"),
                      relief="flat", padx=16, pady=8, cursor="hand2", activebackground="#6d28d9")
        b.grid(row=0, column=col, padx=6)

    def run_engine(self, args):
        if self.running: return
        self.running = True
        self.progress.start()
        self.status.config(text="Сканирование...", fg="#f59e0b")
        self.log.delete("1.0", "end")
        def worker():
            try:
                r = subprocess.run([ENGINE] + args, capture_output=True, text=True, timeout=300)
                self.log.insert("end", r.stdout)
                if r.stderr: self.log.insert("end", "\n" + r.stderr)
            except Exception as e:
                self.log.insert("end", f"Error: {e}")
            finally:
                self.progress.stop()
                self.running = False
                self.status.config(text="Готов", fg="#22c55e")
        threading.Thread(target=worker, daemon=True).start()

    def quick_scan(self):
        self.run_engine(["scan", "C:\\", "--quick"])

    def custom_scan(self):
        d = filedialog.askdirectory()
        if d: self.run_engine(["scan", d])

    def list_sigs(self):
        self.run_engine(["list-sigs"])

    def quarantine_list(self):
        self.run_engine(["quarantines"])

if __name__ == "__main__":
    App().mainloop()
