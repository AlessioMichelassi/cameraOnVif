from onvif import ONVIFCamera
from PyQt6.QtCore import QObject, pyqtSignal


class onvifCam(QObject):
    ip = "127.0.0.1"
    port = 2000
    cam: ONVIFCamera
    username = "admin"
    password = "admin"

    errorSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.initConnection()

    def initUI(self):
        pass

    def initConnection(self):
        pass

    def initCredential(self, credential):
        """
        Credential deve essere un dizionario con le chiavi ip e port
        username e password.
        credential = {
            "ip": "127.0.0.1",
            "port": 2000,
            "username": "admin",
            "password": "admin"}
        :param credential:
        :return:
        """
        self.ip = credential["ip"]
        self.port = credential["port"]
        if "username" in credential.keys():
            self.username = credential["username"]
        if "password" in credential.keys():
            self.password = credential["password"]

    def connectCam(self):
        try:
            self.cam = ONVIFCamera(self.ip, self.port, self.username, self.password)
        except Exception as e:
            errorString = f"From onvifCam.connectCam:\n\tThere is an issue trying connecting\n\t{e}"
            self.errorSignal.emit(errorString)

    def getDeviceInformation(self):
        """
        Ritorna un dizionario con le informazioni del dispositivo
        :return: dict
        """
        return self.cam.devicemgmt.GetDeviceInformation()

    def get_media_profiles(self):
        try:
            media_service = self.cam.create_media_service()
            profiles = media_service.GetProfiles()
            return profiles
        except Exception as e:
            errorString = f"From onvifCam.get_media_profiles:\n\tError getting profiles\n\t{e}"
            self.errorSignal.emit(errorString)
            return None


# test della classe
if __name__ == '__main__':
    credential = {
        "ip": "192.168.1.51",
        "port": 2000,
    }
    cam = onvifCam()
    cam.errorSignal.connect(print)
    cam.initCredential(credential)
    cam.connectCam()
    print(cam.get_media_profiles())