from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from onvifManager.onvifImageManager import OnvifImageManager


class GenericLogIn(QWidget):
    imageManager: OnvifImageManager

    lblIp: QLabel
    lblPort: QLabel
    lblUser: QLabel
    lblPassword: QLabel

    lneIp: QLineEdit
    lnePort: QLineEdit
    lneUser: QLineEdit
    lnePassword: QLineEdit
    btnConnect: QPushButton

    mainLayout: QHBoxLayout

    errorSignal = pyqtSignal(str)
    serverMessageSignal = pyqtSignal(str)
    style = """
    QPushButton::checked {
    color: red;
    border: 1px solid red;
    border-radius: 2px;
    }
    QPushButton::unchecked {
    border: 1px solid black;
    border-radius: 2px;
    }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.imageManager = OnvifImageManager()
        self.imageManager.errorSignal.connect(self.errorSignal)
        self.imageManager.serverMessageSignal.connect(self.serverMessageSignal)

    def initUI(self):
        self.initWidget()
        self.setFixedWidth(640)
        self.initLayout()
        self.initConnection()
        self.setStyleSheet(self.style)

    def initWidget(self):
        self.lblIp = QLabel("IP")
        self.lblPort = QLabel(":")
        self.lblUser = QLabel("User")
        self.lblPassword = QLabel("Pass")

        self.lneIp = QLineEdit("192.168.1.52")

        self.lnePort = QLineEdit("2000")
        self.lnePort.setFixedWidth(50)
        self.lneUser = QLineEdit("admin")
        self.lneUser.setFixedWidth(80)
        self.lnePassword = QLineEdit("admin")
        self.lnePassword.setFixedWidth(80)
        self.btnConnect = QPushButton("LogIn")

        self.btnConnect.setCheckable(True)

    def initLayout(self):
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.lblIp)
        self.mainLayout.addWidget(self.lneIp)
        self.mainLayout.addWidget(self.lblPort)
        self.mainLayout.addWidget(self.lnePort)
        self.mainLayout.addWidget(self.lblUser)
        self.mainLayout.addWidget(self.lneUser)
        self.mainLayout.addWidget(self.lblPassword)
        self.mainLayout.addWidget(self.lnePassword)
        self.mainLayout.addWidget(self.btnConnect)
        self.setLayout(self.mainLayout)

    def initConnection(self):
        self.btnConnect.clicked.connect(self.connectToServer)

    def connectToServer(self):
        if self.btnConnect.isChecked():
            self.btnConnect.setText("LogOut")
            self.connect()
        else:
            self.btnConnect.setText("LogIn")
            self.disconnect()

    def connect(self):
        ip = self.lneIp.text()
        port = self.lnePort.text()
        username = self.lneUser.text()
        password = self.lnePassword.text()
        try:
            self.imageManager.connect(ip, port, username, password)
            self.serverMessageSignal.emit("Connected")
        except Exception as e:
            self.errorSignal.emit(str(e))
            self.btnConnect.setChecked(False)
            self.btnConnect.setText("LogIn")
            self.serverMessageSignal.emit("Disconnected")

    def disconnect(self):
        self.imageManager.disconnect()
        self.serverMessageSignal.emit("Disconnected")


# test widget
if __name__ == '__main__':
    import sys

    app = QApplication([])
    widget = GenericLogIn()
    widget.errorSignal.connect(print)
    widget.serverMessageSignal.connect(print)
    widget.show()
    app.exec()
