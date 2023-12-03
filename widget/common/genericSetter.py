from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class GenericSetter(QWidget):
    lblName: QLabel
    lneValue: QLineEdit
    sbxValue: QSpinBox
    sldValue: QSlider
    lblMin: QLabel
    lblMax: QLabel
    valueChangedSignal = pyqtSignal(str)
    errorSignal = pyqtSignal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.initWidget(name)
        self.initUI()
        self.initConnection()

    def initWidget(self, name):
        self.lblName = QLabel(name)
        self.lneValue = QLineEdit()

        self.sbxValue = QSpinBox()
        self.sbxValue.setRange(0, 255)
        self.lneValue.setValidator(QIntValidator(0, 255))
        self.sbxValue.setSingleStep(1)
        self.sbxValue.setValue(0)
        self.lneValue.setText("0")
        self.lblMin = QLabel("0")
        self.lblMax = QLabel("255")
        self.sldValue = QSlider(Qt.Orientation.Horizontal)

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.lblName)
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.lneValue)
        controlLayout.addWidget(self.sbxValue)
        mainLayout.addLayout(controlLayout)
        sldLayout = QHBoxLayout()
        sldLayout.addWidget(self.lblMin)
        sldLayout.addWidget(self.sldValue)
        sldLayout.addWidget(self.lblMax)
        mainLayout.addLayout(sldLayout)
        self.setLayout(mainLayout)

    def initConnection(self):
        self.sbxValue.valueChanged.connect(self.sbxValueChanged)
        self.lneValue.textChanged.connect(self.lneValueChanged)
        self.sldValue.valueChanged.connect(self.sldValueChanged)

    def sbxValueChanged(self, value):
        self.lneValue.setText(str(value))
        self.sldValue.setValue(int(value))
        self.valueChangedSignal.emit(str(value))

    def lneValueChanged(self, value):
        value = float(value)
        self.sbxValue.setValue(int(value))
        self.sldValue.setValue(int(value))
        self.valueChangedSignal.emit(str(value))

    def sldValueChanged(self, value):
        self.sbxValue.setValue(int(value))
        self.lneValue.setText(str(value))
        self.valueChangedSignal.emit(str(value))

    def setValue(self, value):
        self.sbxValue.setValue(int(value))
        self.lneValue.setText(str(value))

    def getValue(self):
        return self.sbxValue.value()

    def setRange(self, _min, _max):
        _min = int(_min)
        _max = int(_max)
        self.sbxValue.setRange(_min, _max)
        self.lneValue.setValidator(QIntValidator(_min, _max))
        self.sldValue.setRange(_min, _max)
        self.lblMin.setText(str(_min))
        self.lblMax.setText(str(_max))


# test class
if __name__ == '__main__':
    app = QApplication([])
    win = GenericSetter("Test")
    win.show()
    app.exec()
