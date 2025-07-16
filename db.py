import sys
import os
import pandas as pd
from serial_port import serial_manager

from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QGridLayout, QWidget, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class DbWindow(QWidget):
    def __init__(self):
        super().__init__()

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

        serial_manager.data_received.connect(self.receive_telemetry_data)

        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", 
        ]
        self.data_store = []
        self.labels = {}
        self.values = {}

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15
                               )

        telemetry_group = QGroupBox("Telemetry Dashboard")
        telemetry_layout = QGridLayout()
        telemetry_layout.setHorizontalSpacing(30
                                              )
        telemetry_layout.setVerticalSpacing(30)

        for i, key in enumerate(self.telemetry_fields):
            row = i // 3
            col = i % 3

            card = QGroupBox()
            card.setMinimumSize(240, 100)
            card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
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
            label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

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

        # Right Panel with Save Button
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        self.save_button = QPushButton("Save Data to CSV .PDF")
        self.save_button.clicked.connect(self.save_data)
        self.save_button.setMinimumHeight(45)
        right_layout.addWidget(self.save_button)

        main_layout.addWidget(telemetry_group, stretch=4)
        main_layout.addLayout(right_layout, stretch=1)

    def save_data(self):
        if not self.data_store:
            QMessageBox.warning(self, "Warning", "No data available to save.")
            return

        documents_folder = os.path.join(os.path.expanduser("~"), "Documents")
        csv_path = os.path.join(documents_folder, "dashboard_data.csv")
        pdf_path = os.path.join(documents_folder, "dashboard_data.pdf")

        try:
            df = pd.DataFrame(self.data_store)
            df.to_csv(csv_path, index=False)

            with open(pdf_path, "w") as pdf_file:
                pdf_file.write("PDF export placeholder.\n\n")
                pdf_file.write(df.to_string(index=False))

            QMessageBox.information(self, "Success", f"Data saved to:\n{csv_path}\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")

    def update_data_store(self, telemetry_dict, data):
        self.data_store.append(telemetry_dict)
        for key, value in telemetry_dict.items():
            if key in self.values:
                self.values[key].setText(str(value))

    def receive_telemetry_data(self, line: str):
        parts = line.strip().split(',')
        if len(parts) != len(self.telemetry_fields):
            return
        telemetry_dict = dict(zip(self.telemetry_fields, parts))
        self.update_data_store(telemetry_dict, line)


# To test this page standalone:
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = DbWindow()
#     win.show()
#     sys.exit(app.exec_())
