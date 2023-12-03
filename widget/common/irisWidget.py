from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class IrisWidget(QWidget):

    fStopList = ["F1.8", "F2.0", "F2.4", "F2.8", "F3.4", "F4.0", "F4.8", "F5.6", "F6.8", "F8.0", "F9.6", "F11.0", "Close"]
    dialIris: QDial
    lblValue: QLabel
    backgroundColor = QColor(40, 40, 40)

    irisChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.initConnection()

    def initUI(self):
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        self.dialIris = QDial()
        self.dialIris.setRange(0, 24)
        self.dialIris.setSingleStep(1)
        self.dialIris.setValue(12)
        self.dialIris.setNotchesVisible(True)
        self.dialIris.setWrapping(True)
        self.dialIris.setNotchTarget(1.0)
        self.setDialStyle()
        self.lblValue = QLabel(self.fStopList[12])  # Label per visualizzare il valore corrente
        self.lblValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblValue.setStyleSheet("color: white;")

    def initLayout(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.dialIris)
        mainLayout.addWidget(self.lblValue)
        self.setLayout(mainLayout)

    def setDialStyle(self):
        style = """
        QDial {
            background-color: rgb(40, 40, 40);
            color: rgb(255, 100, 100);
            border-radius: 5px;
        }
        QDial::handle {
            background-color: rgb(255, 100, 100);
            border-radius: 5px;
        }
        """
        self.dialIris.setStyleSheet(style)


    def initConnection(self):
        self.dialIris.valueChanged.connect(self.updateDisplay)

    def updateDisplay(self, value):
        self.lblValue.setText(str(value))
        self.lblValue.adjustSize()
        self.lblValue.update()
        self.lblValue.repaint()

    def setRange(self, _min, _max):
        _min = int(_min)
        _max = int(_max)
        self.dialIris.setRange(_min, _max)

    def setValue(self, value):
        value = int(value)
        self.dialIris.setValue(value)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = IrisWidget()
    w.show()
    sys.exit(app.exec())