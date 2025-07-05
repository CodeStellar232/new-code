from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import QTimer, QUrl
import folium
import random
import os
import sys
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapPage(QWidget):
    def __init__(self):
        super().__init__()
        #s#elf.serial = serial_port  # Serial port passed from the main window

        layout = QVBoxLayout()

        self.gps_label = QLabel("📍 GPS Coordinates: Loading...")
        layout.addWidget(self.gps_label)

        if QWebEngineView:
            self.map_widget = QWebEngineView()
            layout.addWidget(self.map_widget)
            self.map_file_path = os.path.join(os.path.dirname(__file__), "map.html")
            self.update_map(37.7749, -122.4194)  # Default to San Francisco
        else:
            error_label = QLabel("❌ Map view is unavailable. Please install PyQtWebEngine.")
            layout.addWidget(error_label)

        self.setLayout(layout)

        # Timer for GPS updates (simulated)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gps)
        self.timer.start(3000)

    def update_map(self, lat, lon):
        """Updates the map with new GPS data"""
        try:
            map_obj = folium.Map(location=[lat, lon], zoom_start=15, tiles="Stamen Terrain")
            folium.Marker([lat, lon], popup="Rocket Position", icon=folium.Icon(color="red")).add_to(map_obj)

            map_obj.save(self.map_file_path)
            self.map_widget.setUrl(QUrl.fromLocalFile(self.map_file_path))
        except Exception as e:
            self.gps_label.setText(f"❌ Failed to update map: {e}")

    def update_gps(self):
        """Simulates GPS movement"""
        lat_offset = random.uniform(-0.001, 0.001)
        lon_offset = random.uniform(-0.001, 0.001)
        lat = 37.7749 + lat_offset
        lon = -122.4194 + lon_offset
        self.gps_label.setText(f"📍 GPS Coordinates: {lat:.5f}, {lon:.5f}")
        self.update_map(lat, lon)


