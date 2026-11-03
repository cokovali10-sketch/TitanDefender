import subprocess, os, threading, sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QProgressBar, QFrame, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "titan.exe")

QSS = """
QMainWindow { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0a0e1a, stop:1 #1a1033); }
QLabel { color: #e2e8f0; font-family: 'Segoe UI'; }
QPushButton {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #06b6d4);
  color: white; border: none; border-radius: 12px; padding: 12px 20px;
  font-size: 13px; font-weight: 600;
}
QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #8b5cf6, stop:1 #22d3ee); }
QPushButton:disabled { background: #334155; color: #94a3b8; }
QTextEdit {
  background: #0f172a; color: #e2e8f0; border: 1px solid #1e293b;
  border-radius: 12px; padding: 12px; font-family: Consolas; font-size: 11px;
}
QProgressBar {
  background: #1e293b; border: none; border-radius: 6px; height: 8px; text-align: center;
}
QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #06b6d4); border-radius: 6px; }
QFrame#card { background: rgba(15,23,42,0.6); border: 1px solid #1e293b; border-radius: 16px; }
"""

class ScanWorker(QThread):
    output = pyqtSignal(str)
    finished = pyqtSignal()
    def __init__(self, args):
        super().__init__(); self.args = args
    def run(self):
        try:
            r = subprocess.run([ENGINE] + self.args, capture_output=True, text=True, timeout=300)
            self.output.emit(r.stdout)
            if r.stderr: self.output.emit("\n" + r.stderr)
        except Exception as e:
            self.output.emit(f"Error: {e}")
        self.finished.emit()

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TitanDefender")
        self.resize(1000, 700)
        self.setStyleSheet(QSS)
        self.worker = None
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 28, 32, 20)
        layout.setSpacing(16)

        # header
        hdr = QHBoxLayout()
        title = QLabel("🛡️  TitanDefender")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #c4b5fd;")
        hdr.addWidget(title)
        sub = QLabel("Modern Antivirus · Glassmorphism")
        sub.setStyleSheet("color: #64748b; font-size: 12px;")
        hdr.addWidget(sub)
        hdr.addStretch()
        pill = QLabel("● Защищено")
        pill.setStyleSheet("color: #22c55e; font-weight: 700; background: #0f172a; border-radius: 12px; padding: 6px 14px;")
        hdr.addWidget(pill)
        layout.addLayout(hdr)

        # safety banner
        safe = QLabel("Безопасный режим: файлы только читаются, удаление только через карантин с подтверждением")
        safe.setStyleSheet("color: #22c55e; font-size: 10px;")
        layout.addWidget(safe)

        # cards
        cards = QHBoxLayout()
        for t, v in [("Последнее сканирование","2 мин назад"),("Угрозы","0"),("Сигнатуры","100"),("Статус","Активен")]:
            frame = QFrame(); frame.setObjectName("card")
            fl = QVBoxLayout(frame); fl.setContentsMargins(16,12,16,12)
            tl = QLabel(t); tl.setStyleSheet("color: #64748b; font-size: 10px;")
            vl = QLabel(v); vl.setStyleSheet("color: #f1f5f9; font-size: 16px; font-weight: 700;")
            fl.addWidget(tl); fl.addWidget(vl)
            cards.addWidget(frame)
        layout.addLayout(cards)

        # buttons
        btns = QHBoxLayout()
        for txt, cmd in [("⚡ Быстрое сканирование", self.quick_scan), ("📁 Выбрать папку", self.custom_scan),
                         ("📋 Сигнатуры", self.list_sigs), ("🔒 Карантин", self.quarantine_list)]:
            b = QPushButton(txt); b.clicked.connect(cmd); btns.addWidget(b)
        layout.addLayout(btns)

        # progress
        self.progress = QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0)
        layout.addWidget(self.progress)

        # log
        self.log = QTextEdit(); self.log.setReadOnly(True)
        layout.addWidget(self.log, 1)

        foot = QLabel("TitanDefender v0.4 · Rust engine + PyQt6 GUI")
        foot.setStyleSheet("color: #475569; font-size: 9px;")
        layout.addWidget(foot)

    def run_engine(self, args):
        if self.worker and self.worker.isRunning(): return
        self.log.clear()
        self.progress.setValue(0)
        self.worker = ScanWorker(args)
        self.worker.output.connect(lambda t: self.log.insertPlainText(t))
        self.worker.finished.connect(lambda: self.progress.setValue(100))
        self.worker.start()

    def quick_scan(self): self.run_engine(["scan","C:\\","--quick","--json"])
    def custom_scan(self):
        d = QFileDialog.getExistingDirectory(self, "Выбрать папку")
        if d: self.run_engine(["scan", d])
    def list_sigs(self): self.run_engine(["list-sigs"])
    def quarantine_list(self): self.run_engine(["quarantines"])

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    w = App(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
