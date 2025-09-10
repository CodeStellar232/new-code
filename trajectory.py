# trajectory3d.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QColor, QVector3D, QQuaternion
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import Qt3DWindow, QOrbitCameraController, QPhongMaterial, QCuboidMesh
from PyQt5.Qt3DRender import QDirectionalLight
import os
import re


class InfoPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.coord_label = QLabel("Coordinates:\nX: 0.00\nY: 0.00\nZ: 0.00")
        self.rpy_label = QLabel("Orientation:\nRoll: 0°\nPitch: 0°\nYaw: 0°")

        layout.addWidget(QLabel("<b>Object Info</b>"))
        layout.addSpacing(10)
        layout.addWidget(self.coord_label)
        layout.addSpacing(10)
        layout.addWidget(self.rpy_label)
        layout.addStretch()

        self.back_button = QPushButton("Back")
        layout.addWidget(self.back_button)

    def update_info(self, pos: QVector3D, rotation: QVector3D):
        self.coord_label.setText(
            f"Coordinates:\nX: {pos.x():.2f}\nY: {pos.y():.2f}\nZ: {pos.z():.2f}"
        )
        self.rpy_label.setText(
            f"Orientation:\nRoll: {rotation.x():.0f}°\nPitch: {rotation.y():.0f}°\nYaw: {rotation.z():.0f}°"
        )


class TrajectoryWidget(QWidget):
    def __init__(self, serial_manager, parent=None):
        super().__init__(parent)
        self.serial_manager = serial_manager
        #self.stacked_widget = stacked_widget

        self.current_position = QVector3D(0, 1, 0)
        self.current_rotation = QVector3D(0, 0, 0)

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.info_panel = InfoPanel()
        self.main_layout.addWidget(self.info_panel)

        self.view = Qt3DWindow()
        self.container = self.createWindowContainer(self.view, parent=self)
        self.container.setMinimumSize(800, 600)
        self.container.setFocusPolicy(Qt.NoFocus)
        self.main_layout.addWidget(self.container)

        self.root_entity = QEntity()
        self._setup_camera()
        self._setup_grid()
        self._load_cube()
        self.view.setRootEntity(self.root_entity)

        # connect serial manager
        self.serial_manager.data_received.connect(self.on_serial_data)
    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)

    def _load_cube(self):
        self.model_entity = QEntity(self.root_entity)

        mesh = QCuboidMesh()
        mesh.setXExtent(1)
        mesh.setYExtent(2)
        mesh.setZExtent(1)

        material = QPhongMaterial()
        material.setDiffuse(QColor(200, 100, 200))

        self.transform = QTransform()
        self.transform.setTranslation(self.current_position)
        self.transform.setRotation(QQuaternion.fromEulerAngles(
            self.current_rotation.x(), self.current_rotation.y(), self.current_rotation.z()
        ))

        self.model_entity.addComponent(mesh)
        self.model_entity.addComponent(material)
        self.model_entity.addComponent(self.transform)

        # light
        light_entity = QEntity(self.root_entity)
        light = QDirectionalLight(light_entity)
        light.setColor(QColor(255, 255, 255))
        light.setIntensity(0.9)
        light_transform = QTransform()
        light_transform.setTranslation(QVector3D(10, 10, 10))
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
        # Just a flat plane grid at Y=0
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

    def on_serial_data(self, data: str):
        """
        Example expected format:
        LAT:12.3,LON:45.6,ALT:100,ROLL:10,PITCH:5,YAW:180
        or
        X:1.2,Y:2.5,Z:3.7,ROLL:15,PITCH:25,YAW:5
        """
        
            # Normalize
        parts = re.split(r'[,:]', data)
        kv = dict(zip(parts[::2], parts[1::2]))

            # position (fallback to current if missing)
        x = float(kv.get("X", self.current_position.x()))
        y = float(kv.get("Y", self.current_position.y()))
        z = float(kv.get("Z", self.current_position.z()))
        self.current_position = QVector3D(x, y, z)

            # rotation
        roll = float(kv.get("ROLL", self.current_rotation.x()))
        pitch = float(kv.get("PITCH", self.current_rotation.y()))
        yaw = float(kv.get("YAW", self.current_rotation.z()))
        self.current_rotation = QVector3D(roll, pitch, yaw)

            # update transform
        self.transform.setTranslation(self.current_position)
        self.transform.setRotation(QQuaternion.fromEulerAngles(roll, pitch, yaw))

            # update info panel
        self.info_panel.update_info(self.current_position, self.current_rotation)

        
