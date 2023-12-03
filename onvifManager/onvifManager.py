from onvif import ONVIFCamera
from PyQt6.QtCore import QObject, pyqtSignal

from onvifImageManager import OnvifImageManager


class OnvifCamManager(QObject):
    ip = "127.0.0.1"
    port = 2000
    cam: ONVIFCamera
    ptz = None
    mediaService = None
    mediaProfile = None
    moveRequest = None
    XMAX, XMIN, YMAX, YMIN = 1, -1, 1, -1
    username = "admin"
    password = "admin"
    imageManager: OnvifImageManager
    errorSignal = pyqtSignal(str)
    serverMessageSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def connectCameras(self, credentialDictionary: dict):
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

        try:
            self.cam = ONVIFCamera(self.ip, self.port, self.username, self.password)
            self.createMediaService()
            self.createPtzService()

            return self.serverMessageSignal.emit(f"Connected to {self.ip}:{self.port}")
        except Exception as e:
            errorString = f"From onvifCam.connectCam:\n\tThere is an issue trying connecting\n\t{e}"
            self.errorSignal.emit(errorString)

    def createMediaService(self):
        """
        Crea il media service che serve per ottenere il profilo di streaming.
        :return:
        """
        self.mediaService = self.cam.create_media_service()
        self.mediaProfile = self.mediaService.GetProfiles()[0]

    def createPtzService(self):
        """
        Crea il ptz service che serve per muovere la camera.
        :return:
        """

        self.ptz = self.cam.create_ptz_service()
        self.updatePanAndTiltRange()
        self.moveRequest = self.ptz.create_type('ContinuousMove')
        self.moveRequest.ProfileToken = self.mediaProfile.token
        if self.moveRequest.Velocity is None:
            self.moveRequest.Velocity = self.ptz.GetStatus({'ProfileToken': self.mediaProfile.token}).Position

    def updatePanAndTiltRange(self):
        """
        Ogni camera ha un range di movimento che può essere ottenuto tramite il ptz service.
        Generalmente il range è compreso tra -1 e 1.
        :return:
        """
        # Get PTZ configuration options for getting continuous move range
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.mediaProfile.PTZConfiguration.token
        # Get range of pan and tilt
        # NOTE: X and Y are velocity vector
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)
        self.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

    def getStatus(self):
        status = self.ptz.GetStatus({'ProfileToken': self.mediaProfile.token})
        xPos = status.Position.PanTilt.x
        yPos = status.Position.PanTilt.y
        zoomPos = status.Position.Zoom.x
        return f"Pan: {xPos}, Tilt: {yPos}, Zoom: {zoomPos}"

    def setHomePosition(self):
        """
        Imposta la posizione di home della camera.
        :return:
        """
        try:
            self.ptz.SetHomePosition({'ProfileToken': self.mediaProfile.token})
            self.serverMessageSignal.emit(f"Home position set:\n\t{self.getStatus()}")
        except Exception as e:
            self.errorSignal.emit(f"Errore durante il settaggio della home position: {e}")

    def goHome(self):
        """
        Muove la camera alla posizione di home.
        :return:
        """
        try:
            self.ptz.GotoHomePosition({'ProfileToken': self.mediaProfile.token})
            self.serverMessageSignal.emit(f"Go Home:\n\t{self.getStatus()}")
        except Exception as e:
            self.errorSignal.emit(f"Errore durante il movimento verso la home position: {e}")

    def stopMove(self):
        """
        Ferma il movimento della camera.
        :return:
        """
        try:
            self.moveRequest.Velocity.PanTilt.x = 0
            self.moveRequest.Velocity.PanTilt.y = 0
            self.moveRequest.Velocity.Zoom.x = 0
            self.ptz.Stop(self.moveRequest.ProfileToken)
            self.serverMessageSignal.emit(f"Stop\n\t{self.getStatus()}")
        except Exception as e:
            self.errorSignal.emit(f"Errore durante l'arresto del movimento: {e}")

    def cMove(self, xVelocity: float, yVelocity: float, zoom: float = 0.0):
        """
        MOVIMENTO CONTINUO:
            La telecamera continua a muoversi nella direzione e alla velocità
            specificate fino a quando non viene inviato un comando di stop.
            Un valore positivo di x indica che la telecamera si muoverà verso destra.

            Un valore negativo di x indica che la telecamera si muoverà verso sinistra.
            La grandezza del valore (indipendentemente dal segno) indica la velocità
            del movimento: valori più grandi significano una velocità maggiore.
            Solitamente, i valori sono normalizzati in un range, come -1 a 1,
            dove -1 rappresenta la velocità massima verso sinistra e +1
            la velocità massima verso destra.
        :param xVelocity: +1 move right, -1 move left
        :param yVelocity: +1 move up, -1 move down
        :param zoom: +1 zoom in, -1 zoom out
        :return:
        """
        try:
            self.moveRequest.Velocity.PanTilt.x = xVelocity
            self.moveRequest.Velocity.PanTilt.y = yVelocity
            self.moveRequest.Velocity.Zoom.x = zoom
            self.ptz.ContinuousMove(self.moveRequest)
            self.serverMessageSignal.emit(f"Move: x={xVelocity}, y={yVelocity}, zoom={zoom}\n\t{self.getStatus()}")
        except Exception as e:
            self.errorSignal.emit(f"Errore durante il movimento continuo: {e}")

    def rMove(self, xRel, yRel, zoomRel=0):
        """
        MOVIMENTO RELATIVO:
            La telecamera si sposta di una quantità specificata rispetto alla sua posizione corrente.
            Una volta completato il movimento, si ferma automaticamente.

        :param xRel: Quantità di movimento orizzontale (pan) relativo rispetto alla posizione corrente.
        :param yRel: Quantità di movimento verticale (tilt) relativo rispetto alla posizione corrente.
        :param zoomRel: Quantità di zoom relativo rispetto alla posizione corrente.
        :return: None. Invia un comando alla telecamera per eseguire un movimento relativo.
        """
        try:
            # Crea la richiesta per il movimento relativo
            rel_move = self.ptz.create_type('RelativeMove')
            rel_move.ProfileToken = self.mediaProfile.token

            # Imposta i valori di pan, tilt e zoom
            rel_move.Translation = {'PanTilt': {'x': xRel, 'y': yRel}, 'Zoom': {'x': zoomRel}}

            # Invia il comando di movimento relativo alla telecamera
            self.ptz.RelativeMove(rel_move)
            self.serverMessageSignal.emit(f"Relative Move: x={xRel}, y={yRel}, zoom={zoomRel}\n\t{self.getStatus()}")
        except Exception as e:
            self.errorSignal.emit(f"Errore durante il movimento relativo: {e}")

    def aMove(self, request):
        """
        MOVIMENTO ASSOLUTO:
            La telecamera si sposta verso una posizione assoluta specificata.
            Una volta raggiunta quella posizione, si ferma.
        si ferma automaticamente.
        :param request:
        :return:
        """
        pass


# test della classe
if __name__ == '__main__':
    credential = {
        "ip": "192.168.1.51",
        "port": 2000,
    }
    cam = OnvifCamManager()
    cam.errorSignal.connect(print)
    cam.serverMessageSignal.connect(print)
    cam.connectCameras(credential)
    cam.cMove(0.5, 0.5, 0.5)
    cam.stopMove()
    cam.setHomePosition()
    cam.rMove(1, 0.5, 0.5)
    cam.goHome()
