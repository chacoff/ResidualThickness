import sys
import csv
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QMessageBox, QLabel, QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem, QLineEdit, QComboBox, QSizePolicy
from PyQt6.QtCore import Qt, QSize, QFileInfo, QPointF, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QColor, QIcon, QPixmap, QFont, QIntValidator, QCursor
import pyqtgraph as pg
import qdarktheme
import pandas as pd
import numpy as np
import os
from scipy import stats
from utility import Methods, HistogramApp, UIParameters
from spinner import Overlay, EmitSignal
import time


class CSVGraphApp(QMainWindow):
    def __init__(self, ):
        super().__init__()

        font = QFont()
        font.setPixelSize(16)
        self._params = UIParameters()
        self.setWindowTitle(f' ResidualThickness - {self._params.title_version}')

        # GUI ----------
        main = QVBoxLayout()

        # Header
        header = QGridLayout()
        self.header_title = QLabel('Residual Thickness:')
        self.header_title.setStyleSheet('''QLabel {font-size: 22px; font-weight: bold; color: #FF8040;}''')

        am_label = QLabel()
        am_logo = QPixmap('icons/logoAM.png')
        label_size = self.header_title.sizeHint()
        scaled_pixmap = am_logo.scaled(label_size,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       transformMode=Qt.TransformationMode.SmoothTransformation)

        am_label.setPixmap(scaled_pixmap)
        am_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        header.setContentsMargins(8, 12, 12, 0)
        header.addWidget(QLabel('  '), 0, 0)
        header.addWidget(self.header_title, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        header.addWidget(am_label, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)

        w_header_panel = QWidget()
        w_header_panel.setLayout(header)

        body = QHBoxLayout()

        # Right Panel
        self.right_panel = QGridLayout()
        self.csv1_title = QLabel(' ')
        self.csv1_title.setStyleSheet('''QLabel {font-size: 14px; font-weight: bold; color: #606060;}''')
        self.table_csv1 = QTableWidget()
        self.table_csv1.setColumnCount(2)
        self.table_csv1.setHorizontalHeaderLabels(['Type', 'Value'])
        self.table_csv1.verticalHeader().setVisible(False)
        self.table_csv1.resizeColumnsToContents()
        self.table_csv1.resizeRowsToContents()
        self.table_csv1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.csv2_title = QLabel(' ')
        self.csv2_title.setStyleSheet('''QLabel {font-size: 14px; font-weight: bold; color: #606060;}''')
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

        # Left panel data filters
        data_configs = QLabel('Data filters:')
        data_configs.setStyleSheet('''QLabel {font-size: 14px; font-weight: bold; color: #606060;}''')
        label_low = QLabel('Low Filter:')
        self.low_filter = QLineEdit()
        self.low_filter.setMaxLength(2)  # Set maximum length to 4 characters
        self.low_filter.setValidator(QIntValidator())  # Allow only integer input
        self.low_filter.setText(self._params.low_filter)
        self.low_filter.setToolTip('minimum is 0%')
        label_high = QLabel('High Filter:')
        self.high_filter = QLineEdit()
        self.high_filter.setMaxLength(3)
        self.high_filter.setValidator(QIntValidator())
        self.high_filter.setText(self._params.high_filter)
        self.high_filter.setToolTip('maximum is 100%')
        label_bin = QLabel('Mean Interval:')
        self.bin_filter = QLineEdit()
        self.bin_filter.setMaxLength(4)
        self.bin_filter.setValidator(QIntValidator())
        self.bin_filter.setText(self._params.mean_interval)
        self.bin_filter.setToolTip('Recommended value is 1000mm. Maximum is 9999mm')
        label_max_elev = QLabel('Max. elevation:')
        self.max_elev_filter = QLineEdit()
        self.max_elev_filter.setMaxLength(6)
        self.max_elev_filter.setValidator(QIntValidator())
        self.max_elev_filter.setText(self._params.max_elevation)
        self.max_elev_filter.setToolTip('Recommended value is 0mm')
        label_min_elev = QLabel('Min. elevation:')
        self.min_elev_filter = QLineEdit()
        self.min_elev_filter.setMaxLength(6)
        self.min_elev_filter.setValidator(QIntValidator())
        self.min_elev_filter.setText(self._params.min_elevation)
        self.min_elev_filter.setToolTip('Recommended value is -10000mm')

        # Left panel plot settings
        plot_configs = QLabel('Plot settings:')
        plot_configs.setStyleSheet('''QLabel {font-size: 14px; font-weight: bold; color: #606060;}''')
        label_x_min = QLabel('X min:')
        self.x_min = QLineEdit()
        self.x_min.setMaxLength(4)
        self.x_min.setValidator(QIntValidator())
        self.x_min.setText(self._params.plot_x_min)
        label_x_max = QLabel('X max:')
        self.x_max = QLineEdit()
        self.x_max.setMaxLength(4)
        self.x_max.setValidator(QIntValidator())
        self.x_max.setText(self._params.plot_x_max)
        label_y_min = QLabel('Y min:')
        self.y_min = QLineEdit()
        self.y_min.setMaxLength(6)
        self.y_min.setValidator(QIntValidator())
        self.y_min.setText(self._params.plot_y_min)
        label_y_max = QLabel('Y max:')
        self.y_max = QLineEdit()
        self.y_max.setMaxLength(8)
        self.y_max.setValidator(QIntValidator())
        self.y_max.setText(self._params.plot_y_max)
        self.label_results = QLabel('Interval Results:')
        self.label_results.setStyleSheet('''QLabel {font-size: 14px; font-weight: bold; color: #606060;}''')
        label_result_average = QLabel('Mean:')
        self.result_average = QLabel('0.000000')
        label_result_trim_20 = QLabel('Trimmed mean 20%: ')
        self.result_trim_20 = QLabel('0.000000')
        label_result_std = QLabel('Standard Deviation:')
        self.result_std = QLabel('0.000000')
        label_result_mode = QLabel('Mode:')
        self.result_mode = QLabel('0.000000')
        label_result_median = QLabel('Median:')
        self.result_median = QLabel('0.000000')
        label_result_min = QLabel('Min. value:')
        self.result_min = QLabel('0.000000')
        label_result_max = QLabel('Max. value:')
        self.result_max = QLabel('0.000000')
        label_result_points = QLabel('Number of Points')
        self.result_points = QLabel('0.000000')

        label_checkbox = QLabel('Sensor to plot:')
        label_checkbox.setStyleSheet('''QLabel {font-size: 14px; font-weight: bold; color: #606060;}''')
        self.column_checkbox = QComboBox()
        self.column_checkbox.currentIndexChanged.connect(self.selection_master_combobox)
        self.action_add_box = QPushButton('add sensor')
        self.action_add_box.clicked.connect(self.add_qcombobox)
        self.action_add_box.setDisabled(True)
        self.action_del_box = QPushButton('remove sensor')
        self.action_del_box.clicked.connect(self.remove_qcombobox)
        self.action_del_box.setDisabled(True)

        self.left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.left_panel.setContentsMargins(0, 8, 0, 0)

        self.left_panel.addWidget(data_configs, 0, 0, 1, 3)
        self.left_panel.addWidget(label_low, 1, 0)
        self.left_panel.addWidget(self.low_filter, 1, 1)
        self.left_panel.addWidget(QLabel('%'), 1, 2)
        self.left_panel.addWidget(label_high, 2, 0)
        self.left_panel.addWidget(self.high_filter, 2, 1)
        self.left_panel.addWidget(QLabel('%'), 2, 2)
        self.left_panel.addWidget(label_bin, 3, 0)
        self.left_panel.addWidget(self.bin_filter, 3, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 3, 2)
        self.left_panel.addWidget(label_max_elev, 4, 0)
        self.left_panel.addWidget(self.max_elev_filter, 4, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 4, 2)
        self.left_panel.addWidget(label_min_elev, 5, 0)
        self.left_panel.addWidget(self.min_elev_filter, 5, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 5, 2)
        self.left_panel.addWidget(plot_configs, 6, 0, 1, 3)
        self.left_panel.addWidget(label_x_min, 7, 0)
        self.left_panel.addWidget(self.x_min, 7, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 7, 2)
        self.left_panel.addWidget(label_x_max, 8, 0)
        self.left_panel.addWidget(self.x_max, 8, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 8, 2)
        self.left_panel.addWidget(label_y_min, 9, 0)
        self.left_panel.addWidget(self.y_min, 9, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 9, 2)
        self.left_panel.addWidget(label_y_max, 10, 0)
        self.left_panel.addWidget(self.y_max, 10, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 10, 2)
        # self.left_panel.addWidget(self.table_widget, 8, 0, 1, 3)

        # left panel: plot result
        self.left_panel.addWidget(self.label_results, 11, 0, 1, 3)
        self.left_panel.addWidget(label_result_average, 12, 0)
        self.left_panel.addWidget(self.result_average, 12, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 12, 2)

        self.left_panel.addWidget(label_result_trim_20, 13, 0)
        self.left_panel.addWidget(self.result_trim_20, 13, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 13, 2)

        self.left_panel.addWidget(label_result_std, 14, 0)
        self.left_panel.addWidget(self.result_std, 14, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 14, 2)
        self.left_panel.addWidget(label_result_mode, 15, 0)
        self.left_panel.addWidget(self.result_mode, 15, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 15, 2)
        self.left_panel.addWidget(label_result_median, 16, 0)
        self.left_panel.addWidget(self.result_median, 16, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 16, 2)
        self.left_panel.addWidget(label_result_min, 17, 0)
        self.left_panel.addWidget(self.result_min, 17, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 17, 2)
        self.left_panel.addWidget(label_result_max, 18, 0)
        self.left_panel.addWidget(self.result_max, 18, 1)
        self.left_panel.addWidget(QLabel('[mm]'), 18, 2)
        self.left_panel.addWidget(label_result_points, 19, 0)
        self.left_panel.addWidget(self.result_points, 19, 1)
        self.left_panel.addWidget(QLabel('[pt]'), 19, 2)

        # left panel: adding sensors
        self.left_panel.addWidget(label_checkbox, 20, 0, 1, 3)
        ad = QHBoxLayout()
        ad.addWidget(self.action_add_box)
        ad.addWidget(self.action_del_box)
        ad.setContentsMargins(0, 0, 0, 0)
        ad_ = QWidget()
        ad_.setLayout(ad)
        self.left_panel.addWidget(ad_, 21, 0, 1, 3)
        self.left_panel.addWidget(self.column_checkbox, 22, 0, 1, 3)
        # self.left_panel.setRowStretch(5, 1)

        w_left_panel = QWidget()
        w_left_panel.setLayout(self.left_panel)

        # Central Panel
        central_panel = QVBoxLayout()
        toolbar = self.addToolBar('menu')
        self.load_csv1 = QAction(QIcon(r'icons/csv-file.png'), 'Load CSV with Thickness or Amplitude data', self)
        self.load_csv1.triggered.connect(self.open_csv)
        self.plot_button = QAction(QIcon(r'icons/plot-graph.png'), 'Plot Data', self)
        self.plot_button.triggered.connect(self.plot_data)
        self.plot_button.setShortcuts(['Return', 'Enter'])
        self.plot_clear = QAction(QIcon(r'icons/clear.png'), 'Clear plot and data', self)
        self.plot_clear.triggered.connect(self.clear_plot)

        toolbar.addAction(self.load_csv1)
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
        self.hover_label = pg.TextItem(anchor=(1, 0),
                                       color=(251, 253, 255, 250),
                                       fill=(49, 51, 53, 190)
                                       )
        self.hover_label.setFont(font)
        self.plot_widget.setLabel('left', 'Elevation [mm]')
        self.plot_widget.setLabel('bottom', 'Thickness [mm]')
        self.plot_widget.setLabel('right', '')
        self.plot_widget.setLabel('top', '')
        self.plot_widget.showGrid(True, True, alpha=self._params.alpha_grid)
        # self.plot_widget.getPlotItem().showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.scene().sigMouseMoved.connect(self.plot_mouse_hover)
        self.plot_widget.scene().sigMouseClicked.connect(self.plot_clicked)
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

        self.overlay = Overlay(self.centralWidget())
        self.overlay.hide()

        self.statusBar().showMessage(f"Ready.")
        # GUI ----------

        # Variables ----------
        self.methods = Methods()
        self.histo = HistogramApp()
        self.df_csv1: pd = None  # csv thickness to plot
        self.df_csv1_name: str = 'Thickness'
        self.df_csv2: pd = None  # csv AMP (amplitude) for filtering
        self.df_csv2_name: str = 'Amplitude'
        self.selected_sensor: str = 'Sensor3'
        self.selected_sensor_list: list = []
        self.selected_sensor_dict: dict = {
            'master': None,
            'slave0': None,
            'slave1': None,
            'slave2': None,
            'slave3': None,
            'slave4': None,
            'slave5': None,
            'slave6': None
        }
        self.average_sensor_data: dict = dict()  # empty!
        self.average_data: list = []
        self.for_histo: list = []
        self.widget_counter: int = 23
        self._chk_slave_list: list = []

    def open_csv(self) -> None:

        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Open CSV File", "./sample_data",
                                                   "CSV Files (*.csv);;All Files (*)")

        if not file_name:
            return

        self.methods.set_data_delimiter(file_name)
        _delimiter: str = self.methods.get_data_delimiter()
        # print(f'delimiter is: {_delimiter}')

        data_path = QFileInfo(file_name).absolutePath()
        is_amplitude = 'AMP' in QFileInfo(file_name).baseName()

        if is_amplitude:
            name = QFileInfo(file_name).baseName()  # .fileName()
            name_csv_amplitude = os.path.join(data_path, name)
            size = len(name_csv_amplitude)
            name_csv_thickness = name_csv_amplitude[:size - 6]
        else:  # it is a thickness file
            name = QFileInfo(file_name).baseName()  # .fileName()
            name_csv_thickness = os.path.join(data_path, name)
            name_csv_amplitude = name_csv_thickness + ' - AMP'

        self.df_csv1_name = QFileInfo(name_csv_thickness+'.csv').baseName()  # fileName() to have it with the extension
        self.read_csv_header(name_csv_thickness+'.csv', self.table_csv1, self.df_csv1_name, self.csv1_title)
        self.df_csv1 = self.methods.return_dataframe(name_csv_thickness+'.csv', delimiter=_delimiter, skip=47)

        self.df_csv2_name = QFileInfo(name_csv_amplitude+'.csv').baseName()  # fileName() to have it with the extension
        self.read_csv_header(name_csv_amplitude+'.csv', self.table_csv2, self.df_csv2_name, self.csv2_title)
        self.df_csv2 = self.methods.return_dataframe(name_csv_amplitude+'.csv', delimiter=_delimiter, skip=47)

        self.populate_checkbox(self.column_checkbox)
        self.action_add_box.setDisabled(False)
        self.action_del_box.setDisabled(False)

    def read_csv_header(self, _file: str, _table: QTableWidget, _name: str, _qtitle: QLabel) -> None:
        """ populates tables with the header parameters from each CSV file and populate the table
         with buttons to drop columns of every csv """

        _qtitle.setText(_name)
        _header = self.methods.read_csv_header(_file,
                                               limit_row=self.methods.get_XYpos(),
                                               titles=[0,
                                                       self.methods.get_cscan_title(),
                                                       self.methods.get_sortie_title()])  # 46, [0, 34, 42]
        self.populate_table(_table, _header, _file)

    def populate_table(self, _table_widget: QTableWidget, _data: pd, _csv: str) -> None:
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

    def populate_checkbox(self, box) -> None:
        """ function to populate the combo boxes with the available sensors to plot """
        if self.df_csv1 is not None and self.df_csv2 is not None:
            checkbox_items = []
            for row_idx, column in enumerate(self.df_csv1.columns):
                if column != 'Elevation':
                    checkbox_items.append(column)
            box.addItems(checkbox_items)

    def selection_master_combobox(self) -> None:
        """ handles the selection in the master combo box """

        if len(self.selected_sensor_list) == 1:  # it means only the master combo box is available
            self.selected_sensor_dict: dict = {  # we reset the dictionary of selected sensors
                'master': None,
                'slave0': None,
                'slave1': None,
                'slave2': None,
                'slave3': None,
                'slave4': None,
                'slave5': None,
                'slave6': None
            }

        self.selected_sensor = self.column_checkbox.currentText()
        self.selected_sensor_dict['master'] = self.column_checkbox.currentText()

        self.update_selected_sensors_list()

        # No longer automatic plot, every plot is now trigger with the plot button
        # if self.df_csv1 is not None and self.df_csv2 is not None:
        #     self.plot_data()

    def new_sensor_to_keep(self, e: int) -> None:
        _sender = self.sender()
        _index: int = self._chk_slave_list.index(_sender)
        _slave: str = f'slave{_index}'

        _sensor = f'Sensor{e+1}'
        self.selected_sensor_dict[_slave] = _sensor
        self.update_selected_sensors_list()

    def update_selected_sensors_list(self) -> None:
        _temp_dict = dict(filter(lambda item: item[1] is not None, self.selected_sensor_dict.items()))
        self.selected_sensor_list = list(_temp_dict.values())

    def plot_data(self) -> None:
        """ plot data """

        self.overlay.show()

        if self.df_csv1 is None or self.df_csv2 is None:
            self.error_box('No data.\n\n'
                           'Please, first load data to process before trying to plot.\n\n'
                           'Pay attention you might need to load 2 csv before attempting to plot.')
            return

        self.plot_widget.removeItem(self.hover_label)
        self.plot_widget.clear()
        self.header_title.setText(f'Residual Thickness: {self.df_csv1_name}')

        x_histo = []
        y_histo = []
        # print(self.selected_sensor_list)
        for _sensor in self.selected_sensor_list:
            columns_to_keep = ['Elevation', _sensor]
            df_thickness = self.df_csv1.copy()
            df_amplitude = self.df_csv2.copy()
            df_thickness = df_thickness[columns_to_keep]
            df_amplitude = df_amplitude[columns_to_keep]

            # TODO: a filter to keep data between elevations -10K and 0. parameters exist but not the UI input fields

            filtered_thickness = self.methods.apply_filter(df_thickness,
                                                           df_amplitude,
                                                           low_filter=float(self.low_filter.text()),
                                                           high_filter=float(self.high_filter.text()),
                                                           saturation=self._params.data_saturation)

            x_1 = filtered_thickness[_sensor]  # before: self.selected_sensor
            y = df_thickness.Elevation
            color = self.methods.give_me_a_color(_sensor)
            scatter_plot = pg.ScatterPlotItem(size=2, pen=pg.mkPen(None), brush=pg.mkBrush(color + [64]))
            scatter_plot.setData(x=x_1, y=y)
            self.plot_widget.addItem(scatter_plot)

            # storing all the average by interval per sensor in a dictionary
            self.average_sensor_data[_sensor] = self.methods.average_by_intervals(_x=x_1,
                                                                                  _y=y,
                                                                                  interval=int(self.bin_filter.text()),
                                                                                  min_elevation=self._params.data_min_elevation)
            x_histo = x_histo + x_1.values.tolist()
            y_histo = y_histo + y.values.tolist()
            self.for_histo = [x_histo, y_histo]  # for histogram

        self.plot_averages()
        self.plot_defaults()
        self.overlay.emitter.trigger_signal()

    def plot_averages(self) -> None:
        """ plot the averages of data according the quantity of selected sensors
        while plotting it is filled the dictionary self.average_sensor_data """

        averaged_df: pd = self.methods.average_by_intervals_all_sensors(_data=self.average_sensor_data)
        self.average_data = averaged_df.values.tolist()

        scatter_average = pg.ScatterPlotItem(size=12, pen=pg.mkPen(None), brush=pg.mkBrush([253, 127, 62, 220]))
        scatter_average.setData(x=averaged_df.x, y=averaged_df.elevation_bin)
        self.plot_widget.addItem(scatter_average)

    def plot_clicked(self, event) -> None:
        """ originally gets the nearest average point on scene, now just clean the plot """

        if not self.average_data:
            return

        if event.double():
            self.histo.close_histo()

            # vb = self.plot_widget.plotItem.vb
            # scene_coords = event.scenePos()
            #
            # if self.plot_widget.sceneBoundingRect().contains(scene_coords):
            #     clicked_point = vb.mapSceneToView(scene_coords)
            #     print(clicked_point)

    def plot_mouse_hover(self, event) -> None:
        """ calls the histogram and a hover item """

        if not self.average_data:
            return

        mouse_relative = QCursor.pos()
        mouse_point = self.plot_widget.getViewBox().mapSceneToView(event)

        point = self.methods.closest_point(mouse_point.x(), mouse_point.y(), self.average_data)

        if self.methods.absolute_point_distance([mouse_point.x(), mouse_point.y()], point):
            self.plot_widget.removeItem(self.hover_label)
            self.plot_widget.addItem(self.hover_label)

            region = f'[{point[1]}, {point[1]+int(self.bin_filter.text())}]'
            hover_text = f'average of {round(point[0], 4)} [mm] within the region of ' \
                         f'\nelevation: {region}.' \
                         f'\nDouble click to close histogram in the selected region.'

            self.hover_label.setText(hover_text)
            self.hover_label.setPos(mouse_point.x(), mouse_point.y())

            # calling the histogram
            df_histo = pd.DataFrame({'x': self.for_histo[0], 'y': self.for_histo[1]})
            df_histo = df_histo[df_histo['x'].notna()]  # remove NaN
            _range = (point[1], point[1] + int(self.bin_filter.text()))  # lower, upper
            df_histo = df_histo[(df_histo['y'] >= _range[0]) & (df_histo['y'] <= _range[1])]
            self.get_all_calculations(df_histo, region)

            self.histo.plot_histogram(df_histo, _range, mouse_relative.x(), mouse_relative.y())
        else:
            self.plot_widget.removeItem(self.hover_label)
            self.histo.close_histo()

    def get_all_calculations(self, _df: pd, interval: str) -> None:
        """ gets all calculations using df_histo in within the range"""

        self.label_results.setText(f'Interval Results: {interval}')
        self.result_average.setText(str(round(_df.loc[:, 'x'].mean(), 8)))
        self.result_std.setText(str(round(_df.loc[:, 'x'].std(), 8)))
        self.result_min.setText(str(round(_df.loc[:, 'x'].min(), 8)))
        self.result_max.setText(str(round(_df.loc[:, 'x'].max(), 8)))
        self.result_median.setText(str(round(_df.loc[:, 'x'].median(), 8)))
        self.result_mode.setText(str(round(_df.loc[:, 'x'].mode()[0], 8)))
        trimmed_mean_20 = float(stats.trim_mean(_df.x, 0.2))
        self.result_trim_20.setText(str(round(trimmed_mean_20, 8)))
        self.result_points.setText(str(_df.loc[:, 'x'].count()))

    def plot_defaults(self) -> None:
        """ defaults for plotting """
        self.average_sensor_data: dict = dict()
        self.plot_widget.plotItem.vb.setLimits(xMin=int(self.x_min.text()),
                                               xMax=int(self.x_max.text()),
                                               yMin=int(self.y_min.text()),
                                               yMax=int(self.y_max.text()))

    def clear_plot(self) -> None:
        """ reset the UI as if it just started """
        self.df_csv1 = None
        self.df_csv2 = None
        self.average_data = None
        self.csv1_title.setText(' ')
        self.csv2_title.setText(' ')
        while self.table_csv1.rowCount() > 0:
            self.table_csv1.removeRow(0)
        while self.table_csv2.rowCount() > 0:
            self.table_csv2.removeRow(0)
        self.plot_widget.removeItem(self.hover_label)
        self.plot_widget.clear()
        self.histo.close_histo()
        self.column_checkbox.clear()
        self.histo.instances = []
        self.action_add_box.setDisabled(True)
        self.action_del_box.setDisabled(True)
        for w in self._chk_slave_list:
            self.left_panel.removeWidget(w)
        self.widget_counter = self._params.current_labels
        self._chk_slave_list = []
        self.main_widget.update()

    def add_qcombobox(self) -> None:

        if self.widget_counter <= self._params.current_widgets:
            _chk_slave = QComboBox()
            _chk_slave.currentIndexChanged.connect(self.new_sensor_to_keep)
            self.left_panel.addWidget(_chk_slave, self.widget_counter, 0, 1, 3)

            self.main_widget.update()
            self.widget_counter += 1

            self._chk_slave_list.append(_chk_slave)
            self.populate_checkbox(_chk_slave)
        else:
            self.error_box('The maximum number of slave plots are 7')

    def remove_qcombobox(self):
        n = len(self._chk_slave_list)  # last

        if n > 0:
            w = self._chk_slave_list[n-1]  # last widget
            self.left_panel.removeWidget(w)  # remove from UI widgets
            self._chk_slave_list.remove(w)  # remove from list of widgets
            self.widget_counter -= 1  # update counter positions
            self.selected_sensor_list.pop()  # remove from list to plot
        else:
            self.error_box('No slave plots to delete')

        self.main_widget.update()

    def error_box(self, message) -> None:
        dlg = QMessageBox(self)
        icon = QIcon('icons/cat.png')
        dlg.setIconPixmap(icon.pixmap(64, 64))
        dlg.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        dlg.setText(message)
        dlg.exec()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    qdarktheme.setup_theme('light')  # 'light' option
    pg.setConfigOption('background', QColor(248, 249, 250))
    pg.setConfigOption('foreground', 'k')
    image_window = CSVGraphApp()
    image_window.setWindowIcon(QIcon(r'icons/chart.png'))
    image_window.show()
    image_window.showMaximized()
    HistogramApp.instances.append(image_window)
    sys.exit(app.exec())
