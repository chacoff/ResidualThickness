import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import numpy as np


class SecondGraphWindow(QMainWindow):
    def __init__(self, x, y):
        super().__init__()

        self.setWindowTitle("Second Graph")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        self.plot_widget.plot(x, y)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQtGraph Example")
        self.setGeometry(100, 100, 800, 600)

        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        self.open_windows = []  # List to keep track of open SecondGraphWindow instances

        self.plot_widget.scene().sigMouseClicked.connect(self.plot_clicked)

    def plot_clicked(self, event):
        if event.double():
            pos = event.pos()
            clicked_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)

            # Example data for the second graph
            x = np.linspace(clicked_point.x() - 5, clicked_point.x() + 5, 100)
            y = np.sin(x)

            existing_window = None
            for window in self.open_windows:
                if not window.isVisible():
                    existing_window = window
                    break

            if existing_window is None:
                new_window = SecondGraphWindow(x, y)
                self.open_windows.append(new_window)
                new_window.show()
            else:
                existing_window.centralWidget().plot_widget.clear()
                existing_window.centralWidget().plot_widget.plot(x, y)
                existing_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
