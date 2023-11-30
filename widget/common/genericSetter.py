from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class GenericSetter(QWidget):

    lblName: QLabel
    lneValue: QLineEdit
    sbxValue: QSpinBox

    valueChangedSignal = pyqtSignal(str)
    errorSignal = pyqtSignal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.initWidget(name)
        self.initUI(name)
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

    def initUI(self, name):
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.lblName)
        mainLayout.addWidget(self.lneValue)
        mainLayout.addWidget(self.sbxValue)
        self.setLayout(mainLayout)

    def initConnection(self):
        self.sbxValue.valueChanged.connect(self.sbxValueChanged)
        self.lneValue.textChanged.connect(self.lneValueChanged)

    def sbxValueChanged(self, value):
        self.lneValue.setText(str(value))
        self.valueChangedSignal.emit(str(value))

    def lneValueChanged(self, value):
        self.sbxValue.setValue(int(value))
        self.valueChangedSignal.emit(str(value))

    def setValue(self, value):
        self.sbxValue.setValue(int(value))
        self.lneValue.setText(str(value))

    def getValue(self):
        return self.sbxValue.value()

    def setRange(self, _min, _max):
        self.sbxValue.setRange(_min, _max)
        self.lneValue.setValidator(QIntValidator(_min, _max))


# test class
if __name__ == '__main__':
    app = QApplication([])
    win = GenericSetter("Test")
    win.show()
    app.exec()