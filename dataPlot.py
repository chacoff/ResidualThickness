from dataclasses import dataclass
import pandas as pd


@dataclass
class SensorData:
    sensor_name: str
    x_data: pd.Series
    y_data: pd.Series


@dataclass
class AverageData:
    sensor_name: str
    x_data: pd.Series
    y_data: pd.Series
