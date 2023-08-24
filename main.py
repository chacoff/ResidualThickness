import sys
import csv
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QMessageBox, QLabel, QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem, QLineEdit
from PyQt6.QtCore import Qt, QSize, QFileInfo
from PyQt6.QtGui import QAction, QColor, QIcon, QPixmap, QFont, QIntValidator
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
import qdarktheme
import pandas as pd
from scipy import stats
import numpy as np
from utility import Methods
from scipy import stats


class CSVGraphApp(QMainWindow):
    def __init__(self, _title: str):
        super().__init__()

        self.setWindowTitle(_title)

        # GUI ----------
        main = QVBoxLayout()

        # Header
        header = QGridLayout()
        self.header_title = QLabel('Residual Thickness:')
        self.header_title.setStyleSheet('''QLabel {font-size: 22px; font-weight: bold; color: #FF8040;}''')

        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self.header_title, 0, 0)

        w_header_panel = QWidget()
        w_header_panel.setLayout(header)

        body = QHBoxLayout()

        # Right Panel
        self.right_panel = QGridLayout()
        self.csv1_title = QLabel(' ')
        self.csv1_title.setStyleSheet('''QLabel {font-size: 16px; font-weight: bold; color: #606060;}''')
        self.table_csv1 = QTableWidget()
        self.table_csv1.setColumnCount(2)
        self.table_csv1.setHorizontalHeaderLabels(['Type', 'Value'])
        self.table_csv1.verticalHeader().setVisible(False)
        self.table_csv1.resizeColumnsToContents()
        self.table_csv1.resizeRowsToContents()
        self.table_csv1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.csv2_title = QLabel(' ')
        self.csv2_title.setStyleSheet('''QLabel {font-size: 16px; font-weight: bold; color: #606060;}''')
        self.table_csv2 = QTableWidget()
        self.table_csv2.setColumnCount(2)
        self.table_csv2.setHorizontalHeaderLabels(['Type', 'Value'])
        self.table_csv2.verticalHeader().setVisible(False)
        self.table_csv2.resizeColumnsToContents()
        self.table_csv2.resizeRowsToContents()
        self.table_csv2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_panel.setContentsMargins(0, 8, 0, 0)

        self.right_panel.addWidget(self.csv1_title, 0, 0)
        self.right_panel.addWidget(self.table_csv1, 1, 0)
        self.right_panel.addWidget(self.csv2_title, 2, 0)
        self.right_panel.addWidget(self.table_csv2, 3, 0)

        w_right_panel = QWidget()
        w_right_panel.setLayout(self.right_panel)

        # Left Panel
        self.left_panel = QGridLayout()
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['Thickness', 'Amplitude'])
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        plot_configs = QLabel('Plot settings:')
        plot_configs.setStyleSheet('''QLabel {font-size: 16px; font-weight: bold; color: #606060;}''')
        label_low = QLabel('Low Filter:')
        self.low_filter = QLineEdit()
        self.low_filter.setMaxLength(2)  # Set maximum length to 4 characters
        self.low_filter.setValidator(QIntValidator())  # Allow only integer input
        self.low_filter.setText('50')
        label_high = QLabel('High Filter:')
        self.high_filter = QLineEdit()
        self.high_filter.setMaxLength(2)
        self.high_filter.setValidator(QIntValidator())
        self.high_filter.setText('99')
        label_bin = QLabel('Mean Interval:')
        self.bin_filter = QLineEdit()
        self.bin_filter.setMaxLength(4)
        self.bin_filter.setValidator(QIntValidator())
        self.bin_filter.setText('500')
        label_x_min = QLabel('X min:')
        self.x_min = QLineEdit()
        self.x_min.setMaxLength(4)
        self.x_min.setValidator(QIntValidator())
        self.x_min.setText('8')
        label_x_max = QLabel('X max:')
        self.x_max = QLineEdit()
        self.x_max.setMaxLength(4)
        self.x_max.setValidator(QIntValidator())
        self.x_max.setText('16')
        label_y_min = QLabel('Y min:')
        self.y_min = QLineEdit()
        self.y_min.setMaxLength(8)
        self.y_min.setValidator(QIntValidator())
        self.y_min.setText('-11000')
        label_y_max = QLabel('Y max:')
        self.y_max = QLineEdit()
        self.y_max.setMaxLength(8)
        self.y_max.setValidator(QIntValidator())
        self.y_max.setText('1000')

        self.left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.left_panel.setContentsMargins(0, 8, 0, 0)

        self.left_panel.addWidget(plot_configs, 0, 0, 1, 3)
        self.left_panel.addWidget(label_low, 1, 0)
        self.left_panel.addWidget(self.low_filter, 1, 1)
        self.left_panel.addWidget(QLabel('%'), 1, 2)
        self.left_panel.addWidget(label_high, 2, 0)
        self.left_panel.addWidget(self.high_filter, 2, 1)
        self.left_panel.addWidget(QLabel('%'), 2, 2)
        self.left_panel.addWidget(label_bin, 3, 0)
        self.left_panel.addWidget(self.bin_filter, 3, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 3, 2)
        self.left_panel.addWidget(label_x_min, 4, 0)
        self.left_panel.addWidget(self.x_min, 4, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 4, 2)
        self.left_panel.addWidget(label_x_max, 5, 0)
        self.left_panel.addWidget(self.x_max, 5, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 5, 2)
        self.left_panel.addWidget(label_y_min, 6, 0)
        self.left_panel.addWidget(self.y_min, 6, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 6, 2)
        self.left_panel.addWidget(label_y_max, 7, 0)
        self.left_panel.addWidget(self.y_max, 7, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 7, 2)
        self.left_panel.addWidget(self.table_widget, 8, 0, 1, 3)
        # self.left_panel.setRowStretch(5, 1)

        w_left_panel = QWidget()
        w_left_panel.setLayout(self.left_panel)

        # Central Panel
        central_panel = QVBoxLayout()
        toolbar = self.addToolBar('menu')
        self.load_csv1 = QAction(QIcon(r'icons/csv-file.png'), 'Load CSV with Thickness data', self)
        self.load_csv1.triggered.connect(lambda: self.open_csv(action=1))
        self.load_csv2 = QAction(QIcon(r'icons/csv-file_2.png'), 'Load CSV with Amplitud data', self)
        self.load_csv2.triggered.connect(lambda: self.open_csv(action=2))
        self.plot_button = QAction(QIcon(r'icons/plot-graph.png'), 'Plot Data', self)
        self.plot_button.triggered.connect(self.plot_data)
        self.plot_clear = QAction(QIcon(r'icons/clear.png'), 'Clear plot and data', self)
        self.plot_clear.triggered.connect(self.clear_plot)

        toolbar.addAction(self.load_csv1)
        toolbar.addAction(self.load_csv2)
        toolbar.addAction(self.plot_button)
        toolbar.addAction(self.plot_clear)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setStyleSheet(
            "QToolBar { background: transparent; border: none; height: 64px;}"
            "QToolBar QToolButton { background: transparent; border: none; }"
            "QToolBar QToolButton::hover { background: rgba(255, 255, 255, 1); }"
        )

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Elevation [mm]')
        self.plot_widget.setLabel('bottom', 'Thickness [mm]')
        self.plot_widget.setLabel('right', '')
        self.plot_widget.setLabel('top', '')
        self.plot_widget.showGrid(True, True)
        central_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        central_panel.setContentsMargins(0, 0, 0, 0)

        central_panel.addWidget(self.plot_widget)
        central_panel.addWidget(toolbar)

        w_central_panel = QWidget()
        w_central_panel.setLayout(central_panel)

        # Body
        body.addWidget(w_left_panel, 1)
        body.addWidget(w_central_panel, 5)
        body.addWidget(w_right_panel, 1)

        w_body_panel = QWidget()
        w_body_panel.setLayout(body)

        # Main
        main.addWidget(w_header_panel, 0)
        main.addWidget(w_body_panel, 1)

        self.main_widget = QWidget()
        self.main_widget.setLayout(main)
        self.setCentralWidget(self.main_widget)
        self.statusBar().showMessage(f"Ready.")
        # GUI ----------

        self.methods = Methods()
        self.df_csv1: pd = None  # csv to plot
        self.df_csv1_name: str = 'Thickness'
        self.df_csv2: pd = None  # csv AMP for filtering
        self.df_csv2_name: str = 'Amplitude'

    def open_csv(self, action) -> None:

        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")

        if not file_name:
            return

        if action == 1:
            self.df_csv1_name = QFileInfo(file_name).baseName()  # fileName() to have it with the extension
            self.read_csv_header(file_name, self.table_csv1, self.df_csv1_name, self.csv1_title)
            self.df_csv1 = self.methods.return_dataframe(file_name, skip=47)
        elif action == 2:
            self.df_csv2_name = QFileInfo(file_name).baseName()  # fileName() to have it with the extension
            self.read_csv_header(file_name, self.table_csv2, self.df_csv2_name, self.csv2_title)
            self.df_csv2 = self.methods.return_dataframe(file_name, skip=47)
        else:
            self.error_box('No implementation')

        self.populate_dropping_buttons()

    def read_csv_header(self, _file: str, _table: QTableWidget, _name: str, _qtitle: QLabel) -> None:
        """ populates tables with the header parameters from each CSV file and populate the table
         with buttons to drop columns of every csv """

        _qtitle.setText(_name)
        _header = self.methods.read_csv_header(_file, limit_row=46, titles=[0, 34, 42])
        self.populate_table(_table, _header, _file)

    def populate_table(self, _table_widget: QTableWidget, _data: pd, _csv: str):
        """" populate table_csv1 and table_csv2 """

        _table_widget.setRowCount(len(_data))

        for row, (param, value) in enumerate(_data):
            param_item = QTableWidgetItem(param)
            param_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            _table_widget.setItem(row, 0, param_item)

            value_item = QTableWidgetItem(value)
            value_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            _table_widget.setItem(row, 1, value_item)

        self.statusBar().showMessage(f"Loaded rows from {_csv}")

    def populate_dropping_buttons(self) -> None:
        """" populate the table with the buttons to drop tables """
        if self.df_csv1 is not None and self.df_csv2 is not None:
            # self.table_widget.setHorizontalHeaderLabels([self.df_csv1_name, self.df_csv2_name])
            self.table_widget.setRowCount(self.max_rows_to_drop())
            self.buttons_fillers(self.df_csv1, 0)
            self.buttons_fillers(self.df_csv2, 1)

    def buttons_fillers(self, _dataframe: pd, _col: int):
        """ generate the buttons to drop tables """
        for row_idx, column in enumerate(_dataframe.columns):
            if column == 'Elevation':
                drop_button = QPushButton(f'{column}', self)
            else:
                drop_button = QPushButton(f'drop {column}', self)
                drop_button.clicked.connect(lambda checked, col=column: self.drop_column(col, _dataframe))
            self.table_widget.setCellWidget(row_idx, _col, drop_button)

    def max_rows_to_drop(self) -> int:
        return max(self.df_csv1.shape[1], self.df_csv2.shape[1])

    def drop_column(self, column, _dataframe):
        if column in _dataframe.columns:
            if column != 'Elevation':
                _dataframe.drop(columns=column, inplace=True, axis=1)
                self.update_dropping_buttons(self.df_csv1, self.df_csv2)
                # print(_dataframe)

    def update_dropping_buttons(self, _csv1: pd, _csv2: pd):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(self.max_rows_to_drop())
        self.buttons_fillers(_csv1, 0)
        self.buttons_fillers(_csv2, 1)

    def plot_data(self) -> None:

        if self.df_csv1 is None or self.df_csv2 is None:
            self.error_box('No data.\n\n'
                           'Please, first load data to process before trying to plot.\n\n'
                           'Pay attention you might need to load 2 csv before attempting to plot.')
            return

        self.plot_widget.clear()
        self.header_title.setText(f'Residual Thickness: {self.df_csv1_name}')
        y = self.df_csv1.Elevation

        filtered_thickness = self.methods.apply_filter(self.df_csv1.copy(),
                                                       self.df_csv2.copy(),
                                                       low_filter=float(self.low_filter.text()),
                                                       high_filter=float(self.high_filter.text()),
                                                       saturation=100)

        # self.plot_widget.plot(x_1, y, pen=pg.mkPen(QColor(249, 127, 63), width=2))

        try:
            for name, series in filtered_thickness.items():
                color = self.methods.generate_color()
                if name != 'Elevation':
                    x_1 = filtered_thickness[name]

                    average_by_interval = self.methods.average_by_intervals(_x=x_1,
                                                                            _y=y,
                                                                            interval=int(self.bin_filter.text()),
                                                                            min_elevation=-10000)

                    scatter_plot = pg.ScatterPlotItem(size=2, pen=pg.mkPen(None), brush=pg.mkBrush(color+[65]))
                    scatter_plot.setData(x=x_1, y=y)

                    self.plot_widget.addItem(scatter_plot)

                    scatter_average = pg.ScatterPlotItem(size=12, pen=pg.mkPen(None), brush=pg.mkBrush(color+[220]))
                    scatter_average.setData(x=average_by_interval.x, y=average_by_interval.elevation_bin)

                    self.plot_widget.addItem(scatter_average)

                    self.plot_widget.plotItem.vb.setLimits(xMin=int(self.x_min.text()),
                                                           xMax=int(self.x_max.text()),
                                                           yMin=int(self.y_min.text()),
                                                           yMax=int(self.y_max.text()))

        except AttributeError as e:
            print(e)

        except ValueError as e:
            print(e)

    def clear_plot(self) -> None:
        self.df_csv1 = None
        self.df_csv2 = None
        self.csv1_title.setText(' ')
        self.csv2_title.setText(' ')
        while self.table_csv1.rowCount() > 0:
            self.table_csv1.removeRow(0)
        while self.table_csv2.rowCount() > 0:
            self.table_csv2.removeRow(0)
        while self.table_widget.rowCount() > 0:
            self.table_widget.removeRow(0)
        self.plot_widget.clear()

    def error_box(self, message) -> None:
        dlg = QMessageBox(self)
        icon = QIcon('icons/cat.png')
        dlg.setIconPixmap(icon.pixmap(64, 64))
        dlg.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        dlg.setText(message)
        dlg.exec()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    qdarktheme.setup_theme('light')  # 'light' option
    pg.setConfigOption('background', QColor(248, 249, 250))
    pg.setConfigOption('foreground', 'k')
    image_window = CSVGraphApp(' T_Logiciel - RD-Esch v0.0.1')
    image_window.setWindowIcon(QIcon(r'icons/bar-graph.png'))
    image_window.show()
    image_window.showMaximized()
    sys.exit(app.exec())
