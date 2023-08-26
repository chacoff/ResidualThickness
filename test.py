import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtGui, QtCore

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = pg.PlotWidget()
    plot_item = win.plot([1, 3, 2, 4, 3, 5], symbol='o')
    hover_label = pg.LabelItem(justify='right')


    def mouse_moved(evt):
        pos = evt[0]  # using the first mouse event
        if plot_item.sceneBoundingRect().contains(pos):
            mouse_point = plot_item.getViewBox().mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()
            hover_label.setText(f"X: {x:.2f}, Y: {y:.2f}")
            hover_label.setPos(mouse_point)


    plot_item.scene().sigMouseMoved.connect(mouse_moved)

    win.addItem(hover_label)
    win.show()
    sys.exit(app.exec())
