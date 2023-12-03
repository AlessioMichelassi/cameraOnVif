from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


from widget.common.genericLogIn import GenericLogIn
from widget.common.genericSetter import GenericSetter
from widget.common.ptzControlWidget import PTZPanTiltWidget, PTZControlWidget
from widget.common.shutterControl import ShutterWidget


class CCUWidget(QWidget):
    logIn: GenericLogIn
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
    hue: GenericSetter

    shutterWidget: ShutterWidget
    ptzControl: PTZControlWidget
    tabControl: QTabWidget
    tabCCU: QWidget

    mainLayout: QVBoxLayout

    _codecDict = {}

    resolutionChanged = pyqtSignal(dict)
    errorSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.imageManager = None
        self.initUI()
        self.initConnection()

    def initUI(self):
        self.tabCCU = None
        self.logIn = GenericLogIn()
        self.logIn.errorSignal.connect(self.errorSignal.emit)
        self.logIn.serverMessageSignal.connect(self.connect)
        self.initMonitor()
        self.initLayout()

    def connect(self, message):
        if message == "Connected":
            self.imageManager = self.logIn.imageManager
            if self.tabCCU is not None:
                self.tabCCU.setEnabled(True)
            else:
                self.initWidget()
                self.initConnection()
                self.initLayout2()
        else:
            self.imageManager = None
            if self.tabCCU is not None:
                self.tabCCU.setEnabled(False)

    def initWidget(self):
        self.initCommonControl()
        self.initDetail()
        self.initBrightness()
        self.initCmbShutter()
        self.ptzControl = PTZControlWidget()

    def initCommonControl(self):
        self.btnGang = self.setGenerics("Gang")
        self.btnTest = self.setGenerics("Test")
        self.btnBars = self.setGenerics("Bars")
        self.btnClose = self.setGenerics("Close")

    def initDetail(self):
        self.detail = self.setGenerics("Detail", 10)
        self.gain = self.setGenerics("Gain", 7)
        self.gamma = self.setGenerics("Gamma", 10)
        self.saturation = self.setGenerics("Saturation", 10)

    def initBrightness(self):
        self.brightness = self.initWidgetGenerics("Brightness")
        self.contrast = self.initWidgetGenerics("Contrast")
        self.gen = self.initWidgetGenerics("...")
        self.hue = self.initWidgetGenerics("Hue")
        self.initMinMaxAndValue()

    @staticmethod
    def setGenerics(arg0, arg1=None):
        if arg1 is not None:
            result = GenericSetter(arg0)
            result.setRange(0, arg1)
            result.setValue(0)
        else:
            result = QPushButton(arg0)
            result.setCheckable(True)
        result.setFixedWidth(620 // 4)
        return result

    @staticmethod
    def returnHLayout(arg0, arg1, arg2, arg3):
        detailLayout = QHBoxLayout()
        detailLayout.addWidget(arg0)
        detailLayout.addWidget(arg1)
        detailLayout.addWidget(arg2)
        detailLayout.addWidget(arg3)
        return detailLayout

    @staticmethod
    def initWidgetGenerics(arg0):
        result = GenericSetter(arg0)
        result.setRange(0, 255)
        result.setValue(0)
        result.setFixedWidth(640 // 4)
        return result

    def initMinMaxAndValue(self):
        dictionary = self.imageManager.serialize()
        """{'Exposure': { 'Mode': 'MANUAL', 'Priority': 'LowNoise', 'Window': { 'bottom': 1.0, 'top': 0.0, 
        'right': 1.0, 'left': 0.0 }, 'MinExposureTime': 10.0, 'MaxExposureTime': 40000.0, 'MinGain': 0.0, 'MaxGain': 
        100.0, 'MinIris': 0.0, 'MaxIris': 10.0, 'ExposureTime': 4000.0, 'Gain': 100.0, 'Iris': 10.0 }, 'Iris': {}, 
        'WhiteBalance': {'CbGain': 10.0, 'CrGain': 10.0, 'Extension': None, 'Mode': 'AUTO'}, 'Focus': {
        'AutoFocusMode': 'AUTO', 'DefaultSpeed': 100.0, 'Extension': None, 'FarLimit': 1000.0, 'NearLimit': 100.0}, 
        'WideDynamicRange': {'Level': 50.0, 'Mode': 'OFF'}, 'Brightness': {'Brightness': 50.0}, 'ColorSaturation': {
        'ColorSaturation': 50.0}, 'Contrast': {'Contrast': 50.0}, 'Sharpness': {'Sharpness': 50.0}, 
        'BacklightCompensation': {'Level': 10.0, 'Mode': 'OFF'}, 'Extension': {}, 'IrCutFilter': {'IrCutFilter': 
        'AUTO'}}"""
        # setta i value
        self.brightness.setValue(dictionary['Brightness']['Brightness'])
        self.contrast.setValue(dictionary['Contrast']['Contrast'])
        self.detail.setValue(dictionary['Sharpness']['Sharpness'])
        self.hue.setValue(dictionary['ColorSaturation']['ColorSaturation'])

    def initLayout(self):
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.logIn)
        self.mainLayout.addWidget(self.controlMonitor)
        self.setLayout(self.mainLayout)

    def initLayout2(self):
        self.tabControl = QTabWidget()
        self.tabControl.setFixedWidth(640)
        self.mainLayout.addWidget(self.tabControl)
        self.tabCCU = self.returnTab1()
        self.tabControl.addTab(self.tabCCU, "Camera CCU")

    def returnTab1(self):
        tabCCU = QWidget()
        vLayout = QVBoxLayout()
        cmnLayout = self.returnHLayout(self.btnGang, self.btnTest, self.btnBars, self.btnClose)
        vLayout.addLayout(cmnLayout)
        cameraCCULayout = QHBoxLayout()
        cameraCCULayout.addWidget(self.shutterWidget)
        vLayout.addLayout(cameraCCULayout)

        dtlLayout = self.returnHLayout(self.detail, self.gain, self.gamma, self.saturation)
        vLayout.addLayout(dtlLayout)

        brtLayout = self.returnHLayout(self.brightness, self.contrast, self.gen, self.hue)
        vLayout.addLayout(brtLayout)
        vLayout.addWidget(self.ptzControl)
        tabCCU.setLayout(vLayout)
        return tabCCU

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

    imageManager = OnvifImageManager()
    imageManager.errorSignal.connect(print)
    imageManager.serverMessageSignal.connect(print)
    mw = CCUWidget()
    mw.show()
    sys.exit(app.exec())
