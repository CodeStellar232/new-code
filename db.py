import sys
import os
import pandas as pd

from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QGridLayout, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt


class DbWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard")
        self.setGeometry(150, 150, 1280, 750)
        self.resize(600, 550)

        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]
        self.data_store = []  # List of dicts to store telemetry data
        self.labels = {}
        self.values = {}

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        telemetry_group = QGroupBox("Dashboard")
        telemetry_layout = QGridLayout()

        for i, key in enumerate(self.telemetry_fields):
            row = i // 3
            col = i % 3

            field_group = QGroupBox()
            field_layout = QHBoxLayout(field_group)
            field_layout.setContentsMargins(5, 5, 5, 5)
            field_layout.setSpacing(5)

            label = QLabel(f"{key}:")
            value = QLabel("N/A")
            self.labels[key] = label
            self.values[key] = value

            field_layout.addWidget(label)
            field_layout.addWidget(value)
            telemetry_layout.addWidget(field_group, row, col)

        telemetry_group.setLayout(telemetry_layout)
        telemetry_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")

        right_layout = QVBoxLayout()
        self.save_button = QPushButton("Save Data to CSV & PDF", self)
        self.save_button.clicked.connect(self.save_data)
        right_layout.addWidget(self.save_button)

        main_layout.addWidget(telemetry_group)
        main_layout.addLayout(right_layout)

    def save_data(self):
        if not self.data_store:
            QMessageBox.warning(self, "Warning", "No data available to save.")
            return

        documents_folder = os.path.join(os.path.expanduser("~"), "Documents")
        csv_path = os.path.join(documents_folder, "dashboard_data.csv")
        pdf_path = os.path.join(documents_folder, "dashboard_data.pdf")

        try:
            # Save to CSV
            df = pd.DataFrame(self.data_store)
            df.to_csv(csv_path, index=False)

            # Save dummy PDF (placeholder)
            with open(pdf_path, "w") as pdf_file:
                pdf_file.write("PDF export placeholder.\n\n")
                pdf_file.write(df.to_string(index=False))

            QMessageBox.information(self, "Success", f"Data saved to:\n{csv_path}\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")

    def update_data_store(self, telemetry_dict, data):
        """Call this method to update data store from other pages."""
        self.data_store.append(telemetry_dict)
        for key, value in telemetry_dict.items():
            if key in self.values:
                self.values[key].setText(str(value))
        if hasattr(self, 'label_status'):
            self.label_status.setText(f"Live: {data}")


'''if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_window = DbWindow()
    db_window.show()
    sys.exit(app.exec_())'''