# serial_manager.py

from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import serial
import serial.tools.list_ports


class SerialReaderWorker(QObject):
    data_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, ser):
        super().__init__()
        self.ser = ser
        self.running = True

    @pyqtSlot()
    def read_loop(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode(errors='ignore').strip()
                if line:
                    self.data_received.emit(line)
            except Exception as e:
                print("❌ Read error:", e)
        self.finished.emit()

    def stop(self):
        self.running = False


class SerialPortManager(QObject):
    data_received = pyqtSignal(str)       # Signal with serial data
    connected = pyqtSignal()              # Signal when port connects
    disconnected = pyqtSignal()           # Signal when port disconnects

    def __init__(self):
        super().__init__()
        self.ser = None
        self.thread = None
        self.worker = None

    def open_port(self, port_name, baud_rate):
        self.close_port()  # Always clean up before opening a new one

        try:
            self.ser = serial.Serial(port_name, baud_rate, timeout=1)
            self.worker = SerialReaderWorker(self.ser)
            self.thread = QThread()

            self.worker.moveToThread(self.thread)

            # Signal-slot wiring
            self.thread.started.connect(self.worker.read_loop)
            self.worker.data_received.connect(self.data_received.emit)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()
            self.connected.emit()
            print(f"✅ Port {port_name} opened at {baud_rate} baud.")
        except Exception as e:
            print(f"❌ Error opening port {port_name}: {e}")

    def close_port(self):
        if self.worker:
            self.worker.stop()

        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                print(f" Port closed.")
            except Exception as e:
                print(f"⚠️ Error closing port: {e}")

        self.worker = None
        self.ser = None
        self.thread = None
        self.disconnected.emit()


# ✅ Global instance (singleton-style)
serial_manager = SerialPortManager()


# ✅ Utility to list available ports
def get_available_ports():
    return [port.device for port in serial.tools.list_ports.comports()]
