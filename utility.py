import pandas as pd
import sys
import csv
import numpy as np
import random


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
    def apply_filter(df1: pd, df2: pd, low_filter: float, high_filter: float, saturation: float):

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

        return result

    @staticmethod
    def generate_color():
        return [random.randint(0, 255) for _ in range(3)]