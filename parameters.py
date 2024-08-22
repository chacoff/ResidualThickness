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