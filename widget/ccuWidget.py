from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from widget.common.genericSetter import GenericSetter
from widget.common.irisWidget import IrisWidget
from widget.common.shutterControl import ShutterWidget


class CCUWidget(QWidget):
    controlMonitor: QLabel

    # generic control
    btnGang: QPushButton
    btnTest: QPushButton
    btnBars: QPushButton
    btnClose: QPushButton

    # detail control
    detail: GenericSetter
    gain: GenericSetter
    gamma: GenericSetter
    saturation: GenericSetter
    brightness: GenericSetter
    contrast: GenericSetter
    gen: GenericSetter
    _codecDict = {}

    resolutionChanged = pyqtSignal(dict)
    errorSignal = pyqtSignal(str)

    def __init__(self, _imageManager, parent=None):
        super().__init__(parent)
        self.imageManager = _imageManager
        self.initUI()
        self.initConnection()

    def initUI(self):
        if self.imageManager is not None:
            self.initWidget()
            self.initLayout()

    def initWidget(self):
        self.initMonitor()
        self.initCommonControl()
        self.initDetail()
        self.initBrightness()
        self.initCmbShutter()
        self.initCmbGain()

    def initCommonControl(self):
        self.btnGang = self.setBtnGenerics("Gang")
        self.btnTest = self.setBtnGenerics("Test")
        self.btnBars = self.setBtnGenerics("Bars")
        self.btnClose = self.setBtnGenerics("Close")

    @staticmethod
    def setBtnGenerics(arg0):
        result = QPushButton(arg0)
        result.setCheckable(True)
        result.setFixedWidth(640 // 4)
        return result

    def returnCommonControlLayout(self):
        commonControlLayout = QHBoxLayout()
        commonControlLayout.addWidget(self.btnGang)
        commonControlLayout.addWidget(self.btnTest)
        commonControlLayout.addWidget(self.btnBars)
        commonControlLayout.addWidget(self.btnClose)
        return commonControlLayout

    def initDetail(self):
        self.detail = GenericSetter("Detail")
        self.detail.setRange(0, 10)
        self.detail.setValue(0)
        self.detail.setFixedWidth(640 // 4)
        self.gain = GenericSetter("Gain")
        self.gain.setRange(0, 7)
        self.gain.setValue(0)
        self.gain.setFixedWidth(640 // 4)
        self.gamma = GenericSetter("Gamma")
        self.gamma.setRange(0, 10)
        self.gamma.setValue(0)
        self.gamma.setFixedWidth(640 // 4)
        self.saturation = GenericSetter("Saturation")
        self.saturation.setRange(0, 10)
        self.saturation.setValue(0)
        self.saturation.setFixedWidth(640 // 4)

    def returnDetailLayout(self):
        detailLayout = QHBoxLayout()
        detailLayout.addWidget(self.detail)
        detailLayout.addWidget(self.gain)
        detailLayout.addWidget(self.gamma)
        detailLayout.addWidget(self.saturation)
        return detailLayout

    def initBrightness(self):
        self.brightness = self.initWidgetGenerics("Brightness")
        self.contrast = self.initWidgetGenerics("Contrast")
        self.gen = self.initWidgetGenerics("...")
        self.hue = self.initWidgetGenerics("Hue")
        self.initMinMaxAndValue()

    @staticmethod
    def initWidgetGenerics(arg0):
        result = GenericSetter(arg0)
        result.setRange(0, 255)
        result.setValue(0)
        result.setFixedWidth(640 // 4)
        return result

    def initMinMaxAndValue(self):
        dictionary = self.imageManager.serialize()
        """
            {'Exposure': {
        'Mode': 'MANUAL',
        'Priority': 'LowNoise',
        'Window': {
            'bottom': 1.0,
            'top': 0.0,
            'right': 1.0,
            'left': 0.0
        },
        'MinExposureTime': 10.0,
        'MaxExposureTime': 40000.0,
        'MinGain': 0.0,
        'MaxGain': 100.0,
        'MinIris': 0.0,
        'MaxIris': 10.0,
        'ExposureTime': 4000.0,
        'Gain': 100.0,
        'Iris': 10.0
    }, 'Iris': {}, 'WhiteBalance': {'CbGain': 10.0, 'CrGain': 10.0, 'Extension': None, 'Mode': 'AUTO'}, 'Focus': {'AutoFocusMode': 'AUTO', 'DefaultSpeed': 100.0, 'Extension': None, 'FarLimit': 1000.0, 'NearLimit': 100.0}, 'WideDynamicRange': {'Level': 50.0, 'Mode': 'OFF'}, 'Brightness': {'Brightness': 50.0}, 'ColorSaturation': {'ColorSaturation': 50.0}, 'Contrast': {'Contrast': 50.0}, 'Sharpness': {'Sharpness': 50.0}, 'BacklightCompensation': {'Level': 10.0, 'Mode': 'OFF'}, 'Extension': {}, 'IrCutFilter': {'IrCutFilter': 'AUTO'}}

        """
        # setta i value
        self.brightness.setValue(dictionary['Brightness']['Brightness'])
        self.contrast.setValue(dictionary['Contrast']['Contrast'])
        self.detail.setValue(dictionary['Sharpness']['Sharpness'])
        self.hue.setValue(dictionary['ColorSaturation']['ColorSaturation'])

    def returnBrightnessLayout(self):
        brightnessLayout = QHBoxLayout()
        brightnessLayout.addWidget(self.brightness)
        brightnessLayout.addWidget(self.contrast)
        brightnessLayout.addWidget(self.gen)
        brightnessLayout.addWidget(self.hue)
        return brightnessLayout

    def initLayout(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.controlMonitor)
        cameraCCULayout = QHBoxLayout()
        cameraCCULayout.addWidget(self.shutterWidget)
        mainLayout.addLayout(cameraCCULayout)
        cmnLayout = self.returnCommonControlLayout()
        mainLayout.addLayout(cmnLayout)
        dtlLayout = self.returnDetailLayout()
        mainLayout.addLayout(dtlLayout)

        brtLayout = self.returnBrightnessLayout()
        mainLayout.addLayout(brtLayout)
        self.setLayout(mainLayout)

    def initConnection(self):
        pass

    def initMonitor(self):
        self.controlMonitor = QLabel("Monitor")
        self.controlMonitor.setFixedSize(640, 480)
        self.controlMonitor.setStyleSheet("background-color: black")
        self.controlMonitor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.controlMonitor.setFrameStyle(QFrame.Shape.Box)
        self.controlMonitor.setLineWidth(1)
        self.controlMonitor.setMidLineWidth(1)

    def initCmbShutter(self):
        self.shutterWidget = ShutterWidget(self.imageManager)


    def initCmbGain(self):
        self.gainList = ["0", "3", "6", "9", "12", "15", "18", "21", "24"]
        self.cmbGain = QComboBox()
        self.cmbGain.addItems(self.gainList)
        self.cmbGain.setCurrentIndex(0)


# test Widget
if __name__ == "__main__":
    import sys
    from onvifManager.onvifImageManager import OnvifImageManager
    app = QApplication([])

    credential = {
        "ip": "192.168.1.52",
        "port": 2000,
        "username": "admin",
        "password": "admin"
    }

    imageManager = OnvifImageManager(**credential)
    imageManager.errorSignal.connect(print)
    imageManager.serverMessageSignal.connect(print)
    mw = CCUWidget(imageManager)
    mw.show()
    sys.exit(app.exec())
