import pandas as pd
import sys
import csv
import numpy as np
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QScreen, QColor, QPainter, QBrush, QFont
import pyqtgraph as pg
import math
import chardet


class Methods(object):
    def __init__(self):
        super().__init__()
        self._params = UIParameters()
        self.delimiter: str = ''
        self.XYpos: int = 0
        self.cscan: int = 0
        self.sortie: int = 0

    def set_data_delimiter(self, file_name: str):
        """ get the delimiter in the data, most of the time is either space of comma """

        with open(file_name, 'r', encoding='windows-1252', newline='') as file:

            count: int = 0
            for line in file:
                # Find reference for the titles
                if self._params.XYpo_title in line:
                    self.XYpos = count - 1

                if self._params.cscan_title in line:
                    self.cscan = count

                if self._params.sortie_title in line:
                    self.sortie = count

                # Take a data sample to know understand the delimiter
                if count == self._params.sample_line:
                    line = line.replace('\0', '')  # Remove any null characters

                    if ',' in line:
                        self.delimiter = ','
                    elif ' ' in line:
                        self.delimiter = ' '
                    else:
                        ...

                    break

                count += 1

    def get_data_delimiter(self) -> str:
        return self.delimiter

    def get_XYpos(self) -> int:
        return self.XYpos

    def get_cscan_title(self) -> int:
        return self.cscan

    def get_sortie_title(self) -> int:
        return self.sortie

    @staticmethod
    def handle_encoding(file_name: str):
        """ due to files with different encodings, we open them and re write them in the same encoding: windows-1252"""
        with open(file_name, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']
            # print(f"Detected encoding: {encoding}")

        with open(file_name, 'r', encoding=encoding, newline='') as f:
            data = f.read()

        with open(file_name, 'w', encoding='windows-1252', newline='') as f:
            f.write(data)

    @staticmethod
    def return_dataframe(file_name: str, delimiter: str, skip: int) -> pd:
        """ return pandas dataframe with the data """
        df = pd.read_csv(file_name, sep=delimiter, engine='python', skiprows=skip, encoding='windows-1252')  # sep=r',|;' encoding='latin-1'
        if df.shape[1] > 9:
            n = df.shape[1] - 9
            df.drop(columns=df.columns[-n:], axis=1,  inplace=True)
        df.columns = ['Elevation', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5', 'Sensor6', 'Sensor7', 'Sensor8']

        return df

    @staticmethod
    def read_csv_header(file_name: str, limit_row: int, titles: list) -> list:
        """ read the header of a csv file and extract titles and parameters"""

        with open(file_name, 'r') as file:
            # csv_reader = csv.reader(file)
            file_pre_process = (line.replace('\0', '') for line in file)
            csv_reader = csv.reader(file_pre_process)

            row_count = 0
            csv_header_data = []
            for row in csv_reader:
                if row_count >= limit_row:
                    break

                if row_count in titles:
                    title_label = row[0].replace(";", "").replace("_", "")
                    # print(f'---{title_label}')
                else:
                    if not len(row) < 1:
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
    def average_by_intervals_all_sensors(_data: dict) -> pd:
        """ calculate the averages of all averages from all sensors according the previous intervals"""
        _df = None
        for key, value in _data.items():
            _df = pd.concat([_df, value])

        averaged_df = _df.groupby('elevation_bin')['x'].mean().reset_index()
        averaged_df = averaged_df.reindex(columns=['x', 'elevation_bin'])  # reindex to keep this column order

        return averaged_df

    @staticmethod
    def generate_color():
        return [random.randint(0, 255) for _ in range(3)]

    @staticmethod
    def give_me_a_color(sensor: str):
        colors = {
            'Sensor1': [203, 65, 88],
            'Sensor2': [47, 147, 49],
            'Sensor3': [67, 233, 251],
            'Sensor4': [39, 144, 228],
            'Sensor5': [255, 0, 255],
            'Sensor6': [135, 38, 236],
            'Sensor7': [255, 128, 0],
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

    def absolute_point_distance(self, a: list, b: list) -> bool:
        thresh = self._params.display_thresh
        diff1 = [abs(a[0] - b[0]), abs(a[1] - b[1])]
        return diff1[0] < thresh[0] and diff1[1] < thresh[1]

    def fixer_for_j(self, j) -> int:
        """ fix j to place the histogram always in the available screen space"""
        available_geometry = QGuiApplication.primaryScreen().availableGeometry()
        j_available = available_geometry.height()

        if j + self._params.histo_height > j_available:
            return j-self._params.histo_height_fix
        else:
            return j


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
        self.save_graph_button = QPushButton('Save Graph')

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


class UIParameters:
    # Titles & Widgets
    title_version: str = 'RDEsch v0.3b'     # title and version of the software
    current_labels: int = 22                # current labels, i.e. widgets to start adding sub-plots
    current_widgets: int = 29               # max counter of widgets to add a max of 8 sub-plots

    # Histogram plot
    histo_width: int = 424                  # width of the histogram window
    histo_width_offset: int = 20            # offset from the mouse pointer
    histo_height: int = 263                 # height of the histogram window (keep golden ratio: 1.618)
    histo_height_fix: int = 223             # maximum offset to avoid the histogram window to be outside the screen
    histo_x_min: float = 6.0                # x_min in the histogram plot
    histo_x_max: float = 14.5               # x_max in the histogram plot
    histo_y_min: float = 0                  # y_min in the histogram plot
    histo_y_max: float = 100                # y_max in the histogram plot: unused >> we use dynamically max(freqs)
    rounded_corner: int = 7                 # number in pixels to round the corner of the histogram window

    # Main Plot
    plot_x_min: str = '6'                   # x_min for the main plot
    plot_x_max: str = '16'                  # x_max for the main plot
    plot_y_min: str = '-12500'              # y_min for the main plot
    plot_y_max: str = '0'                   # y_max for the main plot
    display_thresh: tuple = [0.10, 70]      # absolute space between mouse and point of interest to display histogram
    alpha_grid: float = 0.15                # alpha value for the grid in plots (shared between main and histogram plot)
    sample_line: int = 60                   # arbitrary line 60 where I know for sure there is a data line
    XYpo_title: str = 'X/Y'                 # X/Y row in the CSV is used as a reference to know where the data starts
    cscan_title: str = 'Réglages C-Scan'    # C-scan data title, row for reference
    sortie_title: str = 'Réglages des paramètres en sortie'  # Parameters sortie title, row for reference

    # Default filters
    low_filter: str = '80'                  # Low filter in percentage for the input data
    high_filter: str = '99'                 # high filter in percentage for the input data
    mean_interval: str = '500'              # mean interval to calculate the data
    max_elevation: str = '0'                # max elevation in data
    min_elevation: str = '-12500'           # min elevation in data

    # Data filtering
    data_saturation: int = 100              # to filter data consider saturated
    data_max_elevation: int = 0             # max elevation corresponding data (y axis)
    data_min_elevation: int = -13000        # min elevation corresponding data (y axis)
