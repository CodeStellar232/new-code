import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal
import threading

class SerialManager(QObject):
    data_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.serial_connection = None
        self.reading_thread = None
        self.running = False
    

    def connect(self, port, baudrate):
        if self.serial_connection and self.serial_connection.is_open:
            self.disconnect()

        self.serial_connection = serial.Serial(port, baudrate, timeout=1)
        self.running = True
        self.start_reading_thread()

    def disconnect(self):
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def start_reading_thread(self):
        self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.reading_thread.start()

    def read_serial_data(self):
        try:
            while self.running and self.serial_connection.is_open:
                line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    self.on_data_received(line)
        except Exception as e:
            print(f"Serial Read Error: {str(e)}")

    # When data is received from serial port, emit the signal:
    def on_data_received(self, data):
        self.data_received.emit(data)

# Singleton instance
_serial_manager_instance = None

def get_serial_manager():
    global _serial_manager_instance
    if _serial_manager_instance is None:
        _serial_manager_instance = SerialManager()
    return _serial_manager_instance
