from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys
import math


class CustomDial(QDial):
    outerColor = {
        "borderColor": QColor(75, 70, 70),
        "borderWidth": 2,
        "BackColor": QColor(70, 70, 70),
    }
    innerColor = {
        "borderColor": QColor(0, 0, 0),
        "borderWidth": 1,
        "BackColor": QColor(255, 100, 100),
    }
    notchColor = {
        "color": QColor(255, 255, 255),
        "textColor": QColor(255, 255, 255),
    }

    notchLength = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.notchCount = 10  # Numero di notch
        self.outerDiameter = 20
        self.innerDiameter = self.outerDiameter // 4

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bgColor = self.outerColor["BackColor"].darker(150)
        painter.setBackground(bgColor)
        cx = self.width() / 2
        cy = self.height() / 2
        radius = min(cx, cy) - 1

        self.drawOuterKnob(painter, cx, cy, radius)
        self.drawApertureArc(painter)
        self.drawDiaphragm(painter, cx, cy, radius // 2)
        self.drawNotches(painter, cx, cy, radius)
        angle = (self.value() / self.maximum()) * 2 * math.pi
        innerCx = cx + radius * math.cos(angle)
        innerCy = cy - radius * math.sin(angle)

        self.drawInnerKnob(painter, innerCx, innerCy, self.innerDiameter)

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

    def drawInnerKnob(self, painter, cx, cy, radius):
        """
        Disegna il cerchio interno o Knob del dial
        :param painter: il painter
        :param cx: centro x
        :param cy: centro y
        :param radius: raggio
        :return:
        """
        pen = QPen(self.innerColor["borderColor"], self.innerColor["borderWidth"])
        painter.setPen(pen)
        painter.setBrush(self.innerColor["BackColor"])
        rectF = QRectF(cx - radius, cy - radius, 2 * radius, 2 * radius)
        painter.drawEllipse(rectF)

    def drawOuterKnob(self, painter, cx, cy, radius):
        """
        Disegna il cerchio esterno del dial
        :param painter: il painter
        :param cx:  centro x
        :param cy:  centro y
        :param radius: raggio
        :return:
        """
        pen = QPen(self.outerColor["borderColor"], self.outerColor["borderWidth"])
        painter.setPen(pen)
        painter.setBrush(self.outerColor["BackColor"])

        rectF = QRectF(cx - radius, cy - radius, 2 * radius, 2 * radius)
        painter.drawEllipse(rectF)

    def drawNotches(self, painter, cx, cy, radius):
        radius = radius + 10
        pen = QPen(self.notchColor["color"], 1)
        painter.setPen(pen)
        for i in range(self.notchCount):
            angle = i * (360 / self.notchCount)
            radian = math.radians(angle)
            x = int(cx + (radius - 10) * math.cos(radian))
            y = int(cy - (radius - 10) * math.sin(radian))
            # la lunghezza del notch è in self.notchLength
            # trova la posizione in base a cx e cy
            nCx = cx + (radius - 2) * math.cos(radian)
            nCy = cy - (radius - 2) * math.sin(radian)
            nCx = int(nCx)
            nCy = int(nCy)
            painter.drawLine(x, y, nCx, nCy)

    def drawDiaphragm(self, painter, cx, cy, max_radius):
        # Il raggio del diaframma diminuisce all'aumentare del valore
        aperture = (1 - (self.value() / self.maximum())) * max_radius
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.GlobalColor.black)

        # Disegna il diaframma
        painter.drawEllipse(QPointF(cx, cy), aperture, aperture)

    def mousePressEvent(self, event):
        self.updateDialValue(event.pos())

    def mouseMoveEvent(self, event):
        self.updateDialValue(event.pos())

    def mouseReleaseEvent(self, event):
        self.updateDialValue(event.pos())

    def updateDialValue(self, pos):
        cx = self.width() / 2
        cy = self.height() / 2
        angle = math.atan2(cy - pos.y(), pos.x() - cx)
        if angle < 0:
            angle += 2 * math.pi

        # Converti l'angolo in un valore di dial
        minVal, maxVal = self.minimum(), self.maximum()
        rangeVal = maxVal - minVal
        value = (angle / (2 * math.pi)) * rangeVal + minVal
        self.setValue(int(value))
        self.repaint()  # Aggiorna il disegno del dial


# Test del CustomDial
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWidget = QWidget()
    layout = QVBoxLayout(mainWidget)

    dial = CustomDial()
    layout.addWidget(dial)

    mainWidget.show()
    sys.exit(app.exec())
