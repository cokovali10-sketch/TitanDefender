import subprocess, os, threading, time
import tkinter as tk
from tkinter import filedialog

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "titan.exe")
ACCENT = "#7c3aed"; ACCENT2 = "#22d3ee"; BG = "#0b0f1a"; CARD = "#131a2e"; FG = "#e2e8f0"; MUTED = "#64748b"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TitanDefender")
        self.geometry("960x640")
        self.configure(bg=BG)
        self.minsize(800, 500)
        self.running = False
        self._build()

    def _build(self):
        # header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 8))
        tk.Label(hdr, text="🛡️  TitanDefender", font=("Segoe UI", 26, "bold"), fg="#a78bfa", bg=BG).pack(side="left")
        tk.Label(hdr, text="Modern Antivirus", font=("Segoe UI", 11), fg=MUTED, bg=BG).pack(side="left", padx=14, pady=(10,0))

        # status pill
        self.pill = tk.Label(self, text="● Защищено", font=("Segoe UI", 11, "bold"), fg="#22c55e", bg="#0f172a", padx=16, pady=6)
        self.pill.pack(anchor="w", padx=28, pady=(0,12))

        # cards row
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", padx=28, pady=8)
        for i,(t,v) in enumerate([("Последнее сканирование","2 мин назад"),("Угрозы","0"),("База сигнатур","100"),("Статус","Активен")]):
            c = tk.Frame(cards, bg=CARD, highlightbackground="#1e293b", highlightthickness=1)
            c.grid(row=0, column=i, padx=6, sticky="nsew")
            cards.columnconfigure(i, weight=1)
            tk.Label(c, text=t, font=("Segoe UI", 9), fg=MUTED, bg=CARD).pack(anchor="w", padx=14, pady=(10,2))
            tk.Label(c, text=v, font=("Segoe UI", 14, "bold"), fg=FG, bg=CARD).pack(anchor="w", padx=14, pady=(0,10))

        # buttons
        btns = tk.Frame(self, bg=BG)
        btns.pack(fill="x", padx=28, pady=16)
        for i,(txt,cmd) in enumerate([("⚡ Быстрое сканирование", self.quick_scan),("📁 Выбрать папку", self.custom_scan),("📋 Сигнатуры", self.list_sigs),("🔒 Карантин", self.quarantine_list)]):
            b = tk.Button(btns, text=txt, command=cmd, bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                          relief="flat", padx=18, pady=10, cursor="hand2", activebackground="#6d28d9", bd=0)
            b.grid(row=0, column=i, padx=6, sticky="ew")
            btns.columnconfigure(i, weight=1)

        # progress
        self.progress = tk.Canvas(self, height=6, bg="#1e293b", highlightthickness=0)
        self.progress.pack(fill="x", padx=28, pady=(4,4))
        self.pbar = self.progress.create_rectangle(0,0,0,6, fill=ACCENT, width=0)
        self._prog_val = 0
        self._prog_target = 0
        self._animate_prog()

        # log
        logframe = tk.Frame(self, bg=CARD, highlightbackground="#1e293b", highlightthickness=1)
        logframe.pack(fill="both", expand=True, padx=28, pady=12)
        self.log = tk.Text(logframe, bg=CARD, fg=FG, font=("Consolas", 10), relief="flat", borderwidth=0, padx=12, pady=12)
        self.log.pack(fill="both", expand=True)

        # footer
        tk.Label(self, text="TitanDefender v0.2 · Rust engine + Python GUI", font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(pady=6)

    def _animate_prog(self):
        if self._prog_val < self._prog_target:
            self._prog_val = min(self._prog_val + 3, self._prog_target)
        elif self._prog_val > self._prog_target:
            self._prog_val = self._prog_target
        w = self.progress.winfo_width()
        self.progress.coords(self.pbar, 0, 0, int(w * self._prog_val / 100), 6)
        self.after(16, self._animate_prog)

    def set_progress(self, v):
        self._prog_target = v

    def run_engine(self, args):
        if self.running: return
        self.running = True
        self.set_progress(0)
        self.pill.config(text="● Сканирование...", fg="#f59e0b")
        self.log.delete("1.0", "end")
        def worker():
            try:
                r = subprocess.run([ENGINE] + args, capture_output=True, text=True, timeout=300)
                self.log.insert("end", r.stdout)
                if r.stderr: self.log.insert("end", "\n" + r.stderr)
                self.set_progress(100)
            except Exception as e:
                self.log.insert("end", f"Error: {e}")
            finally:
                self.running = False
                self.pill.config(text="● Готов", fg="#22c55e")
        threading.Thread(target=worker, daemon=True).start()
        # animate progress during scan
        def tick():
            if self.running and self._prog_target < 95:
                self.set_progress(self._prog_target + 2)
                self.after(200, tick)
        self.after(200, tick)

    def quick_scan(self):
        self.run_engine(["scan", "C:\\", "--quick", "--json"])

    def custom_scan(self):
        d = filedialog.askdirectory()
        if d: self.run_engine(["scan", d])

    def list_sigs(self):
        self.run_engine(["list-sigs"])

    def quarantine_list(self):
        self.run_engine(["quarantines"])

if __name__ == "__main__":
    App().mainloop()
