import math

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys


class DialAperture(QGraphicsView):
    dialColor = {
        "borderColor": QColor(75, 70, 70),
        "borderWidth": 2,
        "BackColor": QColor(70, 70, 70),
    }
    knobColor = {
        "borderColor": QColor(0, 0, 0),
        "borderWidth": 1,
        "BackColor": QColor(255, 100, 100),
    }
    dialSize = 100
    knobSize = 20
    isDragging = False
    aperture: QGraphicsEllipseItem
    knob: QGraphicsEllipseItem
    dial: QGraphicsEllipseItem

    lblOpen: QLabel
    lblClose: QLabel
    lblFStop: QLabel

    minValue = 0
    maxValue = 10
    value = 0

    valueChangedSignal = pyqtSignal(str)
    errorSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.apertureValues = ["Open", "F1.8", "F2", "F2.8", "F4", "F5.6", "F8", "F11", "F16", "Close"]
        self.apertureValues.reverse()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(QColor(40, 40, 40))
        self.initUI()
        self.setFixedSize(int(self.dialSize * 1.5), int(self.dialSize * 1.5))
        self.irisToAngleMapping = self.createIrisToAngleMapping()

    def initUI(self):
        self.lblFStop = QLabel()
        self.lblOpen = QLabel()
        self.lblClose = QLabel()
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.dial = self.drawDial()

        self.aperture = self.drawAperture()
        self.knob = self.drawKnob()
        self.knob.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        self.scene.addItem(self.dial)
        self.scene.addItem(self.knob)
        self.scene.addItem(self.aperture)
        # posiziona Aperture al centro del dial
        self.aperture.setPos((self.dialSize - self.aperture.boundingRect().width()) / 2,
                             (self.dialSize - self.aperture.boundingRect().height()) / 2)
        # posiziona Knob all'inizio della path di Aperture
        self.knob.setPos(self.aperture.pos().x() - self.knob.boundingRect().width() / 2,
                         self.aperture.pos().y() - self.knob.boundingRect().height() / 2)
        self.scene.update()
        self.updateKnobPosition(self.knob.pos())
        self.drawLabel()

    def drawDial(self):
        # Crea un gradiente radiale per la sfumatura
        gradient = QRadialGradient(0, 0, 100)
        gradient.setColorAt(0, QColor(80, 80, 80))  # Colore al centro
        gradient.setColorAt(1, QColor(50, 50, 50))  # Colore ai bordi

        # Crea il dial e applica il gradiente
        dial = QGraphicsEllipseItem(QRectF(0, 0, self.dialSize, self.dialSize))
        dial.setPen(QPen(QColor(70, 70, 70), 2))  # Colore e spessore del bordo
        dial.setBrush(QBrush(gradient))  # Applica il gradiente come pennello
        return dial

    def drawKnob(self):
        # Crea un gradiente radiale per la sfumatura
        fgColor = self.knobColor["BackColor"]
        bgColor = fgColor.darker(150)
        gradient = QRadialGradient(0, 0, 100)
        gradient.setColorAt(0, fgColor)
        gradient.setColorAt(1, bgColor)

        knob = QGraphicsEllipseItem(QRectF(0, 0, self.knobSize, self.knobSize))
        knob.setPen(QPen(QColor(0, 0, 0), 1))
        knob.setBrush(QBrush(gradient))
        return knob

    def drawAperture(self):
        # Disegna un cerchio più piccolo di 10 rispetto al dial
        aperture = QGraphicsEllipseItem(QRectF(0, 0, self.dialSize - 20, self.dialSize - 20))
        color = QColor(100, 100, 100)
        aperture.setPen(QPen(color, 1))
        aperture.setBrush(QBrush(color))
        return aperture

    def drawLabel(self):
        self.lblOpen = self.drawText("Open", QPoint(100, 80))
        self.lblClose = self.drawText("Close", QPoint(12, 120))
        CX = int(self.scene.width() / 2)
        CY = int(self.scene.height() / 2)
        self.lblFStop = self.drawText("F1.8", QPoint(CX, CY))

    def drawText(self, name, position=QPoint()):
        # Disegna il testo
        labelText = QLabel(name, self)
        labelText.setFont(QFont("Arial", 12))
        labelText.setStyleSheet("color: rgb(255,200,50);")

        return self.positionLabel(labelText, position)

    def positionLabel(self, labelText, pos):
        # Posiziona la QLabel nella vista
        # Aggiusta le coordinate (x, y) in base alle tue esigenze
        x = pos.x()
        y = pos.y()
        labelText.move(x, y)
        labelText.show()
        return labelText

    def mousePressEvent(self, event):
        # Converti la posizione del mouse nella scena
        scenePos = self.mapToScene(event.pos())
        item = self.scene.itemAt(scenePos, QTransform())
        if item == self.knob:
            self.isDragging = True
            self.updateKnobPosition(scenePos)

    def mouseMoveEvent(self, event):
        if self.isDragging:
            scenePos = self.mapToScene(event.pos())
            self.updateKnobPosition(scenePos)

    def mouseReleaseEvent(self, event):
        self.isDragging = False

    def updateKnobPosition(self, scenePos):
        """
        Per costringere il movimento circolare del knob,
        sicontrolla se la sua posizioneè all'interno del cerchio del dial
        e all'interno di un cerchio più piccolo definito come dial-1.
        :param scenePos:
        :return:
        """
        centerX = self.scene.width() / 2
        centerY = self.scene.height() / 2
        maxRadius = self.dialSize / 2 - self.knobSize / 2  # Raggio massimo
        minRadius = maxRadius - 1

        # Calcola la distanza e l'angolo dal centro del dial alla posizione del mouse
        dx = scenePos.x() - centerX
        dy = scenePos.y() - centerY
        distance = math.sqrt(dx ** 2 + dy ** 2)
        angle = math.atan2(dy, dx)

        # Limita la knob all'interno dell'area anulare
        if distance > maxRadius:
            distance = maxRadius
        elif distance < minRadius:
            distance = minRadius

        # Limiti dell'angolo in radianti (esempio: da 180 a 270 gradi)
        minAngle = math.pi // 1.4  # 180 gradi
        maxAngle = 2.5 * math.pi  # 270 gradi

        # Calcola la nuova posizione della knob
        knobX = centerX + distance * math.cos(angle)
        knobY = centerY + distance * math.sin(angle)

        # Normalizza l'angolo tra 0 e 2*pi
        normalizedAngle = angle % (2 * math.pi)

        # Applica i limiti dell'angolo
        if minAngle <= normalizedAngle <= maxAngle:
            self.knob.setPos(knobX - self.knob.boundingRect().width() / 2,
                             knobY - self.knob.boundingRect().height() / 2)
        self.scene.update()
        self.updateApertureLabel(angle)

    def updateApertureLabel(self, angle):
        # Calcola l'indice dell'apertura basato sull'angolo
        apertureIndex = self.calculateApertureIndex(angle)
    lastValue = 0

    def calculateApertureIndex(self, angle):
        # Normalizza l'angolo tra 0 e 2*pi
        minAngle = math.pi // 1.4  # 180 gradi
        maxAngle = 2.5 * math.pi  # 270 gradi

        normalizedAngle = (angle - minAngle) % ((maxAngle - minAngle) + minAngle)

        # Calcola l'indice basato sull'angolo
        anglePerAperture = (maxAngle - minAngle) / (len(self.apertureValues) - 1)
        apertureIndex = round(normalizedAngle / anglePerAperture)

        if apertureIndex < len(self.apertureValues) > 0:
            # Stampa di debug
            # print(f"Angolo: {angle}, Indice: {apertureIndex}, Valore: {self.apertureValues[apertureIndex]}")
            self.lblFStop.setText(self.apertureValues[apertureIndex])
            self.lblFStop.adjustSize()
            if self.apertureValues[apertureIndex] != self.lastValue:
                self.valueChangedSignal.emit(str(apertureIndex))
                self.lastValue = self.apertureValues[apertureIndex]
        return min(max(apertureIndex, 0), len(self.apertureValues) - 1)

    def createIrisToAngleMapping(self):
        mapping = {}
        minAngle = math.pi // 1.4  # Angolo minimo personalizzato
        maxAngle = 2.5 * math.pi  # Angolo massimo personalizzato
        for irisIndex in range(11):  # Assumendo che l'iris vada da 0 a 10
            anglePerIris = (maxAngle - minAngle) / 10
            angle = minAngle + anglePerIris * irisIndex
            mapping[irisIndex] = angle
        return mapping

    def setValue(self, index):
        index = int(index)
        if index in self.irisToAngleMapping:
            angle = self.irisToAngleMapping[index]
            self.setKnobPositionByAngle(angle)
        else:
            errorString = f"Index {index} is not valid in {self.irisToAngleMapping}"
            self.errorSignal.emit(errorString)

    def setKnobPositionByAngle(self, angle):
        centerX = self.scene.width() / 2
        centerY = self.scene.height() / 2
        maxRadius = self.dialSize / 2 - self.knobSize / 2

        # Calcola la nuova posizione della knob
        knobX = centerX + maxRadius * math.cos(angle)
        knobY = centerY + maxRadius * math.sin(angle)

        self.knob.setPos(knobX - self.knob.boundingRect().width() / 2,
                         knobY - self.knob.boundingRect().height() / 2)
        self.scene.update()
        self.updateApertureLabel(angle)


    def setRange(self, _min, _max):
        self.minValue = _min
        self.maxValue = _max

# Test del CustomDial
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWidget = QWidget()
    layout = QVBoxLayout(mainWidget)

    dial = DialAperture()
    layout.addWidget(dial)

    mainWidget.show()
    sys.exit(app.exec())
