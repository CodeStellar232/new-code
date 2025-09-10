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

    @staticmethod
    def scan_usb_devices():
        """
        Scan all connected USB serial devices.
        """
        for port in serial.tools.list_ports.comports():
            print(f"🔎 {port.device} - {port.description}")

    def connect(self, port, baudrate=115200):
        """Connect to the given serial port."""
        if self.serial_connection and self.serial_connection.is_open:
            self.disconnect()

        self.serial_connection = serial.Serial(port, baudrate, timeout=1)
        self.running = True
        self.start_reading_thread()
        print(f"✅ Connected to {port} at {baudrate} baud")

    def disconnect(self):
        """Disconnect from the serial port."""
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("🔌 Disconnected")

    def start_reading_thread(self):
        """Start a background thread to read serial data."""
        self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.reading_thread.start()

    def read_serial_data(self):
        """Continuously read serial data and log everything."""
        try:
            while self.running and self.serial_connection.is_open:
                raw = self.serial_connection.readline()
                if raw:
                    print(f"RAW BYTES: {raw}")  
                    try:
                        line = raw.decode("utf-8", errors="ignore").strip()
                        print(f"DECODED: {line}")  
                        if line:
                            self.on_data_received(line)
                    except Exception as e:
                        print(f"⚠️ Decode Error: {e}, Raw={raw}")
                else:
                    print("... no data received ...") 
        except Exception as e:
            print(f"Serial Read Error: {str(e)}")

    def on_data_received(self, data):
        
        self.data_received.emit(data)


# Singleton instance
_serial_manager_instance = None

def get_serial_manager():
    global _serial_manager_instance
    if _serial_manager_instance is None:
        _serial_manager_instance = SerialManager()
    return _serial_manager_instance
