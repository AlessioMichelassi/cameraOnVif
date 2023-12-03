import sys

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QSlider, QLabel, QPushButton, QDial)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class PTZControlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Layout principale
        mainLayout = QVBoxLayout(self)

        # Pan and Tilt dials
        panDial = self.createDial("Pan")
        tiltDial = self.createDial("Tilt")

        # Zoom controls
        zoomInButton = QPushButton(QIcon("zoom-in-icon.png"), "")
        zoomOutButton = QPushButton(QIcon("zoom-out-icon.png"), "")
        zoomSlider = QSlider(Qt.Orientation.Vertical)

        # Posiziona i controlli nel layout
        topLayout = QHBoxLayout()
        topLayout.addWidget(tiltDial)

        centerLayout = QHBoxLayout()
        centerLayout.addWidget(zoomOutButton)
        centerLayout.addWidget(zoomSlider)
        centerLayout.addWidget(zoomInButton)

        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(panDial)

        # Aggiungi i layout al layout principale
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(centerLayout)
        mainLayout.addLayout(bottomLayout)

    def createDial(self, label):
        dial = QDial()
        dial.setNotchesVisible(True)
        dialLayout = QVBoxLayout()
        dialLayout.addWidget(QLabel(label))
        dialLayout.addWidget(dial)
        dialContainer = QWidget()
        dialContainer.setLayout(dialLayout)
        return dialContainer


# Test del widget
if __name__ == '__main__':
    app = QApplication([])
    ptzControl = PTZControlWidget()
    ptzControl.show()
    sys.exit(app.exec())
