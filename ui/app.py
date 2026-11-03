import subprocess, os, threading, sys, json, datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QProgressBar, QFrame, QFileDialog, QStackedWidget, QLineEdit,
    QCheckBox, QComboBox, QSpinBox, QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "titan.exe")
HISTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scan_history.json")
SETTINGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "settings.json")

QSS = """
QMainWindow { background: #0a0e1a; }
QWidget { color: #e2e8f0; font-family: 'Segoe UI'; }
QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #06b6d4); color: white; border: none; border-radius: 10px; padding: 10px 18px; font-weight: 600; }
QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #8b5cf6, stop:1 #22d3ee); }
QPushButton:disabled { background: #1e293b; color: #64748b; }
QPushButton.nav { background: transparent; border: none; text-align: left; padding: 12px 16px; border-radius: 8px; color: #94a3b8; }
QPushButton.nav:hover { background: #1e293b; color: #e2e8f0; }
QPushButton.nav[active="true"] { background: #7c3aed; color: white; }
QPushButton.secondary { background: #1e293b; color: #e2e8f0; }
QPushButton.secondary:hover { background: #334155; }
QTextEdit { background: #0f172a; color: #e2e8f0; border: 1px solid #1e293b; border-radius: 12px; padding: 12px; font-family: Consolas; font-size: 11px; }
QProgressBar { background: #1e293b; border: none; border-radius: 6px; height: 8px; }
QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #06b6d4); border-radius: 6px; }
QFrame#card { background: #111827; border: 1px solid #1e293b; border-radius: 16px; }
QLabel#title { font-size: 26px; font-weight: 800; color: #c4b5fd; }
QLabel#muted { color: #64748b; font-size: 11px; }
QCheckBox { color: #e2e8f0; spacing: 8px; }
QComboBox { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 8px; padding: 6px 12px; }
QSpinBox { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 8px; padding: 6px; }
"""

