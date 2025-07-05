import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import threading
import os
import pandas as pd

class Ui_GCA(QWidget):
    data_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]
        self.textBrowser = QTextBrowser()
        self.serial_connection = None
        self.data_logging_enabled = False

    def setupUi(self, GCA):
        GCA.setObjectName("GCA")
        GCA.resize(1132, 650)
        self.gridLayout = QGridLayout(GCA)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QFrame(GCA)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setObjectName("frame")

        # Serial Port Settings
        self.groupBox_3 = QGroupBox(self.frame)
        self.groupBox_3.setGeometry(QRect(100, 1, 221, 211))
        self.groupBox_3.setObjectName("groupBox_3")

        self.label_2 = QLabel("PORT", self.groupBox_3)
        self.label_2.setGeometry(QRect(10, 30, 55, 16))
        self.label_3 = QLabel("BAUD RATE", self.groupBox_3)
        self.label_3.setGeometry(QRect(10, 90, 61, 16))

        self.comboBox_2 = QComboBox(self.groupBox_3)
        self.comboBox_2.setGeometry(QRect(10, 60, 201, 22))

        self.comboBox_3 = QComboBox(self.groupBox_3)
        self.comboBox_3.setGeometry(QRect(10, 110, 201, 22))
        self.comboBox_3.addItems(["1200", "2400", "4800", "9600", "14400", "19200", "38400", "57600", "115200"])

        self.pushButton_2 = QPushButton("CONNECT", self.groupBox_3)
        self.pushButton_2.setGeometry(QRect(30, 150, 171, 28))
        self.pushButton_2.clicked.connect(self.toggle_serial_connection)

        # Data Logger Section 
        self.groupBox_4 = QGroupBox(self.frame)
        self.groupBox_4.setGeometry(QRect(100, 220, 221, 130))  # Increased height from 100 to 130
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("Data Logger")

        self.radio_log = QRadioButton("Log Data", self.groupBox_4)
        self.radio_log.setGeometry(QRect(20, 30, 100, 20))

        self.radio_disable = QRadioButton("Disable Data", self.groupBox_4)
        self.radio_disable.setGeometry(QRect(20, 60, 100, 20))
        self.radio_disable.setChecked(True)
        self.radio_disable.toggled.connect(self.disable_data_logging)

        self.radio_log.toggled.connect(self.toggle_data_logging)
        self.radio_disable.toggled.connect(self.toggle_data_logging)

        self.refresh_ports()
        self.data_logging_enabled = False
        
        # Place the save button just below the Data Logger section
        self.save_button = QPushButton("Save Data to CSV & PDF", self.groupBox_4)
        self.save_button.setGeometry(QRect(20, 95, 180, 28))  # Y position moved down to 95
        self.save_button.clicked.connect(self.save_data)

    def retranslateUi(self, GCA):
        _translate = QCoreApplication.translate
        GCA.setWindowTitle(_translate("GCA", "RECEIVER"))
        
        self.groupBox_3.setTitle(_translate("GCA", "Serial Port Settings"))
        self.groupBox_4.setTitle(_translate("GCA", "Data Logger"))
        self.clear_btn.setText(_translate("GCA", "Clear"))
        self.pushButton_2.setText(_translate("GCA", "CONNECT"))
        self.radio_log.setText(_translate("GCA", "Log Data"))
        self.radio_disable.setText(_translate("GCA", "Disable Data"))
        self.save_button.setText(_translate("GCA", "Save Data to CSV & PDF"))
        

    def toggle_serial_connection(self):
        if self.pushButton_2.text() == "CONNECT":
            self.connect_serial()
        else:
            self.disconnect_serial()

    def connect_serial(self):
        port = self.comboBox_2.currentText()
        baud_rate = int(self.comboBox_3.currentText())
        if not port:
            QMessageBox.warning(None, "Warning", "No COM port selected!")
            return
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        try:
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            self.textBrowser.append(f"✅ Connected to {port} at {baud_rate} baud.")
            self.pushButton_2.setText("DISCONNECT")  # Change button text here
            self.start_reading_thread()
        except Exception as e:
            self.textBrowser.append(f"❌ Failed to connect: {str(e)}")

    def disconnect_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.textBrowser.append("🔌 Disconnected from serial port.")
        self.pushButton_2.setText("CONNECT")
        self.pushButton_2.setEnabled(True)

    def start_reading_thread(self):
        self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.reading_thread.start()

    def read_serial_data(self):
        try:
            while self.serial_connection.is_open:
                line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if line and self.data_logging_enabled:
                    self.data_received.emit(line)
        except Exception as e:
            self.textBrowser.append(f"❌ Error reading data: {str(e)}")

    def update_text_browser(self, data):
        parts = data.split(',')
        if len(parts) == len(self.telemetry_fields):
            formatted = "<b>Telemetry Data:</b><br>"
            for field, value in zip(self.telemetry_fields, parts):
                formatted += f"<b>{field}:</b> {value}<br>"
            self.textBrowser.append(formatted)
        else:
            self.textBrowser.append(data)

    def refresh_ports(self):
        self.comboBox_2.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBox_2.addItem(port.device)

    def disable_data_logging(self):
        if self.radio_disable.isChecked():
            self.data_logging_enabled = False
            self.textBrowser.append("⛔ Data logging disabled.")

    def toggle_data_logging(self):
        if self.radio_log.isChecked():
            self.data_logging_enabled = True
            self.textBrowser.append("▶️ Data logging enabled.")
        elif self.radio_disable.isChecked():
            self.data_logging_enabled = False
            self.textBrowser.append("⛔ Data logging disabled.")
   
   
    def save_data(self):
        documents_folder = os.path.join(os.path.expanduser("~"), "Documents")
        csv_filename = os.path.join(documents_folder, "telemetry_data.csv")
        pdf_filename = os.path.join(documents_folder, "telemetry_data.pdf")

        try:
            pd.DataFrame(self.data_store).to_csv(csv_filename, index=False)
            self.convert_csv_to_pdf(csv_filename, pdf_filename)
            QMessageBox.information(self, "Success", f"Data saved to:\n{csv_filename}\n{pdf_filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")
            
    def convert_csv_to_pdf(self, csv_path, pdf_path):
        # Placeholder for PDF export logic
        with open(pdf_path, "w") as f:
            f.write("PDF conversion not yet implemented.\n")
            f.write(f"Would convert: {csv_path}")

def get_serial_ports():
    """Return a list of available serial port device names."""
    return [port.device for port in serial.tools.list_ports.comports()]

def open_serial(port, baudrate=9600, timeout=1):
    """Open and return a serial.Serial object."""
    return serial.Serial(port, baudrate, timeout=timeout)

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_GCA()
    ui.setupUi(MainWindow)
    MainWindow.setCentralWidget(ui.frame)
    MainWindow.show()
    sys.exit(app.exec_())