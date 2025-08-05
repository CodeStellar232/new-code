# map2.py
import sys
import os
import folium
import serial
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFrame,QApplication, QMainWindow
from PyQt5.QtCore import  QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont
from serial_port import serial_manager


class MapPage(QWidget):
     def __init__(self):
        super().__init__()

        self.setWindowTitle("Map")
        self.setGeometry(150, 150, 1280, 750)

        self.lat = None
        self.lon = None
        self.zoom_level = 13
        self.altitude = "--"
        self.speed = "--"
        self.flight_mode = "--"

        self.initUI()
        serial_manager.data_received.connect(self.update_data)

     def initUI(self):
        layout = QVBoxLayout(self)

        # Main frame
        self.frame = QFrame()
        frame_layout = QHBoxLayout(self.frame)

        # Left: Telemetry Info + Zoom
        self.groupBox = QGroupBox("Telemetry Info")
        self.groupBox.setMinimumWidth(200)
        info_layout = QVBoxLayout(self.groupBox)

        font = QFont("Nirmala Text", 11)

        self.label_latlon = QLabel("Lat, Lon: --, --")
        self.label_alt = QLabel("Altitude: --")
        self.label_speed = QLabel("Speed: --")
        self.label_mode = QLabel("Flight Mode: --")

        for label in [self.label_latlon, self.label_alt, self.label_speed, self.label_mode]:
            label.setFont(font)
            info_layout.addWidget(label)

        # Round Zoom Buttons
        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("-")

        self.zoom_in_btn.setStyleSheet(self.round_button_style())
        self.zoom_out_btn.setStyleSheet(self.round_button_style())
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        info_layout.addWidget(self.zoom_in_btn)
        info_layout.addWidget(self.zoom_out_btn)

        # Right: Map view
        self.map_view = QWebEngineView()
        self.generate_map()
        self.refresh_map()

        # Assemble layout
        frame_layout.addWidget(self.groupBox)
        frame_layout.addWidget(self.map_view)
        layout.addWidget(self.frame)

     def round_button_style(self):
        return """
        QPushButton {
            border: 2px solid #444;
            border-radius: 25px;
            background-color: black;
            color: white;
            min-width: 50px;
            min-height: 50px;
            max-width: 50px;
            max-height: 50px;
            font-size: 18px;
        }
        QPushButton:hover {
            background-color: #222;
        }
        """

     def setup_serial(self):
        try:
            self.serial_port = serial.Serial('COM3', 9600, timeout=1)
        except serial.SerialException:
            self.serial_port = None
            print("⚠️ Serial connection failed. Check COM port.")

     def read_serial_data(self):
        if self.serial_port and self.serial_port.in_waiting:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                print(f"[Serial] {line}")
                data = line.split(",")
                if len(data) >= 5:
                    self.lat = float(data[0])
                    self.lon = float(data[1])
                    self.altitude = data[2]
                    self.speed = data[3]
                    self.flight_mode = data[4]

                    self.update_labels()
                    self.refresh_map()
            except Exception as e:
                print(f"Error reading serial: {e}")

     def update_labels(self):
        self.label_latlon.setText(f"Lat, Lon: {self.lat:.5f}, {self.lon:.5f}")
        self.label_alt.setText(f"Altitude: {self.altitude} m")
        self.label_speed.setText(f"Speed: {self.speed} km/h")
        self.label_mode.setText(f"Flight Mode: {self.flight_mode}")

     def generate_map(self):
        m = folium.Map(location=[self.lat, self.lon], zoom_start=self.zoom_level)
        folium.Marker([self.lat, self.lon], tooltip="Live Position").add_to(m)
        m.save("map.html")

     def refresh_map(self):
        self.generate_map()
        self.map_view.setUrl(QUrl.fromLocalFile(os.path.abspath("map.html")))

     def zoom_in(self):
        if self.zoom_level < 18:
            self.zoom_level += 1
            self.refresh_map()

     def zoom_out(self):
        if self.zoom_level > 2:
            self.zoom_level -= 1
            self.refresh_map()
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    map_page = MapPage()
    window.setCentralWidget(map_page)
    window.setWindowTitle("Live Map with Telemetry")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())