class ScanWorker(QThread):
    output = pyqtSignal(str); finished = pyqtSignal()
    def __init__(self, args):
        super().__init__(); self.args = args
    def run(self):
        try:
            r = subprocess.run([ENGINE] + self.args, capture_output=True, text=True, timeout=300)
            self.output.emit(r.stdout or "")
            if r.stderr: self.output.emit("\n" + r.stderr)
            self._save(r.stdout)
        except Exception as e:
            self.output.emit(f"Error: {e}")
        self.finished.emit()
    def _save(self, out):
        try:
            data = []
            if os.path.exists(HISTORY):
                data = json.load(open(HISTORY, encoding="utf-8"))
            data.append({"time": datetime.datetime.now().isoformat(), "args": self.args, "output": (out or "")[:1500]})
            json.dump(data[-100:], open(HISTORY, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        except Exception: pass

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TitanDefender")
        self.resize(1180, 760)
        self.setStyleSheet(QSS)
        self.worker = None
        self.settings = self._load_settings()
        self._build()
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick_status); self._timer.start(5000)

    def _load_settings(self):
        try:
            return json.load(open(SETTINGS, encoding="utf-8"))
        except Exception:
            return {"realtime": True, "autoupdate": True, "safemode": True, "schedule": "off", "interval": 60}

    def _save_settings(self):
        try:
            json.dump(self.settings, open(SETTINGS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        except Exception: pass

    def _build(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QHBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        side = QWidget(); side.setFixedWidth(230); side.setStyleSheet("background: #080c18;")
        sl = QVBoxLayout(side); sl.setContentsMargins(12,20,12,20); sl.setSpacing(4)
        logo = QLabel("🛡️  TitanDefender"); logo.setStyleSheet("font-size: 18px; font-weight: 800; color: #c4b5fd; padding: 8px;")
        sl.addWidget(logo)
        sl.addSpacing(12)
        self.nav_btns = {}
        for key, txt in [("dashboard","📊  Панель"),("scan","🔍  Сканирование"),("deep","🔬  Глубокий скан"),("optimize","⚡  Оптимизация"),("quarantine","🔒  Карантин"),("history","📜  История"),("settings","⚙️  Настройки")]:
            b = QPushButton(txt); b.setProperty("class","nav"); b.clicked.connect(lambda _, k=key: self.switch(k))
            sl.addWidget(b); self.nav_btns[key] = b
        sl.addStretch()
        self.status_pill = QLabel("● Защищено")
        self.status_pill.setStyleSheet("color: #22c55e; font-size: 10px; padding: 8px;")
        sl.addWidget(self.status_pill)
        root.addWidget(side)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.pages = {}
        self.pages["dashboard"] = self._dashboard_page()
        self.pages["scan"] = self._scan_page()
        self.pages["deep"] = self._deep_page()
        self.pages["optimize"] = self._optimize_page()
        self.pages["quarantine"] = self._quarantine_page()
        self.pages["whitelist"] = self._whitelist_page()
        self.pages["history"] = self._history_page()
        self.pages["settings"] = self._settings_page()
        for k, p in self.pages.items():
            self.stack.addWidget(p)
        self.switch("dashboard")

    def switch(self, key):
        for k, b in self.nav_btns.items():
            b.setProperty("active", "true" if k == key else "false")
            b.style().unpolish(b); b.style().polish(b)
        self.stack.setCurrentWidget(self.pages[key])

    def _card(self, layout, title, value):
        f = QFrame(); f.setObjectName("card")
        fl = QVBoxLayout(f); fl.setContentsMargins(16,12,16,12)
        tl = QLabel(title); tl.setStyleSheet("color: #64748b; font-size: 10px;")
        vl = QLabel(value); vl.setStyleSheet("color: #f1f5f9; font-size: 16px; font-weight: 700;")
        fl.addWidget(tl); fl.addWidget(vl)
        layout.addWidget(f)

    def _dashboard_page(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(24,24,24,24); l.setSpacing(16)
        t = QLabel("Панель управления"); t.setObjectName("title"); l.addWidget(t)
        cards = QHBoxLayout()
        last = "—"
        threats = 0
        try:
            data = json.load(open(HISTORY, encoding="utf-8"))
            if data:
                last = data[-1]["time"][:19].replace("T"," ")
                threats = sum(d.get("output","").count("THREAT") for d in data)
        except Exception: pass
        try:
            import psutil
            cpu = f"{psutil.cpu_percent()}%"
            mem = f"{psutil.virtual_memory().percent}%"
        except Exception:
            cpu = "n/a"; mem = "n/a"
        for tt, vv in [("????????? ????????????", last),("????? ???????", str(threats)),("CPU", cpu),("??????", mem)]:
            self._card(cards, tt, vv)
        l.addLayout(cards)
        qa = QHBoxLayout()
        b1 = QPushButton("⚡ Оптимизировать ПК"); b1.clicked.connect(lambda: (self.switch("optimize"), self.optimize()))
        b2 = QPushButton("🔬 Глубокий скан"); b2.clicked.connect(lambda: self.switch("deep"))
        b3 = QPushButton("📤 Экспорт отчёта"); b3.clicked.connect(self.export_report)
        b3.setProperty("class","secondary")
        qa.addWidget(b1); qa.addWidget(b2); qa.addWidget(b3); qa.addStretch()
        l.addLayout(qa)
        l.addStretch()
        return w

    def export_report(self):
        try:
            data = json.load(open(HISTORY, encoding="utf-8")) if os.path.exists(HISTORY) else []
            path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчёт", "report.json", "JSON (*.json)")
            if path:
                json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Готово", f"Отчёт сохранён: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def _scan_page(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(24,24,24,24); l.setSpacing(12)
        t = QLabel("Сканирование"); t.setObjectName("title"); l.addWidget(t)
        btns = QHBoxLayout()
        for txt, cmd in [("⚡ Быстрое сканирование", self.quick_scan), ("📁 Выбрать папку", self.custom_scan), ("📋 Сигнатуры", self.list_sigs), ("🔒 Карантин", self.quarantine_list)]:
            b = QPushButton(txt); b.clicked.connect(cmd); btns.addWidget(b)
        l.addLayout(btns)
        self.progress = QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0)
        l.addWidget(self.progress)
        self.log = QTextEdit(); self.log.setReadOnly(True)
        l.addWidget(self.log, 1)
        return w

    def _deep_page(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(24,24,24,24); l.setSpacing(12)
        t = QLabel("Глубокий скан"); t.setObjectName("title"); l.addWidget(t)
        row = QHBoxLayout()
        self.deep_path = QLabel("C:\\"); row.addWidget(self.deep_path)
        b = QPushButton("Выбрать папку"); b.clicked.connect(self.pick_deep); row.addWidget(b)
        b2 = QPushButton("Запустить"); b2.clicked.connect(self.deep_scan); row.addWidget(b2)
        l.addLayout(row)
        self.dlog = QTextEdit(); self.dlog.setReadOnly(True); l.addWidget(self.dlog, 1)
        return w
    def pick_deep(self):
        d = QFileDialog.getExistingDirectory(self, "Папка для глубокого скана")
        if d: self.deep_path.setText(d)
    def deep_scan(self):
        self.switch("deep")
        self.run_engine(["deep-scan", self.deep_path.text()], target=self.dlog)

    def _optimize_page(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(24,24,24,24); l.setSpacing(12)
        t = QLabel("Оптимизация ПК"); t.setObjectName("title"); l.addWidget(t)
        b = QPushButton("Анализировать"); b.clicked.connect(self.optimize); l.addWidget(b)
        self.olog = QTextEdit(); self.olog.setReadOnly(True); l.addWidget(self.olog, 1)
        return w
    def optimize(self):
        self.switch("optimize")
        self.run_engine(["optimize"], target=self.olog)

    def _quarantine_page(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(24,24,24,24)
        t = QLabel("Карантин"); t.setObjectName("title"); l.addWidget(t)
        b = QPushButton("Обновить список"); b.clicked.connect(self.quarantine_list); l.addWidget(b)
        self.qlog = QTextEdit(); self.qlog.setReadOnly(True); l.addWidget(self.qlog, 1)
        return w

    def _whitelist_page(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(24,24,24,24); l.setSpacing(12)
        t = QLabel("?????????? (whitelist)"); t.setObjectName("title"); l.addWidget(t)
        row = QHBoxLayout()
        self.wl_input = QLineEdit(); self.wl_input.setPlaceholderText("??? SHA256 ??? ?????????? ? ??????????")
        row.addWidget(self.wl_input)
        b = QPushButton("????????"); b.clicked.connect(self.add_whitelist); row.addWidget(b)
        l.addLayout(row)
        self.wl_log = QTextEdit(); self.wl_log.setReadOnly(True); l.addWidget(self.wl_log, 1)
        return w
    def add_whitelist(self):
        h = self.wl_input.text().strip()
        if h:
            self.run_engine(["whitelist-add", h], target=self.wl_log)
            self.wl_input.clear()

    def _history_page(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(24,24,24,24)
        t = QLabel("История сканирований"); t.setObjectName("title"); l.addWidget(t)
        b = QPushButton("Загрузить"); b.clicked.connect(self.load_history); l.addWidget(b)
        self.hlog = QTextEdit(); self.hlog.setReadOnly(True); l.addWidget(self.hlog, 1)
        return w

    def _settings_page(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(24,24,24,24); l.setSpacing(12)
        t = QLabel("Настройки"); t.setObjectName("title"); l.addWidget(t)
        self.cb_realtime = QCheckBox("Real-time защита"); self.cb_realtime.setChecked(self.settings.get("realtime", True))
        self.cb_realtime.stateChanged.connect(lambda s: (self.settings.update({"realtime": bool(s)}), self._save_settings()))
        l.addWidget(self.cb_realtime)
        self.cb_autoupdate = QCheckBox("Автообновление сигнатур"); self.cb_autoupdate.setChecked(self.settings.get("autoupdate", True))
        self.cb_autoupdate.stateChanged.connect(lambda s: (self.settings.update({"autoupdate": bool(s)}), self._save_settings()))
        l.addWidget(self.cb_autoupdate)
        self.cb_safe = QCheckBox("Безопасный режим (только чтение)"); self.cb_safe.setChecked(self.settings.get("safemode", True))
        self.cb_safe.stateChanged.connect(lambda s: (self.settings.update({"safemode": bool(s)}), self._save_settings()))
        l.addWidget(self.cb_safe)
        row = QHBoxLayout()
        row.addWidget(QLabel("Расписание сканирования:"))
        self.combo_sched = QComboBox(); self.combo_sched.addItems(["off","daily","weekly"])
        self.combo_sched.setCurrentText(self.settings.get("schedule","off"))
        self.combo_sched.currentTextChanged.connect(lambda v: (self.settings.update({"schedule": v}), self._save_settings()))
        row.addWidget(self.combo_sched)
        l.addLayout(row)
        l.addStretch()
        return w

    def _tick_status(self):
        self.status_pill.setText("● Защищено" if self.settings.get("realtime", True) else "● Real-time выкл")

    def run_engine(self, args, target=None):
        if self.worker and self.worker.isRunning(): return
        target = target or self.log
        target.clear()
        self.progress.setValue(0)
        self.worker = ScanWorker(args)
        self.worker.output.connect(lambda t: target.insertPlainText(t))
        self.worker.finished.connect(lambda: self.progress.setValue(100))
        self.worker.start()
        def tick():
            if self.worker.isRunning() and self.progress.value() < 95:
                self.progress.setValue(self.progress.value() + 2)
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(250, tick)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(250, tick)

    def quick_scan(self): self.run_engine(["scan","C:\\","--quick","--json"])
    def custom_scan(self):
        d = QFileDialog.getExistingDirectory(self, "Выбрать папку")
        if d: self.run_engine(["scan", d])
    def list_sigs(self): self.run_engine(["list-sigs"])
    def yara_scan(self):
        d = QFileDialog.getExistingDirectory(self, "????? ??? YARA-?????")
        if d: self.run_engine(["yara-scan", d])
    def quarantine_list(self):
        self.switch("quarantine")
        self.run_engine(["quarantines"], target=self.qlog)
    def restore_quarantine(self):
        name = self.restore_input.text().strip()
        if name: self.run_engine(["quarantine-restore", name], target=self.qlog)
    def delete_quarantine(self):
        name = self.restore_input.text().strip()
        if name: self.run_engine(["quarantine-delete", name], target=self.qlog)
    def load_history(self):
        try:
            data = json.load(open(HISTORY, encoding="utf-8"))
            self.hlog.clear()
            for e in reversed(data):
                self.hlog.append(f"[{e['time']}] {e['args']}\n{e['output'][:300]}\n{'-'*40}")
        except Exception as ex:
            self.hlog.setPlainText(f"Нет истории: {ex}")

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    w = App(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
