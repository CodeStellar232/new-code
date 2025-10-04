# trajectory3d.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QVector3D, QQuaternion
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import QPhongMaterial, QCuboidMesh, QOrbitCameraController, Qt3DWindow
from PyQt5.Qt3DRender import QDirectionalLight
import re


class InfoPanel(QFrame):
    """Side panel to display position and orientation info"""
    def __init__(self, serial_manager=None, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager
        self.setFixedWidth(250)
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("<b>Object Info</b>"))
        layout.addSpacing(10)

        self.coord_label = QLabel("Coordinates:\nX: 0.00\nY: 0.00\nZ: 0.00")
        self.rpy_label = QLabel("Orientation:\nRoll: 0°\nPitch: 0°\nYaw: 0°")

        layout.addWidget(self.coord_label)
        layout.addSpacing(10)
        layout.addWidget(self.rpy_label)
        layout.addStretch()

    def update_info(self, pos: QVector3D, rotation: QVector3D):
        self.coord_label.setText(
            f"Coordinates:\nX: {pos.x():.2f}\nY: {pos.y():.2f}\nZ: {pos.z():.2f}"
        )
        self.rpy_label.setText(
            f"Orientation:\nRoll: {rotation.x():.0f}°\nPitch: {rotation.y():.0f}°\nYaw: {rotation.z():.0f}°"
        )


class TrajectoryWidget(QWidget):
    """3D Trajectory Viewer embedded safely in QWidget"""
    def __init__(self, serial_manager=None, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager

        self.current_position = QVector3D(0, 1, 0)
        self.current_rotation = QVector3D(0, 0, 0)

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        # Info panel
        self.info_panel = InfoPanel()
        self.main_layout.addWidget(self.info_panel)

        # Create Qt3DWindow and wrap in QWidget container
        self.view = Qt3DWindow()
        self.view.defaultFrameGraph().setClearColor(QColor(50, 50, 50))
        self.container = QWidget.createWindowContainer(self.view)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.container)

        # Root entity
        self.root_entity = QEntity()
        self.view.setRootEntity(self.root_entity)

        # Setup scene
        self._setup_camera()
        self._setup_grid()
        self._load_cube()

        # Serial updates scheduled safely
        
        self.serial_manager.data_received.connect(self.schedule_update)

    def _load_cube(self):
        """Load a cube representing the object"""
        self.model_entity = QEntity(self.root_entity)

        mesh = QCuboidMesh()
        mesh.setXExtent(1)
        mesh.setYExtent(2)
        mesh.setZExtent(1)

        material = QPhongMaterial()
        material.setDiffuse(QColor(100, 200, 255))

        self.transform = QTransform()
        self.transform.setTranslation(self.current_position)
        self.transform.setRotation(QQuaternion.fromEulerAngles(
            self.current_rotation.x(), self.current_rotation.y(), self.current_rotation.z()
        ))

        self.model_entity.addComponent(mesh)
        self.model_entity.addComponent(material)
        self.model_entity.addComponent(self.transform)

        # Directional light
        light_entity = QEntity(self.root_entity)
        light = QDirectionalLight(light_entity)
        light.setColor(QColor(255, 255, 255))
        light.setIntensity(1.0)
        light_transform = QTransform()
        light_transform.setTranslation(QVector3D(10, 20, 10))
        light_entity.addComponent(light)
        light_entity.addComponent(light_transform)

    def _setup_camera(self):
        camera = self.view.camera()
        camera.lens().setPerspectiveProjection(45.0, 16 / 9, 0.1, 1000.0)
        camera.setPosition(QVector3D(0, 8, 20))
        camera.setViewCenter(QVector3D(0, 0, 0))

        cam_controller = QOrbitCameraController(self.root_entity)
        cam_controller.setLinearSpeed(50)
        cam_controller.setLookSpeed(180)
        cam_controller.setCamera(camera)

    def _setup_grid(self):
        for axis in range(-10, 11):
            if axis == 0:
                continue

            # X lines
            line_x = QEntity(self.root_entity)
            mesh_x = QCuboidMesh()
            mesh_x.setXExtent(0.02)
            mesh_x.setYExtent(0.02)
            mesh_x.setZExtent(20.0)
            transform_x = QTransform()
            transform_x.setTranslation(QVector3D(axis, 0, 0))
            mat_x = QPhongMaterial()
            mat_x.setDiffuse(QColor(180, 180, 180))
            line_x.addComponent(mesh_x)
            line_x.addComponent(mat_x)
            line_x.addComponent(transform_x)

            # Z lines
            line_z = QEntity(self.root_entity)
            mesh_z = QCuboidMesh()
            mesh_z.setXExtent(20.0)
            mesh_z.setYExtent(0.02)
            mesh_z.setZExtent(0.02)
            transform_z = QTransform()
            transform_z.setTranslation(QVector3D(0, 0, axis))
            mat_z = QPhongMaterial()
            mat_z.setDiffuse(QColor(180, 180, 180))
            line_z.addComponent(mesh_z)
            line_z.addComponent(mat_z)
            line_z.addComponent(transform_z)

    def schedule_update(self, data: str):
        """Schedule the update safely to avoid blocking the main UI thread"""
        QTimer.singleShot(0, lambda: self.on_serial_data(data))

    def on_serial_data(self, data: str):
        """Update position and rotation from serial data"""
        try:
            parts = re.split(r'[,:]', data)
            kv = dict(zip(parts[::2], parts[1::2]))

            x = float(kv.get("X", self.current_position.x()))
            y = float(kv.get("Y", self.current_position.y()))
            z = float(kv.get("Z", self.current_position.z()))
            roll = float(kv.get("ROLL", self.current_rotation.x()))
            pitch = float(kv.get("PITCH", self.current_rotation.y()))
            yaw = float(kv.get("YAW", self.current_rotation.z()))
        except (ValueError, IndexError):
            return  

        self.current_position = QVector3D(x, y, z)
        self.current_rotation = QVector3D(roll, pitch, yaw)

        self.transform.setTranslation(self.current_position)
        self.transform.setRotation(QQuaternion.fromEulerAngles(roll, pitch, yaw))

        self.info_panel.update_info(self.current_position, self.current_rotation)
