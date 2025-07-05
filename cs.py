import sys
from PyQt5.QtWidgets import(
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QTextEdit, QLineEdit, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QGroupBox, QSizePolicy, QGridLayout)

class ConsoleWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Console")
        self.resize(900, 600)  # Use resize, not setGeometry

        # Set expanding size policy for the main window
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

        self.total_packets = 0
        self.missing_packets = 0
        self.corrupt_packets = 0
        self.last_packet_id = -1
        self.last_packet_time = "N/A"
        
        self.headers = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]
        
        self.value_labels = {}
        self.packet_labels = {}
        self.initUI()
  
    def initUI(self):
        # Use a central widget for layout
        main_layout = QHBoxLayout(self)  # Set layout directly on self

        console_group = QGroupBox("Console")
        console_layout = QVBoxLayout(console_group)

        command_layout = QHBoxLayout()
        command_layout.setSizeConstraint(QHBoxLayout.SetFixedSize)
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter Command")

        self.send_button = QPushButton("Send")
        self.send_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.send_button.setMinimumWidth(100)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.clear_button.setMinimumWidth(100) 

        self.timestamp_checkbox = QCheckBox("Timestamp")
        self.timestamp_checkbox.setChecked(True)
        self.send_button.setMinimumWidth(100)

        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_button)
        command_layout.addWidget(self.clear_button)
        command_layout.addWidget(self.timestamp_checkbox)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add raw telemetry display widget
        self.raw_telemetry_display = QTextEdit()
        self.raw_telemetry_display.setReadOnly(True)
        self.raw_telemetry_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        split_layout = QHBoxLayout()
        split_layout.addWidget(self.console_output, 7)
        split_layout.addWidget(self.raw_telemetry_display, 3)

        right_side_layout = QVBoxLayout()

        self.command_history_list = QListWidget()
        command_history_group = QGroupBox("Command History")
        command_history_layout = QVBoxLayout(command_history_group)
        command_history_layout.addWidget(self.command_history_list)

        packet_info_group = QGroupBox("Packet Info")
        packet_info_layout = QGridLayout()
        packet_info_group.setLayout(packet_info_layout)
        packet_info_group.setFixedHeight(300)

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

        self.send_button.clicked.connect(self.send_command)
        self.clear_button.clicked.connect(self.clear_console)
        self.command_input.returnPressed.connect(self.send_command)
        self.command_history_list.itemClicked.connect(lambda item: self.command_input.setText(item.text()))

    def send_command(self):
        pass

    def clear_console(self):
        self.console_output.clear()

    def update_data(self, data: str):
        self.console_output.append(f"{data}")
        self.raw_telemetry_display.append(data)
        self.command_history_list.addItem(data)

'''if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConsoleWindow()
    window.show()
    sys.exit(app.exec_())'''