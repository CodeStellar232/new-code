# db.py
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QGridLayout, QMessageBox, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from serial_port import SerialManager


class DbWindow(QWidget):
    def __init__(self, serial_manager, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager

        self.setWindowTitle("Dashboard")
        self.setGeometry(150, 150, 1280, 750)
        self.setStyleSheet("""
            QWidget {
                background-color: #ECEFF1;
                font-family: Segoe UI;
                font-size: 12pt;
            }
            QLabel {
                color: #37474F;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QGroupBox {
                border: 1px solid #B0BEC5;
                border-radius: 10px;
                background-color: white;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 8px 0px;
            }
        """)

        # Telemetry fields
        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", " GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]

        # SI Units for fields
        self.units = {
            "Team ID": "",
            "Timestamp": "s",
            "Packet Count": "",
            "Altitude": "m",
            "Pressure": "Pa",
            "Temperature": "°C",
            "Voltage": "V",
            "GNSS Time": "s",
            "GNSS Latitude": "°",
            "GNSS Longitude": "°",
            "GNSS Altitude": "m",
            " GNSS Satellites": "",
            "Accel X": "m/s²",
            "Accel Y": "m/s²",
            "Accel Z": "m/s²",
            "Gyro X": "°/s",
            "Gyro Y": "°/s",
            "Gyro Z": "°/s",
            "Flight State": ""
        }

        # Connect to serial manager
        self.serial_manager.data_received.connect(self.update_data)

        self.data_store = []
        self.labels = {}
        self.values = {}

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Scroll area for telemetry dashboard
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        telemetry_group = QGroupBox("Telemetry Dashboard")
        telemetry_layout = QGridLayout()
        telemetry_layout.setHorizontalSpacing(20)
        telemetry_layout.setVerticalSpacing(20)

        # Arrange cards in 5 columns
        for i, key in enumerate(self.telemetry_fields):
            row = i // 5
            col = i % 5

            card = QGroupBox()
            card.setMinimumSize(180, 90)  # smaller cards
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

            card.setStyleSheet("""
                QGroupBox {
                    background-color: #F5F7F9;
                    border: 1px solid #CFD8DC;
                    border-radius: 10px;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(5)

            label = QLabel(key)
            label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

            value = QLabel("N/A")
            value.setFont(QFont("Segoe UI", 11))
            value.setStyleSheet("color: #1E88E5;")
            value.setWordWrap(True)
            value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

            self.labels[key] = label
            self.values[key] = value

            card_layout.addWidget(label)
            card_layout.addWidget(value)
            telemetry_layout.addWidget(card, row, col)

        telemetry_group.setLayout(telemetry_layout)
        scroll_area.setWidget(telemetry_group)

        # Right Panel with Save Button
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)
        self.save_button = QPushButton("Save Data to CSV")
        self.save_button.clicked.connect(self.save_data)
        self.save_button.setMinimumHeight(45)
        right_layout.addWidget(self.save_button)

        main_layout.addWidget(scroll_area, stretch=4)
        main_layout.addLayout(right_layout, stretch=1)

    def save_data(self):
        if not self.data_store:
            QMessageBox.warning(self, "Warning", "No data available to save.")
            return

        from PyQt5.QtWidgets import QFileDialog
        options = QFileDialog.Options()
        csv_path, _ = QFileDialog.getSaveFileName(
            self, "Save Data to CSV", os.path.join(os.path.expanduser("~"), "dashboard_data.csv"),
            "CSV Files (*.csv);;All Files (*)", options=options
        )
        if not csv_path:
            return

        try:
            df = pd.DataFrame(self.data_store)
            df.rename(columns=lambda c: f"{c} ({self.units.get(c,'')})" if self.units.get(c,"") else c, inplace=True)
            df.to_csv(csv_path, index=False)
            QMessageBox.information(self, "Success", f"Data saved to:\n{csv_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")

    @staticmethod
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
            return str(data)

    def update_data_store(self, telemetry_dict):
        # Only update fields that exist in self.values
        display_dict = {}
        for key, value in telemetry_dict.items():
            if key in self.values:
                unit = self.units.get(key, "")
                display_text = f"{value} {unit}" if unit else str(value)
                self.values[key].setText(display_text)
                display_dict[key] = value
        self.data_store.append(display_dict)

    def update_data(self, line: str):
        try:
            parts = line.strip().split(',')

            telemetry_dict = {}
            for i, key in enumerate(self.telemetry_fields):
                if i < len(parts):
                    value = parts[i].strip()
                else:
                    value = "N/A"  # Fill missing fields

                # Optionally, clean the key name (remove leading/trailing spaces)
                clean_key = key.strip()
                telemetry_dict[clean_key] = value

            self.update_data_store(telemetry_dict)
        except Exception as e:
            print(f"[DbWindow] update_data error: {e}")

