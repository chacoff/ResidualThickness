import pandas as pd
import sys
import csv
import numpy as np
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QGuiApplication, QScreen
import pyqtgraph as pg
import math


class Methods(object):

    @staticmethod
    def return_dataframe(file_name: str, skip: int) -> pd:
        """ return pandas dataframe with the data """

        df = pd.read_csv(file_name, sep=r',|;', engine='python', skiprows=skip, encoding='latin-1')
        if df.shape[1] > 9:
            n = df.shape[1] - 9
            df.drop(columns=df.columns[-n:], axis=1,  inplace=True)
        df.columns = ['Elevation', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5', 'Sensor6', 'Sensor7', 'Sensor8']

        return df

    @staticmethod
    def read_csv_header(file_name: str, limit_row: int, titles: list) -> list:
        """ read the header of a csv file and extract titles and parameters"""

        with open(file_name, "r") as file:
            csv_reader = csv.reader(file)

            row_count = 0
            csv_header_data = []
            for row in csv_reader:
                if row_count >= limit_row:
                    break

                if row_count in titles:
                    title_label = row[0].replace(";", "").replace("_", "")
                    # print(f'---{title_label}')
                else:
                    rows = row[0].split(":")
                    param = rows[0]
                    value = rows[1]
                    param_label = param.strip()
                    value_label = value.strip().replace(";", "")
                    csv_header_data.append((param_label, value_label))
                row_count += 1

        return csv_header_data
    
    @staticmethod
    def apply_filter(df1: pd, df2: pd, low_filter: float, high_filter: float, saturation: float) -> pd:
        """ returns a panda data frame with all the filters applied over the selected sensor data"""

        mask1 = df2.iloc[:, 1:] == saturation
        mask2 = df2.iloc[:, 1:] <= low_filter  # all below is True, i.e., afterwards NaN
        mask3 = df2.iloc[:, 1:] >= high_filter  # all above is True, i.e., afterwards NaN

        mask = mask1 | mask2 | mask3

        common_indices = df1.index.intersection(mask.index)
        common_columns = df1.columns.intersection(mask.columns)

        # Replace corresponding cells in df1 with NaN according mask
        df1.loc[common_indices, common_columns] = df1.loc[common_indices, common_columns].where(~mask)

        return df1

    @staticmethod
    def average_by_intervals(_x: list, _y: list, interval: int, min_elevation: int) -> pd:
        """ returns a new panda dataframe containing only the average according an interval"""
        data = {'x': _x,
                'y': _y}

        df = pd.DataFrame(data)

        elevation_bins = list(range(min_elevation, 0 + interval, interval))

        df['elevation_bin'] = pd.cut(df['y'], bins=elevation_bins, labels=elevation_bins[:-1])
        result = df.groupby('elevation_bin')['x'].apply(lambda x: np.nanmean(x)).reset_index()
        cols = ['x', 'elevation_bin']  # re-order to follow x, y
        result = result[cols]
        return result

    @staticmethod
    def generate_color():
        return [random.randint(0, 255) for _ in range(3)]

    @staticmethod
    def give_me_a_color(sensor: str):
        colors = {
            'Sensor1': [203, 65, 88],
            'Sensor2': [135, 38, 236],
            'Sensor3': [67, 233, 251],
            'Sensor4': [39, 144, 228],
            'Sensor5': [255, 128, 0],
            'Sensor6': [47, 147, 49],
            'Sensor7': [255, 0, 255],
            'Sensor8': [255, 0, 0],
        }

        return colors[sensor]

    @staticmethod
    def closest_point(x: float, y: float, average_data: list) -> list:
        closest_distance = float('inf')
        closest_point = None
        for point in average_data:
            distance = ((x - point[0]) ** 2 + (y - point[1]) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_point = point

        return closest_point

    @staticmethod
    def distance_to_point(a: list, b: list) -> int:
        return int(math.dist(a, b))

    @staticmethod
    def absolute_point_distance(a: list, b: list) -> bool:
        thresh = [0.10, 70]
        diff1 = [abs(a[0] - b[0]), abs(a[1] - b[1])]
        return diff1[0] < thresh[0] and diff1[1] < thresh[1]


class HistogramApp(QMainWindow):
    instances = []

    def __init__(self, data):
        super().__init__()
        self.data = data
        methods = Methods()
        self.colors = methods.generate_color()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, 440, 380)

        layout = QVBoxLayout()
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(layout)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'frequency ')
        self.plot_widget.setLabel('bottom', 'Thickness [mm]')
        self.plot_widget.setLabel('right', '')
        self.plot_widget.setLabel('top', '')
        self.plot_widget.showGrid(True, True, alpha=0.15)
        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.close)

        layout.addWidget(self.plot_widget)
        layout.addWidget(self.close_button)

        self.center_on_screen()
        self.instances.append(self)

    def plot_histogram(self, _range: tuple):

        hist, bins = np.histogram(self.data.x, bins=25)

        self.plot_widget.clear()

        bin_centers = (bins[:-1] + bins[1:]) / 2
        bars = pg.BarGraphItem(x=bin_centers, height=hist, width=(bins[1] - bins[0]), brush=self.colors + [180])
        self.plot_widget.addItem(bars)

        freqs = []
        for bin_center, freq in zip(bin_centers, hist):
            text_item = pg.TextItem(f'{freq}', anchor=(0.5, 0), color=(252, 255, 252))
            self.plot_widget.addItem(text_item)
            text_item.setPos(bin_center, freq)
            freqs.append(freq)

        self.plot_widget.plotItem.vb.setLimits(xMin=9.0,
                                               xMax=15.0,
                                               yMin=0,
                                               yMax=max(freqs))

        legend = self.plot_widget.addLegend()
        legend.addItem(bars, f'Range {_range}')

        self.show()

    def center_on_screen(self):
        available_geometry = QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.geometry()

        x = (available_geometry.width() - window_geometry.width()) // 2
        y = (available_geometry.height() - window_geometry.height()) // 2

        self.move(x, y)
