# cs.py
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QLineEdit, QPushButton, QListWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QCheckBox, QGroupBox, QSizePolicy, QGridLayout
)
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt
from datetime import datetime


class ConsoleWindow(QWidget):
    def __init__(self, serial_manager, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager

        self.total_packets = 0
        self.missing_packets = 0
        self.corrupt_packets = 0
        self.last_packet_id = -1
        self.last_packet_time = "N/A"

        
       
        self.serial_manager.data_received.connect(self.update_data)
       

        self.headers = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]

        self.packet_labels = {}
        self.value_labels = {}

        self.setup_ui()
        self.setStyleSheet("""
    QGroupBox {
        border: 2px solid #555;
        border-radius: 8px;
        margin-top: 10px;
        padding: 10px;
        background-color: #f4f4f4;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px;
        color: #333;
        font-weight: bold;
    }

    QTextEdit, QLineEdit, QListWidget, QLabel {
        background-color: white;
        border: 1px solid #aaa;
        border-radius: 5px;
    }

    QPushButton {
        background-color: #d0d0d0;
        border-radius: 5px;
        padding: 6px;
    }

    QPushButton:hover {
        background-color: #bbb;
    }

    QCheckBox {
        padding-left: 5px;
    }
""")

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Left console section
        console_group = QGroupBox("Console Dashboard")
        console_layout = QVBoxLayout(console_group)

        command_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter Command")

        self.send_button = QPushButton("Send")
        self.clear_button = QPushButton("Clear")
        self.timestamp_checkbox = QCheckBox("Timestamp")
        self.timestamp_checkbox.setChecked(True)

        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_button)
        command_layout.addWidget(self.clear_button)
        command_layout.addWidget(self.timestamp_checkbox)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)

        self.raw_telemetry_display = QTextEdit()
        self.raw_telemetry_display.setReadOnly(True)

        split_layout = QHBoxLayout()
        split_layout.addWidget(self.console_output, 7)
        split_layout.addWidget(self.raw_telemetry_display, 3)

        right_side_layout = QVBoxLayout()
        self.command_history_list = QListWidget()

        command_history_group = QGroupBox("Command History")
        command_history_layout = QVBoxLayout(command_history_group)
        command_history_layout.addWidget(self.command_history_list)

        packet_info_group = QGroupBox("Packet Info")
        packet_info_layout = QGridLayout(packet_info_group)
        packet_headers = [
            "Total Packets", "Missing Packets", "Packet Loss %",
            "Corrupt Packets", "Last Packet ID", "Last Packet Time"
        ]
        for row, name in enumerate(packet_headers):
            packet_info_layout.addWidget(QLabel(f"{name}:"), row, 0)
            label = QLabel("-")
            self.packet_labels[name] = label
            packet_info_layout.addWidget(label, row, 1)

        right_side_layout.addWidget(command_history_group)
        right_side_layout.addWidget(packet_info_group)
        split_layout.addLayout(right_side_layout, 3)

        console_layout.addLayout(command_layout)
        console_layout.addLayout(split_layout)
        main_layout.addWidget(console_group, 3)

        # Right telemetry panel
        telemetry_group = QGroupBox("Raw Telemetry")
        telemetry_layout = QVBoxLayout(telemetry_group)
        telemetry_values_layout = QGridLayout()

        for i, header in enumerate(self.headers):
            telemetry_values_layout.addWidget(QLabel(f"{header}:"), i, 0)
            value_label = QLabel("-")
            self.value_labels[header] = value_label
            telemetry_values_layout.addWidget(value_label, i, 1)
        telemetry_layout.addLayout(telemetry_values_layout)
        main_layout.addWidget(telemetry_group, 1)

        # Button connections
        self.send_button.clicked.connect(self.send_command)
        self.clear_button.clicked.connect(self.clear_console)
        self.command_input.returnPressed.connect(self.send_command)
        self.command_history_list.itemClicked.connect(
            lambda item: self.command_input.setText(item.text())
        )

    def send_command(self):
        command = self.command_input.text().strip()
        if command:
            timestamp = datetime.now().strftime("[%H:%M:%S] ") if self.timestamp_checkbox.isChecked() else ""
            self.console_output.append(f"{timestamp}> {command}")
            self.command_history_list.addItem(command)
            self.command_input.clear()

    def clear_console(self):
        self.console_output.clear()
        self.raw_telemetry_display.clear()
        self.command_history_list.clear()
        self.total_packets = 0
        self.missing_packets = 0
        self.corrupt_packets = 0
        self.last_packet_id = -1
        self.last_packet_time = "N/A"
        for label in self.packet_labels.values():
            label.setText("-")
        for label in self.value_labels.values():
            label.setText("-")

    def update_data(self, data: str):
        # Called via Qt signal; safe to update UI here.
        try:
            self.console_output.append(data)
            self.console_output.moveCursor(QTextCursor.End)
            self.raw_telemetry_display.append(data)

            self.parse_telemetry(data)
            self.update_packet_info(data)
        except Exception as e:
            # Avoid crashing the GUI due to malformed data
            print(f"[ConsoleWindow] update_data error: {e}")

    def parse_telemetry(self, line: str):
        parts = line.strip().split(',')
        if len(parts) != len(self.headers):
            # don't attempt to map if format isn't exact
            return
        for header, value in zip(self.headers, parts):
            # update labels defensively
            if header in self.value_labels:
                self.value_labels[header].setText(value)

    def extract_packet_id(self, parts):
        try:
            return int(parts[2])
        except Exception:
            return self.last_packet_id + 1

    def update_packet_info(self, line: str):
        parts = line.strip().split(',')
        if len(parts) < 3:
            self.corrupt_packets += 1
        else:
            try:
                packet_id = self.extract_packet_id(parts)
                if self.last_packet_id != -1 and packet_id > self.last_packet_id + 1:
                    self.missing_packets += packet_id - (self.last_packet_id + 1)
                self.last_packet_id = packet_id
                self.total_packets += 1
                self.last_packet_time = datetime.now().strftime("%H:%M:%S")
            except Exception:
                self.corrupt_packets += 1

        total_expected = self.total_packets + self.missing_packets
        packet_loss = (self.missing_packets / total_expected) * 100 if total_expected else 0

        # update UI
        self.packet_labels["Total Packets"].setText(str(self.total_packets))
        self.packet_labels["Missing Packets"].setText(str(self.missing_packets))
        self.packet_labels["Packet Loss %"].setText(f"{packet_loss:.2f}")
        self.packet_labels["Corrupt Packets"].setText(str(self.corrupt_packets))
        self.packet_labels["Last Packet ID"].setText(str(self.last_packet_id))
        self.packet_labels["Last Packet Time"].setText(self.last_packet_time)
