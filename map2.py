import os
import folium
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSizePolicy
)
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont
import threading
import time


class MapPage(QWidget):
    
    _map_ready = pyqtSignal(str)

    def __init__(self, serial_manager, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager

        self.lat = 0.0
        self.lon = 0.0
        self.altitude = "0"
        self.flight_mode = "N/A"
        self.zoom_level = 12

        self._map_lock = threading.Lock()
        self._last_refresh = 0.0
        self._refresh_interval = 0.5  # seconds min between refreshes
        self._generating = False

        self.init_ui()
        #self.setup_connections()
        self._map_ready.connect(self._on_map_ready)
        #self.serial_manager.data_received.connect(self.update_data)

        # create initial map
        self._enqueue_map_refresh()

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
        self.label_mode = QLabel("Flight Mode: --")

        for label in (self.label_alt, self.label_mode):
            label.setFont(QFont("Nirmala Text", 11))
            label.setStyleSheet("color: #000;")
            telemetry_bar.addWidget(label)

        telemetry_bar.addStretch()

        # Map view
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Zoom buttons
        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("-")
        for btn in (self.zoom_in_btn, self.zoom_out_btn):
            btn.setFixedSize(30, 30)

        telemetry_bar.addWidget(self.zoom_in_btn)
        telemetry_bar.addWidget(self.zoom_out_btn)

        # Add to map box
        map_layout.addLayout(telemetry_bar)
        map_layout.addWidget(self.web_view)

        # Add to main layout
        main_layout.addWidget(map_box)

    
        self.serial_manager.data_received.connect(self.update_location_map)
        

        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

    def update_location_map(self, data: str):
        """
        Parse incoming telemetry and update map/labels.
        Expected format (from navg): 
        TEAMID,PACKET_NO,...,LAT,LON,ALT,...,STATE
        """
        try:
            parts = data.strip().split(",")
            if len(parts) < 11:
                return  # not enough data

            lat = float(parts[8])
            lon = float(parts[9])
            alt = parts[10]
            mode = parts[-1] if len(parts) > 18 else "N/A"

            # update state
            self.lat = lat
            self.lon = lon
            self.altitude = alt
            self.flight_mode = mode

            self.update_labels()
            self._enqueue_map_refresh()

        except Exception as e:
            print(f"[MapPage] Error parsing data: {e}")
            
    def convert_data(data: str, expected_type: str):
    
        if expected_type == "string":
            return str(data)

        elif expected_type == "int":
            return int(data)

        elif expected_type == "float":
            return float(data)

        elif expected_type == "char":
            return data[0] if len(data) > 0 else ''

        elif expected_type == "uint8_t":
            val = int(data)
            return val if 0 <= val <= 255 else None

        else:
            # fallback
            return str(data)

    def update_labels(self):
        try:
            self.label_alt.setText(f"Altitude: {self.altitude} m")
            self.label_mode.setText(f"Flight Mode: {self.flight_mode}")
        except Exception:
            pass

    def _enqueue_map_refresh(self):
        now = time.time()
        if self._generating:
            return
        if now - self._last_refresh < self._refresh_interval:
            delay_ms = int((self._refresh_interval - (now - self._last_refresh)) * 1000) + 10
            QTimer.singleShot(delay_ms, self._start_map_generation_thread)
        else:
            self._start_map_generation_thread()

    def _start_map_generation_thread(self):
        if self._generating:
            return
        self._generating = True
        t = threading.Thread(target=self._generate_map_html, daemon=True)
        t.start()

    def _generate_map_html(self):
        try:
            m = folium.Map(location=[self.lat, self.lon], zoom_start=self.zoom_level)
            folium.Marker(
                [self.lat, self.lon],
                tooltip=f"Lat:{self.lat}, Lon:{self.lon}, Alt:{self.altitude}"
            ).add_to(m)

            tmp_path = os.path.abspath("map.html")
            m.save(tmp_path)
            self._map_ready.emit(tmp_path)
            self._last_refresh = time.time()
        except Exception as e:
            print(f"[MapPage] Map generation error: {e}")
        finally:
            self._generating = False

    def _on_map_ready(self, path):
        try:
            self.web_view.setUrl(QUrl.fromLocalFile(path))
        except Exception as e:
            print(f"[MapPage] Failed to set URL: {e}")

    def zoom_in(self):
        if self.zoom_level < 20:
            self.zoom_level += 1
            self._enqueue_map_refresh()

    def zoom_out(self):
        if self.zoom_level > 2:
            self.zoom_level -= 1
            self._enqueue_map_refresh()
