import pandas as pd
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QMessageBox, QLabel, QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem, QLineEdit, QComboBox, QMdiSubWindow
from PyQt6.QtCore import Qt, QSize, QFileInfo, QPointF
from PyQt6.QtGui import QAction, QColor, QIcon, QPixmap, QFont, QIntValidator


class ColumnsMethod:
    def __init__(self):
        super().__init__()
        self.table_widget = QTableWidget()
        self.df_csv1: pd = None
        self.df_csv2: pd = None

    # ---- methods not used since we no longer drop columns >> kept for a while
    def populate_dropping_buttons(self) -> None:
        """" populate the table with the buttons to drop tables """
        if self.df_csv1 is not None and self.df_csv2 is not None:
            # self.table_widget.setHorizontalHeaderLabels([self.df_csv1_name, self.df_csv2_name])
            self.table_widget.setRowCount(self.max_rows_to_drop())
            self.buttons_fillers(self.df_csv1, 0)
            self.buttons_fillers(self.df_csv2, 1)

    def update_dropping_buttons(self, _csv1: pd, _csv2: pd):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(self.max_rows_to_drop())
        self.buttons_fillers(_csv1, 0)
        self.buttons_fillers(_csv2, 1)

    def max_rows_to_drop(self) -> int:
        return max(self.df_csv1.shape[1], self.df_csv2.shape[1])

    def drop_column(self, column, _dataframe):
        if column in _dataframe.columns:
            if column != 'Elevation':
                _dataframe.drop(columns=column, inplace=True, axis=1)
                self.update_dropping_buttons(self.df_csv1, self.df_csv2)
                # print(_dataframe)

    def buttons_fillers(self, _dataframe: pd, _col: int):
        """ generate the buttons to drop tables """
        for row_idx, column in enumerate(_dataframe.columns):
            if column == 'Elevation':
                drop_button = QPushButton(f'{column}', self)
            else:
                drop_button = QPushButton(f'drop {column}', self)
                drop_button.clicked.connect(lambda checked, col=column: self.drop_column(col, _dataframe))
            self.table_widget.setCellWidget(row_idx, _col, drop_button)


