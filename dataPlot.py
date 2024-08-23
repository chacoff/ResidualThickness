from dataclasses import dataclass
import pandas as pd


@dataclass
class SensorData:
    sensor_name: str
    x_data: pd.Series
    y_data: pd.Series
