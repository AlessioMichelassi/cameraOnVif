from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from onvifManager import onvifImageManager
from widget.common.dialAperture import DialAperture
from widget.common.genericSetter import GenericSetter


class ShutterWidget(QWidget):
    cmbShutterMode: QComboBox
    cmbShutterPriority: QComboBox
    exposureTimeWidget: GenericSetter
    gainWidget: GenericSetter
    irisWidget: DialAperture

    minExposureTime: float
    maxExposureTime: float
    minGain: float
    maxGain: float
    minIris: float
    maxIris: float

    exposureTime: float
    gain: float
    iris: float

    errorSignal = pyqtSignal(str)
    serverMessageSignal = pyqtSignal(str)

    def __init__(self, _imageManager: onvifImageManager, parent=None):
        super().__init__(parent)
        self.imageManager = _imageManager
        self.initUI()

    def initUI(self):
        if self.imageManager is not None:
            self.initWidget()

    def initConnection(self):
        self.exposureTimeWidget.valueChangedSignal.connect(self.setExposureTimeValue)
        self.gainWidget.valueChangedSignal.connect(self.setGainValue)
        self.irisWidget.valueChangedSignal.connect(self.setIrisValue)
        self.cmbShutterMode.currentTextChanged.connect(self.setShutterMode)
        self.cmbShutterPriority.currentTextChanged.connect(self.setShutterPriority)



    def initWidget(self):
        self.initShutterMode()
        self.initShutterPriority()
        self.initExposureTime()
        self.initGain()
        self.initIris()
        self.initLayout()

    def initLayout(self):
        vLayout = QVBoxLayout()
        spacerSingle = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        vLayout.addItem(spacerSingle)
        vLayout.addWidget(self.cmbShutterMode)
        vLayout.addWidget(self.cmbShutterPriority)
        vLayout.addWidget(self.irisWidget)
        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(self.exposureTimeWidget)
        vLayout2.addWidget(self.gainWidget)
        spacer = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vLayout2.addItem(spacer)
        hLayout = QHBoxLayout()
        hLayout.addLayout(vLayout)
        hLayout.addLayout(vLayout2)
        self.setLayout(hLayout)
        self.setMinMax()

    def initShutterMode(self):
        expMode = self.imageManager.getExposureModes()
        self.cmbShutterMode = QComboBox()
        self.cmbShutterMode.addItems(expMode)

    def initShutterPriority(self):
        expPriority = self.imageManager.getExposurePriority()
        self.cmbShutterPriority = QComboBox()
        self.cmbShutterPriority.addItems(expPriority)

    def initExposureTime(self):
        self.exposureTimeWidget = self.initGenericWidgets("Exposure Time")

    def initGain(self):
        self.gainWidget = self.initGenericWidgets("Gain")
        self.gainWidget.setEnabled(False)

    def initIris(self):
        self.irisWidget = DialAperture()

    @staticmethod
    def initGenericWidgets(arg0):
        result = GenericSetter(arg0)
        result.setRange(0, 100)
        result.setValue(0)
        return result

    def setMinMax(self):
        dictionary = self.imageManager.exposure
        self.exposureTimeWidget.setRange(dictionary['MinExposureTime'], dictionary['MaxExposureTime'])
        self.gainWidget.setRange(dictionary['MinGain'], dictionary['MaxGain'])
        self.irisWidget.setRange(dictionary['MinIris'], dictionary['MaxIris'])
        self.exposureTimeWidget.setValue(dictionary['ExposureTime'])
        self.gainWidget.setValue(dictionary['Gain'])
        self.irisWidget.setValue(dictionary['Iris'])
        self.getValue()
        self.initConnection()

    def setExposureTimeValue(self, value):
        pass

    def setGainValue(self, value):
        pass

    def setIrisValue(self, value):
        self.imageManager.setIris(value)

    def setShutterMode(self, mode):
        self.imageManager.setExposureMode(mode)
        self.setMinMax()

    def setShutterPriority(self, priority):
        self.imageManager.setExposurePriority(priority)
        self.setMinMax()

    def getValue(self):
        dictionary = self.imageManager.exposure
        exposureTime = dictionary['ExposureTime']
        gain = dictionary['Gain']
        iris = dictionary['Iris']
        print(exposureTime, gain, iris)
        self.exposureTimeWidget.setValue(exposureTime)
        self.gainWidget.setValue(gain)
        self.irisWidget.setValue(iris)

    def sendErrorMessage(self, message):
        self.errorSignal.emit(message)


if __name__ == '__main__':
    from onvifManager.onvifImageManager import OnvifImageManager

    app = QApplication([])

    credential = {
        "ip": "192.168.1.52",
        "port": 2000,
        "username": "admin",
        "password": "admin"
    }

    imageManager = OnvifImageManager()
    imageManager.connect(**credential)
    imageManager.errorSignal.connect(print)
    imageManager.serverMessageSignal.connect(print)
    win = ShutterWidget(imageManager)
    win.show()
    app.exec()
