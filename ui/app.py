import subprocess, os, threading
import tkinter as tk
from tkinter import filedialog

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "titan.exe")
ACCENT = "#8b5cf6"; ACCENT2 = "#06b6d4"; BG = "#080c18"; CARD = "#111827"; FG = "#f1f5f9"; MUTED = "#64748b"; BORDER = "#1e293b"

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, color=ACCENT, **kw):
        super().__init__(parent, height=42, highlightthickness=0, bg=parent["bg"], cursor="hand2", **kw)
        self.command = command; self.text = text; self.color = color; self.hover = False
        self.bind("<Enter>", lambda e: (setattr(self,"hover",True), self._draw()))
        self.bind("<Leave>", lambda e: (setattr(self,"hover",False), self._draw()))
        self.bind("<Button-1>", lambda e: command())
        self._draw()
    def _draw(self):
        self.delete("all")
        w = self.winfo_width() or 160
        h = 42
        r = 12
        c = "#a78bfa" if self.hover else self.color
        self.create_rounded_rect(2,2,w-2,h-2,r,fill=c,outline="")
        self.create_text(w//2, h//2, text=self.text, fill="white", font=("Segoe UI", 10, "bold"))
    def create_rounded_rect(self, x1,y1,x2,y2,r,**kw):
        self.create_arc(x1,y1,x1+2*r,y1+2*r,start=90,extent=90,style="pieslice",**kw)
        self.create_arc(x2-2*r,y1,x2,y1+2*r,start=0,extent=90,style="pieslice",**kw)
        self.create_arc(x1,y2-2*r,x1+2*r,y2,start=180,extent=90,style="pieslice",**kw)
        self.create_arc(x2-2*r,y2-2*r,x2,y2,start=270,extent=90,style="pieslice",**kw)
        self.create_rectangle(x1+r,y1,x2-r,y2,**kw)
        self.create_rectangle(x1,y1+r,x2,y2-r,**kw)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TitanDefender")
        self.geometry("980x680")
        self.configure(bg=BG)
        self.minsize(860, 560)
        self.running = False
        self._build()

    def _build(self):
        # header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=32, pady=(28, 6))
        tk.Label(hdr, text="🛡️", font=("Segoe UI Emoji", 34), fg=ACCENT, bg=BG).pack(side="left")
        box = tk.Frame(hdr, bg=BG)
        box.pack(side="left", padx=12)
        tk.Label(box, text="TitanDefender", font=("Segoe UI", 30, "bold"), fg="#c4b5fd", bg=BG).pack(anchor="w")
        tk.Label(box, text="Modern Antivirus · Glassmorphism", font=("Segoe UI", 11), fg=MUTED, bg=BG).pack(anchor="w")

        # status pill
        self.pill = tk.Label(self, text="  ● Защищено  ", font=("Segoe UI", 10, "bold"), fg="#22c55e", bg="#0f172a", padx=14, pady=6)
        self.pill.pack(anchor="w", padx=32, pady=(0,14))
        tk.Label(self, text="?????????? ?????: ????? ?????? ????????, ???????? ?????? ????? ???????? ? ??????????????", font=("Segoe UI", 9), fg="#22c55e", bg=BG).pack(anchor="w", padx=32, pady=(0,8))

        # cards
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", padx=32, pady=8)
        self.card_vals = {}
        for i,(t,v) in enumerate([("Последнее сканирование","2 мин назад"),("Угрозы","0"),("Сигнатуры","100"),("Статус","Активен")]):
            c = tk.Frame(cards, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            c.grid(row=0, column=i, padx=8, sticky="nsew")
            cards.columnconfigure(i, weight=1)
            tk.Label(c, text=t, font=("Segoe UI", 9), fg=MUTED, bg=CARD).pack(anchor="w", padx=16, pady=(12,2))
            lbl = tk.Label(c, text=v, font=("Segoe UI", 16, "bold"), fg=FG, bg=CARD)
            lbl.pack(anchor="w", padx=16, pady=(0,12))
            self.card_vals[t] = lbl

        # buttons
        btns = tk.Frame(self, bg=BG)
        btns.pack(fill="x", padx=32, pady=18)
        for i,(txt,cmd) in enumerate([("⚡ Быстрое сканирование", self.quick_scan),("📁 Выбрать папку", self.custom_scan),("📋 Сигнатуры", self.list_sigs),("🔒 Карантин", self.quarantine_list)]):
            b = RoundedButton(btns, txt, cmd)
            b.grid(row=0, column=i, padx=6, sticky="ew")
            btns.columnconfigure(i, weight=1)

        # progress
        self.progress = tk.Canvas(self, height=8, bg="#1e293b", highlightthickness=0)
        self.progress.pack(fill="x", padx=32, pady=(6,6))
        self.pbar = self.progress.create_rectangle(0,0,0,8, fill=ACCENT, width=0)
        self._prog = 0; self._target = 0
        self._animate()

        # log
        logframe = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        logframe.pack(fill="both", expand=True, padx=32, pady=12)
        self.log = tk.Text(logframe, bg=CARD, fg=FG, font=("Consolas", 10), relief="flat", borderwidth=0, padx=14, pady=14, insertbackground=FG)
        self.log.pack(fill="both", expand=True)

        tk.Label(self, text="TitanDefender v0.3 · Rust engine + Python GUI", font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(pady=8)

    def _animate(self):
        if self._prog < self._target:
            self._prog = min(self._prog + 4, self._target)
        w = self.progress.winfo_width()
        self.progress.coords(self.pbar, 0, 0, int(w*self._prog/100), 8)
        self.after(16, self._animate)

    def set_progress(self, v): self._target = v

    def run_engine(self, args):
        if self.running: return
        self.running = True
        self.set_progress(0)
        self.pill.config(text="  ● Сканирование...  ", fg="#f59e0b")
        self.log.delete("1.0", "end")
        def worker():
            try:
                r = subprocess.run([ENGINE]+args, capture_output=True, text=True, timeout=300)
                self.log.insert("end", r.stdout)
                if r.stderr: self.log.insert("end", "\n"+r.stderr)
                self.set_progress(100)
            except Exception as e:
                self.log.insert("end", f"Error: {e}")
            finally:
                self.running = False
                self.pill.config(text="  ● Готов  ", fg="#22c55e")
        threading.Thread(target=worker, daemon=True).start()
        def tick():
            if self.running and self._target < 95:
                self.set_progress(self._target + 2)
                self.after(250, tick)
        self.after(250, tick)

    def quick_scan(self): self.run_engine(["scan","C:\\","--quick","--json"])
    def custom_scan(self):
        d = filedialog.askdirectory()
        if d: self.run_engine(["scan", d])
    def list_sigs(self): self.run_engine(["list-sigs"])
    def quarantine_list(self): self.run_engine(["quarantines"])

if __name__ == "__main__":
    App().mainloop()
