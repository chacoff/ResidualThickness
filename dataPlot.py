from dataclasses import dataclass
import pandas as pd
from scipy import stats


@dataclass
class DataIntervals:
    filename: str
    gate: str
    year: str
    pile: str
    pos: str
    trial: str
    sensors: list
    low_filter: int
    high_filter: int
    step: int
    interval: str
    mean: float
    trim20: float
    std: float
    mode: float
    median: float
    min: float
    max: float
    points: int

    def __init__(self, interval: str, _df: pd.DataFrame):
        self.interval = f'Interval Results: {interval}'
        self.mean = round(_df.loc[:, 'x'].mean(), 8)
        self.trim20 = round(float(stats.trim_mean(_df.x, 0.2)), 8)
        self.std = round(_df.loc[:, 'x'].std(), 8)
        self.mode = round(_df.loc[:, 'x'].mode()[0], 8)
        self.median = round(_df.loc[:, 'x'].median(), 8)
        self.min = round(_df.loc[:, 'x'].min(), 8)
        self.max = round(_df.loc[:, 'x'].max(), 8)
        self.points = _df.loc[:, 'x'].count()

    def __str__(self) -> str:
        return (
            f'Interval: {self.interval}\n'
            f'Mean: {self.mean}\n'
            f'Trimmed Mean 20%: {self.trim20}\n'
            f'Standard Deviation: {self.std}\n'
            f'Mode: {self.mode}\n'
            f'Median: {self.median}\n'
            f'Min: {self.min}\n'
            f'Max: {self.max}\n'
            f'Points: {self.points}'
        )

    def to_dict(self, dc: dict):  # data complement
        return {
            'FileName': dc['filename'],
            'Gate': dc['gate'],
            'Year': dc['year'],
            'Pile': dc['pile'],
            'Position': dc['pos'],
            'Trial': dc['trial'],
            'Sensors': dc['sensors'],
            'LowFilter': dc['low_filter'],
            'HighFilter': dc['high_filter'],
            'Step': dc['step'],
            'Interval': self.interval,
            'Mean': self.mean,
            'Trimmed Mean 20%': self.trim20,
            'Standard Deviation': self.std,
            'Mode': self.mode,
            'Median': self.median,
            'Min': self.min,
            'Max': self.max,
            'Points': self.points
        }
