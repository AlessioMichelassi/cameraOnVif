import math

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import numpy as np


class CustomDial(QDial):
    isDragging = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.isDragging = False
        self.setRange(0, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Disegna l'arco esterno
        rect = self.drawApertureArc(painter)
        # Calcola la posizione della maniglia
        angle = np.radians((self.value() / self.maximum()) * 270 - 135)
        handleRadius = rect.width() / 2
        cx = rect.center().x() + handleRadius * np.cos(angle)
        cy = rect.center().y() - handleRadius * np.sin(angle)
        self.drawHandle(painter, cx, cy)

    def drawApertureArc(self, painter):
        """
        Disegna l'arco esterno
        :param painter: il painter
        :param cx: centro x
        :param cy: centro y
        :param radius: raggio
        :return:
        """
        # Disegna l'arco
        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)
        startAngle = 215 * 16  # Inizia da 135 gradi (in sedicesimi di grado)
        spanAngle = -270 * 16  # Arco di 270 gradi
        color = QColor(70, 70, 70)
        painter.setPen(QPen(color, 6))
        painter.drawArc(rect, startAngle, spanAngle)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawArc(rect, startAngle, spanAngle)
        return rect

    def drawHandle(self, painter, cx, cy):
        """
        Disegna la maniglia
        :param painter: il painter
        :param cx: centro x
        :param cy: centro y
        :param radius: raggio
        :return:
        """
        # Disegna la maniglia
        handleRect = QRectF(cx - 8, cy - 8, 16, 16)
        painter.setBrush(Qt.GlobalColor.red)
        painter.drawEllipse(handleRect)

    def mousePressEvent(self, event):
        if self.isPointInHandle(event.pos()):
            self.isDragging = True
            self.setValueBasedOnMousePosition(event.pos())

    def mouseMoveEvent(self, event):
        if self.isDragging:
            self.setValueBasedOnMousePosition(event.pos())

    def mouseReleaseEvent(self, event):
        self.isDragging = False

    def isPointInHandle(self, point):
        # Verifica se il punto del mouse è all'interno del cursore (knob)
        # Implementa qui la logica di controllo
        return True

    def setValueBasedOnMousePosition(self, pos):
        # Calcola l'angolo tra la posizione del mouse e l'asse orizzontale
        center = QPointF(self.width() / 2, self.height() / 2)
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        angle = np.arctan2(dy, dx)

        # Converti l'angolo in un valore del dial
        # Assicurati che l'angolo e la conversione siano corretti per il tuo dial
        dialAngle = np.degrees(angle) - 135
        if dialAngle < 0:
            dialAngle += 360
        value = int((dialAngle / 270) * self.maximum())
        self.setValue(value)
# test widget
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dial = CustomDial()
    dial.show()
    sys.exit(app.exec())
