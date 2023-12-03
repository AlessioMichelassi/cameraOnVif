from onvif import ONVIFCamera
from PyQt6.QtCore import QObject, pyqtSignal


class onvifCam(QObject):
    ip = "127.0.0.1"
    port = 2000
    cam: ONVIFCamera
    ptzService = None
    mediaService = None
    ptzTokens = None

    username = "admin"
    password = "admin"



    errorSignal = pyqtSignal(str)
    serverMessageSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.initConnection()

    def initUI(self):
        pass

    def initConnection(self):
        pass

    def initCredential(self, credentialDictionary: dict) :
        """
        Credential deve essere un dizionario con le chiavi ip e port
        username e password.
        credential = {
            "ip": "127.0.0.1",
            "port": 2000,
            "username": "admin",
            "password": "admin"}
        :param credentialDictionary:
        :return:
        """
        self.ip = credentialDictionary["ip"]
        self.port = credentialDictionary["port"]
        if "username" in credentialDictionary.keys():
            self.username = credentialDictionary["username"]
        if "password" in credentialDictionary.keys():
            self.password = credentialDictionary["password"]

    def connectCam(self):
        try:
            self.cam = ONVIFCamera(self.ip, self.port, self.username, self.password)
            self.createPtzService()
            return self.serverMessageSignal.emit(f"Connected to {self.ip}:{self.port}")
        except Exception as e:
            errorString = f"From onvifCam.connectCam:\n\tThere is an issue trying connecting\n\t{e}"
            self.errorSignal.emit(errorString)

    def createPtzService(self):
        self.ptzService = self.cam.create_ptz_service()
        self.mediaService = self.getMediaProfile()
        self.ptzTokens = self.ptzService.GetConfigurations()[0]

    def getDeviceInformation(self):
        """
        Ritorna un dizionario con le informazioni del dispositivo
        :return: dict
        """
        return self.cam.devicemgmt.GetDeviceInformation()

    def getHostname(self):
        """
        Ritorna il nome del dispositivo
        :return: str
        """
        return self.cam.devicemgmt.GetHostname()

    def getMediaProfile(self):
        try:
            media_service = self.cam.create_media_service()
            profiles = media_service.GetProfiles()
            return profiles
        except Exception as e:
            errorString = f"From onvifCam.get_media_profiles:\n\tError getting profiles\n\t{e}"
            self.errorSignal.emit(errorString)
            return None

    def movePan(self, speed: float):
        """
        Muove la camera in orizzontale
        :param speed: float
        :return:
        """
        try:
            if self.ptzService is None:
                self.createPtzService()

            request = self.ptzService.create_type('ContinuousMove')
            request.ProfileToken = self.ptzTokens
            request.Velocity = {'PanTilt': {'x': speed, 'y': 0}}

            self.ptzService.ContinuousMove(request)
        except Exception as e:
            errorString = f"From onvifCam.movePan:\n\tError moving camera\n\t{e}"
            self.errorSignal.emit(errorString)


# test della classe
if __name__ == '__main__':
    credential = {
        "ip": "192.168.1.51",
        "port": 2000,
    }
    cam = onvifCam()
    cam.errorSignal.connect(print)
    cam.serverMessageSignal.connect(print)
    cam.initCredential(credential)
    cam.connectCam()
    cam.movePan(0.5)
