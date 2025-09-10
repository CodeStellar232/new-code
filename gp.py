# gp.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg


class GraphsWindow(QWidget):
    def __init__(self, serial_manager, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager
        self.setAttribute(Qt.WA_DeleteOnClose, False)

        self.graphs = {}
        self.curves = {}
        self.data = {}
        self.serial_data = []

        # Define six graphs with telemetry labels
        self.graph_specs = [
            ("Pressure [Pa]", ["Pressure"]),
            ("Altitude [m]", ["Altitude"]),
            ("Voltage [V]", ["Voltage"]),
            ("Accelerometer [m/s²]", ["AccX", "AccY", "AccZ"]),
            ("Gyroscope [rad/s]", ["GyroX", "GyroY", "GyroZ"]),
            ("Temperature [°C]", ["Temperature"])
        ]

        # Layout
        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        positions = [(i // 3, i % 3) for i in range(len(self.graph_specs))]
        for pos, (title, labels) in zip(positions, self.graph_specs):
            graph = self.create_graph(title, labels)
            grid_layout.addWidget(graph, *pos)

        # Serial monitor
        self.serial_monitor = QLabel("Serial Monitor:\n")
        self.serial_monitor.setStyleSheet("color: black; background-color: white; padding: 6px;")
        self.serial_monitor.setFont(QFont("Arial", 10))

        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.serial_monitor)
        self.setLayout(main_layout)

        # Connect serial manager
        
        self.serial_manager.data_received.connect(self.on_serial_data)
       
    def create_graph(self, title, labels):
        plot_widget = pg.PlotWidget(title=title)
        plot_widget.showGrid(x=True, y=True)

        # add legend if multi-axis graph
        if len(labels) > 1:
            plot_widget.addLegend(offset=(10, 10))

        colors = ['r', 'g', 'b', 'y', 'c', 'm', 'w']
        for i, label in enumerate(labels):
            self.data[label] = {"x": [], "y": []}
            curve = plot_widget.plot(
                [], [], pen=pg.mkPen(color=colors[i % len(colors)], width=2),
                name=label
            )
            self.curves[label] = curve
            self.graphs[label] = plot_widget

        return plot_widget

    def on_serial_data(self, line: str):
        """
        Expected format (example):
        TEAM123,1000,1,107,100249,28,3.30,12:34:56,23.123456,72.987654,122,9,8,-7,-1,190,-85,242,ASCENT

        Mapping (example indices):
        [1]  Packet counter
        [4]  Pressure
        [5]  Temperature
        [6]  Voltage
        [11] Altitude
        [12-14] AccX, AccY, AccZ
        [15-17] GyroX, GyroY, GyroZ
        """
        try:
            parts = line.strip().split(",")
            if len(parts) < 18:
                return

            t = int(parts[1])            # packet number
            pressure = float(parts[4])
            temp = float(parts[5])
            voltage = float(parts[6])
            altitude = float(parts[11])
            accx, accy, accz = float(parts[12]), float(parts[13]), float(parts[14])
            gyrox, gyroy, gyroz = float(parts[15]), float(parts[16]), float(parts[17])

            values = {
                "Pressure": pressure,
                "Temperature": temp,
                "Voltage": voltage,
                "Altitude": altitude,
                "AccX": accx, "AccY": accy, "AccZ": accz,
                "GyroX": gyrox, "GyroY": gyroy, "GyroZ": gyroz,
            }

            for key, val in values.items():
                if key not in self.data:
                    continue
                self.data[key]["x"].append(t)
                self.data[key]["y"].append(val)

                # Keep only last 500 points
                if len(self.data[key]["x"]) > 500:
                    self.data[key]["x"] = self.data[key]["x"][-500:]
                    self.data[key]["y"] = self.data[key]["y"][-500:]

                self.curves[key].setData(self.data[key]["x"], self.data[key]["y"])

            # Update serial monitor
            self.serial_data.append(line)
            if len(self.serial_data) > 2:
                self.serial_data = self.serial_data[-2:]
            self.serial_monitor.setText("Serial Monitor:\n" + "\n".join(self.serial_data))

        except Exception as e:
            print(f"[GraphsWindow] Error parsing line: {line} ({e})")

    
            self.serial_manager.data_received.disconnect(self.on_serial_data)
       
       
