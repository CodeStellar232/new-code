# map2.py

import os
import folium
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont
from serial_port import serial_manager


class MapPage(QWidget):
    def __init__(self):
        super().__init__()

        self.lat = 0.0
        self.lon = 0.0
        self.altitude = "0"
        self.speed = "0"
        self.flight_mode = "N/A"
        self.zoom_level = 17

        self.init_ui()
        self.setup_connections()
        self.refresh_map()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Main container frame
        map_box = QGroupBox("Map View")
        map_layout = QVBoxLayout()
        map_box.setLayout(map_layout)

        # Top bar: Telemetry labels
        telemetry_bar = QHBoxLayout()
        telemetry_bar.setSpacing(20)

        self.label_alt = QLabel("Altitude: --")
        self.label_speed = QLabel("Speed: --")
        self.label_mode = QLabel("Flight Mode: --")

        for label in (self.label_alt, self.label_speed, self.label_mode):
            label.setFont(QFont("Nirmala Text", 11))
            label.setStyleSheet("color: #000;")
            telemetry_bar.addWidget(label)

        telemetry_bar.addStretch()
        serial_manager.data_received.connect(self.parse_data)

        # Zoom buttons
        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("-")

        for btn in (self.zoom_in_btn, self.zoom_out_btn):
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid #444;
                    border-radius: 15px;
                    background-color: black;
                    color: white;
                }
            """)
        telemetry_bar.addWidget(self.zoom_in_btn)
        telemetry_bar.addWidget(self.zoom_out_btn)

        # Map view
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to map box
        map_layout.addLayout(telemetry_bar)
        map_layout.addWidget(self.web_view)

        # Add to main layout
        main_layout.addWidget(map_box)

    def setup_connections(self):
        serial_manager.data_received.connect(self.update_location_map)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

    def update_location_map(self, data):
        try:
            lat, lon, alt, spd, mode = self.parse_data(data)
            self.lat = lat
            self.lon = lon
            self.altitude = alt
            self.speed = spd
            self.flight_mode = mode
            self.update_labels()
            self.refresh_map()
        except Exception as e:
            print(f"[MapPage] Error parsing data: {e}")

    def parse_data(self, data):
        # Expected format: LAT:12.34,LON:56.78,ALT:123,SPD:45,FMD:STAB
        parts = data.strip().split(",")
        lat = float(parts[0].split(":")[1])
        lon = float(parts[1].split(":")[1])
        alt = parts[2].split(":")[1]
        spd = parts[3].split(":")[1]
        mode = parts[4].split(":")[1]
        return lat, lon, alt, spd, mode

    def update_labels(self):
        self.label_alt.setText(f"Altitude: {self.altitude} m")
        self.label_speed.setText(f"Speed: {self.speed} km/h")
        self.label_mode.setText(f"Flight Mode: {self.flight_mode}")

    def refresh_map(self):
        m = folium.Map(location=[self.lat, self.lon], zoom_start=self.zoom_level)
        folium.Marker([self.lat, self.lon], tooltip="Current Location").add_to(m)
        m.save("map.html")
        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath("map.html")))

    def zoom_in(self):
        if self.zoom_level < 20:
            self.zoom_level += 1
            self.refresh_map()

    def zoom_out(self):
        if self.zoom_level > 2:
            self.zoom_level -= 1
            self.refresh_map()

'''if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MapPage()
    window.show()
    sys.exit(app.exec_())'''