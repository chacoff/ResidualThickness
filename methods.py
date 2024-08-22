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
from parameters import UIParameters


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
