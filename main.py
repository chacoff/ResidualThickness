import sys
import csv
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QMessageBox, QLabel, QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem
from PyQt6.QtCore import Qt, QSize, QFileInfo
from PyQt6.QtGui import QAction, QColor, QIcon, QPixmap, QFont
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
import qdarktheme
import pandas as pd
from utility import Methods


class CSVGraphApp(QMainWindow):
    def __init__(self, _title: str):
        super().__init__()

        self.setWindowTitle(_title)

        # GUI ----------
        main = QHBoxLayout()

        # Left Panel
        self.left_panel = QGridLayout()
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
        self.left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.left_panel.setContentsMargins(8, 30, 8, 8)

        self.left_panel.addWidget(self.csv1_title, 0, 0)
        self.left_panel.addWidget(self.table_csv1, 1, 0)
        self.left_panel.addWidget(self.csv2_title, 2, 0)
        self.left_panel.addWidget(self.table_csv2, 3, 0)

        w_left_panel = QWidget()
        w_left_panel.setLayout(self.left_panel)

        main.addWidget(w_left_panel, 1)

        # Right Panel
        right_panel = QVBoxLayout()
        toolbar = self.addToolBar('menu')
        self.load_csv1 = QAction(QIcon(r'icons/csv-file.png'), 'Load CSV', self)
        self.load_csv1.triggered.connect(self.open_csv1)
        self.load_csv2 = QAction(QIcon(r'icons/csv-file_2.png'), 'Load CSV', self)
        self.load_csv2.triggered.connect(self.open_csv2)
        self.plot_button = QAction(QIcon(r'icons/plot-graph.png'), 'Plot Data', self)
        self.plot_button.triggered.connect(self.plot_data)
        self.plot_clear = QAction(QIcon(r'icons/clear.png'), 'Clear plot and data', self)
        self.plot_clear.triggered.connect(self.clear_plot)

        toolbar.addAction(self.load_csv1)
        toolbar.addAction(self.load_csv2)
        toolbar.addAction(self.plot_button)
        toolbar.addAction(self.plot_clear)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(48, 48))
        toolbar.setStyleSheet(
            "QToolBar { background: transparent; border: none; height: 64px;}"
            "QToolBar QToolButton { background: transparent; border: none; }"
            "QToolBar QToolButton::hover { background: rgba(255, 255, 255, 1); }"
        )

        self.plot_widget = pg.PlotWidget()
        plot_title = '<span style="font-size: 22px; font-weight: bold; color: #FF8040;">Residual Thickness</span>'
        self.plot_widget.setTitle(plot_title)
        self.plot_widget.setLabel('left', 'Y')
        self.plot_widget.setLabel('bottom', 'X')
        self.plot_widget.setLabel('right', '')
        self.plot_widget.setLabel('top', '')
        self.plot_widget.showGrid(True, True)
        right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_panel.setContentsMargins(0, 8, 36, 8)

        right_panel.addWidget(self.plot_widget)
        right_panel.addWidget(toolbar)

        w_right_panel = QWidget()
        w_right_panel.setLayout(right_panel)

        main.addWidget(w_right_panel, 5)

        self.main_widget = QWidget()
        self.main_widget.setLayout(main)
        self.setCentralWidget(self.main_widget)
        self.statusBar().showMessage(f"Ready.")
        # GUI ----------

        self.methods = Methods()
        self.df_csv1: pd = None
        self.df_csv2: pd = None

    def open_csv1(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")

        if not file_name:
            return

        self.csv1_title.setText(QFileInfo(file_name).fileName())
        csv1_header = self.methods.read_csv_header(file_name, limit_row=46, titles=[0, 34, 42])
        self.populate_table(self.table_csv1, csv1_header, file_name)
        self.df_csv1 = self.methods.return_dataframe(file_name, skip=47)

    def open_csv2(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")

        if not file_name:
            return

        self.csv2_title.setText(QFileInfo(file_name).fileName())
        csv2_header = self.methods.read_csv_header(file_name, limit_row=46, titles=[0, 34, 42])
        self.populate_table(self.table_csv2, csv2_header, file_name)
        self.df_csv2 = self.methods.return_dataframe(file_name, skip=47)

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

    def plot_data(self) -> None:

        if self.df_csv1 is None or self.df_csv2 is None:
            self.error_box('No data.\n\n'
                           'Please, first load data to process before trying to plot.\n\n'
                           'Pay attention you might need to load 2 csv before attempting to plot.')
            return

        print(self.df_csv1.shape)
        print(self.df_csv2.shape)

        x_1 = self.df_csv1.s3
        y_1 = self.df_csv2.s3

        x_2 = self.df_csv1.s4
        y_2 = self.df_csv2.s4

        self.plot_widget.clear()
        self.plot_widget.plot(x_1, y_1, pen=pg.mkPen(QColor(249, 127, 63), width=2))
        self.plot_widget.plot(x_2, y_2, pen=pg.mkPen(QColor(49, 127, 243), width=2))

    def clear_plot(self) -> None:
        self.df_csv1 = None
        self.df_csv2 = None
        self.csv1_title.setText(' ')
        self.csv2_title.setText(' ')
        while self.table_csv1.rowCount() > 0:
            self.table_csv1.removeRow(0)
        while self.table_csv2.rowCount() > 0:
            self.table_csv2.removeRow(0)
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
