import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QGridLayout, QLabel, QWidget
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg


class GraphsWindow(QWidget):
    update_graphs_signal = pyqtSignal(dict)

    def __init__(self, serial_manager, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager
        self.setWindowTitle("Telemetry Graphs")
        self.setGeometry(100, 100, 1100, 650)
        self.update_graphs_signal.connect(self.update_graphs)

        self.layout = QVBoxLayout(self)
        self.label = QLabel("Graph output will appear here.")
        self.layout.addWidget(self.label)

        # Connect serial data to update_data
        self.serial_manager.data_received.connect(self.update_data)

        self.arduino_connected = False
        self.serial_data = []
        self.arduino_port = None

        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "AccX", "AccY", "AccZ", "GyroX", "GyroY", "GyroZ", "Flight State"
        ]

        self.graph_specs = [
            ("Pressure [Pa]", ["Pressure"]),
            ("Altitude [m]", ["Altitude"]),
            ("Voltage [V]", ["Voltage"]),
            ("Accelerometer [m/s²]", ["AccX", "AccY", "AccZ"]),
            ("Gyroscope [rad/s]", ["GyroX", "GyroY", "GyroZ"]),
            ("Temperature [°C]", ["Temperature"])
        ]

        self.graphs = {}
        self.curves = {}
        self.data = {}

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        positions = [(i // 3, i % 3) for i in range(len(self.graph_specs))]
        for pos, (title, labels) in zip(positions, self.graph_specs):
            graph = self.create_graph(title, labels)
            grid_layout.addWidget(graph, *pos)

        self.serial_monitor = QLabel("Serial Monitor:\n")
        self.serial_monitor.setStyleSheet("color: black; background-color: white; padding: 6px;")
        self.serial_monitor.setFont(QFont('Arial', 10))

        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.serial_monitor)

        self.setLayout(main_layout)  # ✅ Apply layout to the main widget

    def create_graph(self, title, labels):
        plot_widget = pg.PlotWidget(title=title)
        plot_widget.setBackground("black")
        plot_widget.showGrid(x=True, y=True)

        legend = pg.LegendItem(offset=(70, 30))
        legend.setParentItem(plot_widget.getPlotItem())

        colors = ['r', 'g', 'b', 'y', 'c', 'm', 'w']

        for i, label in enumerate(labels):
            color = colors[i % len(colors)]
            self.graphs[label] = plot_widget
            self.data[label] = {'x': [], 'y': []}
            curve = plot_widget.plot([], [], pen=pg.mkPen(color=color, width=2), name=label)
            self.curves[label] = curve
            legend.addItem(curve, label)

        return plot_widget

    def update_graphs(self, new_data=None):
        if not self.arduino_connected or new_data is None:
            return

        for key, values in new_data.items():
            if key in self.curves:
                x_data = values['x'][-1000:]
                y_data = values['y'][-1000:]

                self.data[key]['x'] = x_data
                self.data[key]['y'] = y_data

                self.curves[key].setData(x_data, y_data)
                self.graphs[key].enableAutoRange(axis='x', enable=True)
                self.graphs[key].enableAutoRange(axis='y', enable=True)

    def update_data(self, telemetry_dict):
        if not telemetry_dict:
            return

        self.arduino_connected = True
        current_time = time.time()

        for key, value in telemetry_dict.items():
            if key in self.data:
                self.data[key]['x'].append(current_time)
                try:
                    self.data[key]['y'].append(float(value))
                except ValueError:
                    self.data[key]['y'].append(0.0)

        self.update_graphs(self.data)
        self.serial_monitor.setText(f"Serial Monitor:\n{telemetry_dict}")


'''if __name__ == "__main__":
    app = QApplication(sys.argv)
    serial_port = None  # Replace with actual serial port object if needed
    graphs_window = GraphsWindow(serial_port)
    graphs_window.show()
    sys.exit(app.exec_())'''