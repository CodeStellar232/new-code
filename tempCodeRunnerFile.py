from PyQt5 import QtCore, QtGui, QtWidgets
import serial.tools.list_ports
import warnings
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from serial_port import serial_manager as serial_port

# Import your integrated pages
from db import DbWindow as DashboardWidget
from cs import ConsoleWindow as ConsoleWidget
from gp import GraphsWindow as GraphWidget
from map import MapPage as MapWidget
from trajectory import TrajectoryPage as TrajectoryWidget

warnings.filterwarnings("ignore", category=UserWarning)


# ✅ Custom Slide Menu class 
class CustomSlideMenu(QtWidgets.QWidget):
    def __init__(self, parent=None, expanded_width=150, collapsed_width=60, animation_duration=300):
        super().__init__(parent)
        self.expanded_width = expanded_width
        self.collapsed_width = collapsed_width
        self.animation_duration = animation_duration

        self.setMinimumWidth(self.collapsed_width)
        self.setMaximumWidth(self.expanded_width)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)  # 🔒 Prevent horizontal expansion

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
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
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
        self.centralwidget.setObjectName("centralwidget")

        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # Header layout
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
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("C:/.../menu.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuBtn.setIcon(icon5)
        self.menuBtn.setIconSize(QtCore.QSize(30, 30))
        self.menuBtn.setCheckable(True)
        self.verticalLayout_8.addWidget(self.menuBtn)

        self.headerLayout.addWidget(self.widget3)

        self.header = QtWidgets.QWidget()
        self.header.setMinimumHeight(90)
        self.header.setMaximumHeight(90)
        self.header.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)  # 🔒 Prevent vertical expansion

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
        self.refreshBtn.setIcon(QtGui.QIcon("C:/.../refresh.png"))
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
        self.CONNECT.setAutoExclusive(True)
        gridLayout.addWidget(self.CONNECT, 0, 0, 1, 1)
        groupBoxLayout.addWidget(self.groupBox_10)

        self.groupBox2 = QtWidgets.QGroupBox()
        loggingLayout = QtWidgets.QVBoxLayout(self.groupBox2)
        self.radioButton = QtWidgets.QRadioButton("LOGGING")
        self.radioButton_2 = QtWidgets.QRadioButton("DELOGGING")
        loggingLayout.addWidget(self.radioButton)
        loggingLayout.addWidget(self.radioButton_2)
        groupBoxLayout.addWidget(self.groupBox2)

        headerLayoutInner.addWidget(self.groupBox_6)
        self.headerLayout.addWidget(self.headerWidget)
        self.mainLayout.addLayout(self.headerLayout)

        # Body Layout
        self.bodyLayout = QtWidgets.QHBoxLayout()
        self.bodyLayout.setContentsMargins(1, 1, 1, 1)
        self.bodyLayout.setSpacing(0)

        self.side_menu = CustomSlideMenu()
        self.side_menu.setObjectName("side_menu")
        self.side_menu.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)  # 🔒 Patch already applied inside CustomSlideMenu too

        sideMenuLayout = self.side_menu.layout

        # Side Menu Buttons
        self.Db = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("C:/.../dashboard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Db.setIcon(icon)
        self.Db.setIconSize(QtCore.QSize(30, 30))
        self.Db.setCheckable(True)
        self.Db.setAutoExclusive(True)
        sideMenuLayout.addWidget(self.Db)

        self.Cs = QtWidgets.QPushButton()
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("C:/.../web-programming.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Cs.setIcon(icon1)
        self.Cs.setIconSize(QtCore.QSize(30, 30))
        self.Cs.setCheckable(True)
        self.Cs.setAutoExclusive(True)
        sideMenuLayout.addWidget(self.Cs)

        self.Gp = QtWidgets.QPushButton()
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("C:/.../graph1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Gp.setIcon(icon2)
        self.Gp.setIconSize(QtCore.QSize(30, 30))
        self.Gp.setCheckable(True)
        self.Gp.setAutoExclusive(True)
        sideMenuLayout.addWidget(self.Gp)

        self.map = QtWidgets.QPushButton()
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("C:/.../map1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.map.setIcon(icon3)
        self.map.setIconSize(QtCore.QSize(30, 30))
        self.map.setCheckable(True)
        self.map.setAutoExclusive(True)
        sideMenuLayout.addWidget(self.map)

        self.trajectory = QtWidgets.QPushButton()
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("C:/.../app-store.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.trajectory.setIcon(icon4)
        self.trajectory.setIconSize(QtCore.QSize(30, 30))
        self.trajectory.setCheckable(True)
        self.trajectory.setAutoExclusive(True)
        sideMenuLayout.addWidget(self.trajectory)

        self.settings = QtWidgets.QPushButton("Settings")
        self.settings.setCheckable(True)
        self.settings.setAutoExclusive(True)
        sideMenuLayout.addWidget(self.settings)

        self.bodyLayout.addWidget(self.side_menu)

        self.main_body = QtWidgets.QWidget()
        self.main_body.setObjectName("main_body")
        self.main_body.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_body_layout = QtWidgets.QVBoxLayout(self.main_body)
        self.main_body_layout.setContentsMargins(0, 0, 0, 0)
        self.main_body_layout.setSpacing(0)

        self.stackedWidget = QtWidgets.QStackedWidget(self.main_body)
        self.stackedWidget.setObjectName("stackedWidget")
        self.main_body_layout.addWidget(self.stackedWidget)

        self.refreshSerialPorts()

        self.bodyLayout.addWidget(self.main_body)
        self.mainLayout.addLayout(self.bodyLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        # Load Integrated Pages
        self.dashboardPage = DashboardWidget()
        self.consolePage = ConsoleWidget()
        self.graphPage = GraphWidget()
        self.mapPage = MapWidget()
        self.trajectoryPage = TrajectoryWidget()

        self.stackedWidget.addWidget(self.dashboardPage)
        self.stackedWidget.addWidget(self.consolePage)
        self.stackedWidget.addWidget(self.graphPage)
        self.stackedWidget.addWidget(self.mapPage)
        self.stackedWidget.addWidget(self.trajectoryPage)

        self.stackedWidget.setCurrentIndex(0)

        self.menuBtn.toggled.connect(self.side_menu.toggle)
        self.Db.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.Cs.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.Gp.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.map.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.trajectory.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4))

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.CONNECT.clicked.connect(self.handle_connect_toggle)

        self.logging_enabled = False
        self.radioButton.toggled.connect(self.handle_logging_toggle)
        self.radioButton_2.toggled.connect(self.handle_logging_toggle)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def refreshSerialPorts(self):
        self.comboBox1.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBox1.addItem(port.device)

    def handle_connect_toggle(self):
        if self.CONNECT.isChecked():
            port = self.comboBox1.currentText()
            baudrate = int(self.comboBox.currentText())
            try:
                serial_port.open_port(port, baudrate)
                self.CONNECT.setText("DISCONNECT")
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Connection Error", f"Could not open port:\n{e}")
                self.CONNECT.setChecked(False)
        else:
            serial_port.close_port()
            self.CONNECT.setText("CONNECT")

    def handle_logging_toggle(self):
        self.logging_enabled = self.radioButton.isChecked()

    def log_data(self, data):
        if self.logging_enabled:
            print(f"Logging data: {data}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
