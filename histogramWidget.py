import pandas as pd
import sys
import csv
import numpy as np
import random
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QScreen, QColor, QPainter, QBrush, QFont
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
import math
import chardet
from parameters import UIParameters
from methods import Methods


class HistogramApp(QMainWindow):
    instances = []

    def __init__(self):
        super().__init__()
        self.data = None
        self._methods = Methods()
        self._params = UIParameters()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, self._params.histo_width, self._params.histo_height)

        layout = QVBoxLayout()
        self.central_widget = RoundedWidget()  # QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(layout)

        self.plot_widget = pg.PlotWidget()
        font = QFont()
        font.setPixelSize(8)
        for label in ['top', 'right', 'bottom', 'left']:
            # self.plot_widget.getPlotItem().hideAxis('bottom')
            self.plot_widget.setLabel(label, '')
            self.plot_widget.getAxis(label).setStyle(tickFont=font)

        self.title_histo = QLabel('')
        self.title_histo.setStyleSheet('''QLabel {font-size: 14px; font-weight: bold; color: #61605e;}''')

        self.plot_widget.showGrid(True, True, alpha=self._params.alpha_grid)
        self.plot_widget.setContentsMargins(0, 0, 0, 0)

        self.expand_button = QPushButton('Expand')
        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.close_histo)
        self.export_button = QPushButton('Export data')
        self.export_button.clicked.connect(self.export_histo)
        self.save_graph_button = QPushButton('Save Graph')
        self.save_graph_button.clicked.connect(self.export_histo_image)

        menu = QHBoxLayout()
        menu.addWidget(self.expand_button)
        menu.addWidget(self.export_button)
        menu.addWidget(self.save_graph_button)
        menu.addWidget(self.close_button)
        menu.setContentsMargins(0, 0, 8, 0)
        menu_w = QWidget()
        menu_w.setLayout(menu)

        layout.addWidget(self.title_histo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.plot_widget)
        layout.addWidget(menu_w)

        self.setWindowTitle('histogram')
        self.instances.append(self)

    def plot_histogram(self, data: pd, _range: tuple, i: int, j: int):
        self.data = data

        _brush = [253, 127, 63, random.randint(140, 200)]  # blue: 52, 93, 205

        hist, bins = np.histogram(self.data.x, bins=25)

        self.plot_widget.clear()

        bin_centers = (bins[:-1] + bins[1:]) / 2
        bars = pg.BarGraphItem(x=bin_centers,
                               height=hist,
                               width=(bins[1] - bins[0]),
                               brush=_brush)
        self.plot_widget.addItem(bars)

        freqs = []
        for bin_center, freq in zip(bin_centers, hist):
            text_item = pg.TextItem(f'{freq}', anchor=(0.5, 0), color=(252, 255, 252))
            self.plot_widget.addItem(text_item)
            text_item.setPos(bin_center, freq)
            freqs.append(freq)

        self.plot_widget.plotItem.vb.setLimits(xMin=self._params.histo_x_min,
                                               xMax=self._params.histo_x_max,
                                               yMin=self._params.histo_y_min,
                                               yMax=max(freqs))

        self.title_histo.setText(f'Elevation range: {_range}')
        # legend = self.plot_widget.addLegend()
        # legend.addItem(bars, f'Range {_range}')

        j = self._methods.fixer_for_j(j)
        self.move(i+self._params.histo_width_offset, j)
        self.show()

    def center_on_screen(self):
        available_geometry = QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.geometry()

        x = (available_geometry.width() - window_geometry.width()) // 2
        y = (available_geometry.height() - window_geometry.height()) // 2

        self.move(x, y)

    def export_histo(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data", "There is no data to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Histogram Data", os.getenv('HOME'), "CSV Files (*.csv)")

        if file_path:
            hist, bins = np.histogram(self.data.x, bins=25)
            bin_centers = (bins[:-1] + bins[1:]) / 2

            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Bin Center", "Frequency"])
                for bin_center, freq in zip(bin_centers, hist):
                    writer.writerow([bin_center, freq])

            # QMessageBox.information(self, "Export Successful", f"Histogram data has been exported to {file_path}.")

    def export_histo_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Histogram Image", os.getenv('HOME'),
                                                   "PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp)")

        if file_path:
            exporter = ImageExporter(self.plot_widget.plotItem)

            original_width = exporter.parameters()['width']
            exporter.parameters()['width'] = original_width * 4

            exporter.export(file_path)
            # QMessageBox.information(self, "Export Successful", f"Histogram image has been saved to {file_path}.")

    def close_histo(self) -> None:
            self.close()


class RoundedWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._params = UIParameters()

    def paintEvent(self, event):
        """" override paintEvent"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        brush = QBrush(QColor(248, 249, 252, 160))  # Background color with transparency
        painter.setBrush(brush)
        painter.drawRoundedRect(self.rect(), self._params.rounded_corner, self._params.rounded_corner)  # Rounded corners
