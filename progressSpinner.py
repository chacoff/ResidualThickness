import math, sys
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import *
from PyQt6.QtWidgets import QWidget, QMainWindow, QTextEdit, QGridLayout, QApplication, QPushButton


class Overlay(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        palette = QPalette()
        self.setPalette(palette)
        self.timer = None
        self.counter = None
        self.emitter = EmitSignal()
        self.receiver = ReceiveSignal()

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 0)))  # last value is the halo for spinner
        painter.setPen(QPen(Qt.PenStyle.NoPen))

        for i in range(8):

            if (self.counter / 5) % 8 == i:
                painter.setBrush(QBrush(QColor(207 + (self.counter % 5) * 32, 120, 27)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))

            painter.drawEllipse(self.width() / 2 + 25 * math.cos(2 * math.pi * i / 8.0) - 5,
                                self.height() / 2 + 25 * math.sin(2 * math.pi * i / 8.0) - 5,
                                16, 16)

        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(25)
        self.counter = 0

    def timerEvent(self, event):
        self.counter += 1
        self.update()
        self.emitter.signal.connect(self.receiver.update_status)
        if self.counter == 40 or self.receiver.get_status():
            print(self.receiver.get_status())
            self.killTimer(self.timer)
            self.hide()
            self.receiver.set_status(False)


class EmitSignal(QWidget):
    signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def trigger_signal(self):
        self.emit_signal()

    def emit_signal(self):
        self.signal.emit(True)
        print("Emitted signal")


class ReceiveSignal(QWidget):
    def __init__(self):
        super().__init__()
        self.status: bool = False

    def update_status(self, message) -> None:
        self.status = message

    def get_status(self) -> bool:
        return self.status

    def set_status(self, status: bool) -> None:
        self.status = status

