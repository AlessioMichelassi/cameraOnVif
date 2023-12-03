import math
import sys

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class PTZPanTiltWidget(QWidget):
    isDragging = False
    center = QPoint(0, 0)
    lastPoint = QPoint(0, 0)
    moveSignal = pyqtSignal(float, float)
    stopSignal = pyqtSignal()

    colors = {
        'background': QColor(40, 40, 40),
        'line': QColor(155, 45, 140, 80),
        'center': QColor(55, 55, 55, 80),
        'lineDragging': QColor(255, 0, 0),
        'centerDragging': QColor(155, 100, 0),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setFixedSize(200, 200)
        self.center = QPoint(int(self.width() / 2), int(self.height() / 2))
        self.lastPoint = self.center
        self.setMouseTracking(True)  # Abilita il tracking del mouse senza bisogno di cliccare

    def paintEvent(self, a0, _QPaintEvent=None):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bgColor = self.colors['background']
        painter.fillRect(self.rect(), bgColor)  # Sfondo del widget

        # Disegna gli assi
        lnColor = self.colors['line']
        painter.setPen(QPen(lnColor, 1))
        painter.drawLine(0, self.center.y(), self.width(), self.center.y())  # Linea orizzontale
        painter.drawLine(self.center.x(), 0, self.center.x(), self.height())  # Linea verticale

        for scale, color in zip([0.2, 0.5, 1], ['center', 'line', 'lineDragging']):
            painter.setPen(QPen(self.colors["line"], 1))
            radius = int(self.width() / 2 * scale)
            painter.drawEllipse(self.center, radius, radius)

        if self.isDragging:
            drLine = self.colors['lineDragging']
            # Disegna la linea di movimento PTZ
            painter.setPen(QPen(drLine, 2, Qt.PenStyle.SolidLine))
            painter.drawLine(self.center, self.lastPoint)  # Linea dal centro al punto di movimento

    def mousePressEvent(self, event, _QMouseEvent=None):
        self.isDragging = True
        self.lastPoint = event.pos()
        self.updatePanTiltSpeed()
        self.update()

    def mouseMoveEvent(self, event, _QMouseEvent=None):
        self.lastPoint = event.pos()
        if self.isDragging:
            self.updatePanTiltSpeed()
        self.update()

    def mouseReleaseEvent(self, event, _QMouseEvent=None):
        self.lastPoint = self.center
        self.updatePanTiltSpeed()
        self.isDragging = False
        self.stopSignal.emit()
        self.update()

    def updatePanTiltSpeed(self):
        # Calcola le velocità di pan/tilt in base alla distanza e angolo dal centro
        dx = self.lastPoint.x() - self.center.x()
        dy = self.lastPoint.y() - self.center.y()
        distance = math.hypot(dx, dy)
        max_distance = math.hypot(self.width() / 2, self.height() / 2)
        speed_scale = distance / max_distance  # Velocità normalizzata da 0 a 1

        # Calcola la direzione separata per pan e tilt
        pan_speed = speed_scale if dx > 0 else -speed_scale
        tilt_speed = speed_scale if dy > 0 else -speed_scale

        # Emette i segnali con i valori separati per pan e tilt
        self.moveSignal.emit(pan_speed, tilt_speed)


# Test del PTZPanTiltWidget
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWidget = QWidget()
    layout = QVBoxLayout(mainWidget)

    ptzControl = PTZPanTiltWidget()
    layout.addWidget(ptzControl)
    ptzControl.moveSignal.connect(lambda x, y: print(f"Pan: {x}, Tilt: {y}"))
    mainWidget.show()
    sys.exit(app.exec())
