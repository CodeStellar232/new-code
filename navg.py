
from PyQt5 import QtCore, QtGui, QtWidgets
import serial.tools.list_ports
import warnings
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

from db import DbWindow as DashboardWidget
from cs import ConsoleWindow as ConsoleWidget
from gp import GraphsWindow as GraphWidget
from map2 import MapPage as MapWidget
#from trajectory import TrajectoryWidget  
from serial_port import SerialManager

warnings.filterwarnings("ignore", category=UserWarning)


class CustomSlideMenu(QtWidgets.QWidget):
    def __init__(self, parent=None, expanded_width=150, collapsed_width=60, animation_duration=300):
        super().__init__(parent)
        self.expanded_width = expanded_width
        self.collapsed_width = collapsed_width
        self.animation_duration = animation_duration

        self.setMinimumWidth(self.collapsed_width)
        self.setMaximumWidth(self.expanded_width)

        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.is_collapsed = True

    def toggle(self):
        if self.is_collapsed:
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
        else:
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)

        self.animation.start()
        self.is_collapsed = not self.is_collapsed


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Create a single SerialManager instance and pass it to pages
        self.serial_manager = SerialManager()

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 750)
        MainWindow.setMinimumSize(900, 600)

        MainWindow.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
        )

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("""
        *{
            border: none;
            background-color: transparent;
            color: #000;
        }
        #centralwidget{
            background-color: #78909C;
        }
        #side_menu{
            background-color: #eae8e0;
            border-radius: 20px;
        }
        QPushButton{
            padding: 10px;
            background-color: #ececdf;
            border-radius: 5px;
        }
        #main_body{
            background-color: rgb(220, 220, 220);
            border-radius: 10px;
        }
        QComboBox {
            background-color: white;
            color: black;
            border: 1px solid gray;
            border-radius: 5px;
            padding: 2px 5px;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: black;
            selection-background-color: #ececdf;
        }
        """)

        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(1, 1, 1, 1)
        self.mainLayout.setSpacing(0)

        # ---------------- HEADER ----------------
        self.headerLayout = QtWidgets.QHBoxLayout()
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.setSpacing(0)

        self.widget3 = QtWidgets.QWidget()
        self.widget3.setFixedWidth(60)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.widget3)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setSpacing(0)

        self.menuBtn = QtWidgets.QPushButton()
        self.menuBtn.setText("")
        icon5 = QtGui.QIcon("menu.png")
        self.menuBtn.setIcon(icon5)
        self.menuBtn.setIconSize(QtCore.QSize(30, 30))
        self.menuBtn.setCheckable(True)
        self.verticalLayout_8.addWidget(self.menuBtn)
        self.headerLayout.addWidget(self.widget3)
        self.headerLayout.addWidget(self.widget3)

        self.header = QtWidgets.QWidget()
        self.header.setMinimumHeight(90)
        self.header.setMaximumHeight(90)

        self.headerWidget = QtWidgets.QWidget(self.header)
        headerLayoutInner = QtWidgets.QHBoxLayout(self.headerWidget)
        headerLayoutInner.setContentsMargins(10, 10, 10, 10)

        self.groupBox_6 = QtWidgets.QGroupBox()
        groupBoxLayout = QtWidgets.QHBoxLayout(self.groupBox_6)

        self.groupBox = QtWidgets.QGroupBox("PORT_NAME")
        portLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.comboBox1 = QtWidgets.QComboBox()
        portLayout.addWidget(self.comboBox1)
        groupBoxLayout.addWidget(self.groupBox)

        self.refreshBtn = QtWidgets.QPushButton()
        
        self.refreshBtn.setIcon(QtGui.QIcon("refresh.png"))
        self.refreshBtn.setIconSize(QtCore.QSize(20, 20))
        self.refreshBtn.setFixedSize(30, 30)
        self.refreshBtn.setStyleSheet("QPushButton { padding: 2px; background-color: #ececdf; border-radius: 5px; }")
        self.refreshBtn.clicked.connect(self.refreshSerialPorts)
        groupBoxLayout.addWidget(self.refreshBtn)

        self.groupBox1 = QtWidgets.QGroupBox("BAUDRATE")
        baudLayout = QtWidgets.QVBoxLayout(self.groupBox1)
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItems(["9600", "115200", "250000"])
        baudLayout.addWidget(self.comboBox)
        groupBoxLayout.addWidget(self.groupBox1)

        self.groupBox_10 = QtWidgets.QGroupBox()
        gridLayout = QtWidgets.QGridLayout(self.groupBox_10)
        self.CONNECT = QtWidgets.QPushButton("CONNECT")
        self.CONNECT.setCheckable(True)
        self.CONNECT.setAutoExclusive(False)
        gridLayout.addWidget(self.CONNECT, 0, 0, 1, 1)
        groupBoxLayout.addWidget(self.groupBox_10)

        self.groupBox2 = QtWidgets.QGroupBox()
        loggingLayout = QtWidgets.QVBoxLayout(self.groupBox2)
        self.radioButton = QtWidgets.QRadioButton("LOGGING")
        self.radioButton_2 = QtWidgets.QRadioButton("DELOGGING")
        loggingLayout.addWidget(self.radioButton)
        loggingLayout.addWidget(self.radioButton_2)
        groupBoxLayout.addWidget(self.groupBox2)

        self.loggingGroup = QtWidgets.QButtonGroup(MainWindow)
        self.loggingGroup.addButton(self.radioButton)
        self.loggingGroup.addButton(self.radioButton_2)
        self.loggingGroup.setExclusive(True)

        headerLayoutInner.addWidget(self.groupBox_6)
        self.headerLayout.addWidget(self.headerWidget)
        self.mainLayout.addLayout(self.headerLayout)

        # ---------------- BODY ----------------
        self.bodyLayout = QtWidgets.QHBoxLayout()
        self.bodyLayout.setContentsMargins(5, 5, 5, 5)
        self.bodyLayout.setSpacing(2)
        self.side_menu = CustomSlideMenu()
        self.side_menu.setObjectName("side_menu")
        self.side_menu.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sideMenuLayout = self.side_menu.layout
        self.navButtonGroup = QtWidgets.QButtonGroup(MainWindow)
        self.navButtonGroup.setExclusive(True)

        # Navigation buttons
        def create_nav_button(text, icon_path):
            btn = QtWidgets.QPushButton(text)
            btn.setCheckable(True)
            icon = QtGui.QIcon(icon_path)
            btn.setIcon(icon)
            btn.setIconSize(QtCore.QSize(30, 30))
            sideMenuLayout.addWidget(btn)
            self.navButtonGroup.addButton(btn)
            return btn
        self.Db = create_nav_button("Dashboard", "dashboard.png")
        self.Db.setChecked(True)
        self.Cs = create_nav_button("Console", "web-programming.png")
        self.Gp = create_nav_button("Graphs", "graph1.png")
        self.map = create_nav_button("Map", "map1.png")
        self.trajectory = create_nav_button("Trajectory", "app-store.png")
        self.settings = QtWidgets.QPushButton("Settings")
        self.settings.setCheckable(True)
        sideMenuLayout.addWidget(self.settings)
        self.navButtonGroup.addButton(self.settings)
        self.bodyLayout.addWidget(self.side_menu)

        self.main_body = QtWidgets.QWidget()
        self.main_body.setObjectName("main_body")
        self.main_body.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_body_layout = QtWidgets.QVBoxLayout(self.main_body)
        self.main_body_layout.setContentsMargins(0, 0, 0, 0)
        self.main_body_layout.setSpacing(0)

        self.stackedWidget = QtWidgets.QStackedWidget(self.main_body)
        self.main_body_layout.addWidget(self.stackedWidget)

        self.bodyLayout.addWidget(self.main_body)
        self.mainLayout.addLayout(self.bodyLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

        # ---------------- PAGES ----------------
        self.dashboardPage = DashboardWidget(self.serial_manager)
        self.consolePage = ConsoleWidget(self.serial_manager)
        self.graphPage = GraphWidget(self.serial_manager)
        self.mapPage = MapWidget(self.serial_manager)
        #self.trajectoryPage = TrajectoryWidget(self.serial_manager, self.stackedWidget)

        self.stackedWidget.addWidget(self.dashboardPage)   # index 0
        self.stackedWidget.addWidget(self.consolePage)    # index 1
        self.stackedWidget.addWidget(self.graphPage)      # index 2
        self.stackedWidget.addWidget(self.mapPage)        # index 3
        #self.stackedWidget.addWidget(self.trajectoryPage) # index 4
        self.stackedWidget.setCurrentIndex(0)
        def on_nav_button_pressed(self, button):
          if button == self.Db:
           self.stackedWidget.setCurrentIndex(0)
          elif button == self.Cs:
           self.stackedWidget.setCurrentIndex(1)
          elif button == self.Gp:
           self.stackedWidget.setCurrentIndex(2)
          elif button == self.map:
            self.stackedWidget.setCurrentIndex(3)
          elif button == self.trajectory:
           self.stackedWidget.setCurrentIndex(4)
          

        # ---------------- SIGNALS ----------------
        self.menuBtn.toggled.connect(self.side_menu.toggle)
        self.navButtonGroup.buttonPressed.connect(self.on_nav_button_pressed)

        self.CONNECT.pressed.connect(self.handle_connect_toggle)
        self.loggingGroup.buttonPressed.connect(self.handle_logging_toggle)

        try:
            self.serial_manager.data_received.connect(self.log_data)
        except Exception:
            pass

        self.refreshSerialPorts()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "NAVIGATOR"))

    def on_nav_button_pressed(self, button):
        if button == self.Db:
            self.stackedWidget.setCurrentIndex(0)
        elif button == self.Cs:
            self.stackedWidget.setCurrentIndex(1)
        elif button == self.Gp:
            self.stackedWidget.setCurrentIndex(2)
        elif button == self.map:
            self.stackedWidget.setCurrentIndex(3)
        elif button == self.trajectory:
            self.stackedWidget.setCurrentIndex(4)
        

    def refreshSerialPorts(self):
        self.comboBox1.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if not ports:
            self.comboBox1.addItem("No device found")
        else:
            for port in ports:
                self.comboBox1.addItem(port)

    def handle_connect_toggle(self):
        if self.CONNECT.isChecked():
            port = self.comboBox1.currentText()
            try:
                baudrate = int(self.comboBox.currentText())
            except ValueError:
                QtWidgets.QMessageBox.critical(None, "Connection Error", "Invalid baudrate selected.")
                self.CONNECT.setChecked(False)
                return

            if "No device" in str(port):
                QtWidgets.QMessageBox.critical(None, "Connection Error", "No USB device detected!")
                self.CONNECT.setChecked(False)
                return
            try:
                self.serial_manager.connect(port, baudrate)
                self.CONNECT.setText("DISCONNECT")
                self.comboBox1.setEnabled(False)
                self.comboBox.setEnabled(False)
                print(f"✅ Connected to {port} at {baudrate}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Connection Error", f"Could not open port:\n{e}")
                self.CONNECT.setChecked(False)
        else:
            try:
                self.serial_manager.disconnect()
            except Exception:
                pass
            print("🔌 Disconnected")
            self.CONNECT.setText("CONNECT")
            self.comboBox1.setEnabled(True)
            self.comboBox.setEnabled(True)

    def handle_logging_toggle(self, button):
        try:
            if button.text() == "LOGGING":
                if hasattr(self.serial_manager, "set_logging_state"):
                    self.serial_manager.set_logging_state(True, False)
                else:
                    self.serial_manager.logging_enabled = True
                    self.serial_manager.delogging_enabled = False
                print("Logging enabled")
            elif button.text() == "DELOGGING":
                if hasattr(self.serial_manager, "set_logging_state"):
                    self.serial_manager.set_logging_state(False, True)
                else:
                    self.serial_manager.logging_enabled = False
                    self.serial_manager.delogging_enabled = True
                print("Delogging enabled")
        except Exception:
            pass

    def log_data(self, data):
        print(f"Received: {data}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
