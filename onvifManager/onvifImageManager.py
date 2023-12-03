from onvif import ONVIFCamera
from PyQt6.QtCore import QObject, pyqtSignal


class OnvifImageManager(QObject):
    cam: ONVIFCamera
    imagingService: ONVIFCamera
    mediaService: ONVIFCamera
    currentSettings: None
    profiles: None
    videoToken: None
    errorSignal = pyqtSignal(str)
    serverMessageSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def connect(self, ip, port, username, password):
        try:
            self.cam = ONVIFCamera(ip, port, username, password)
            if self.cam.devicemgmt.GetDeviceInformation():
                self.initImagingSettings()
            else:
                self.serverMessageSignal.emit("Disconnected")
        except Exception as e:
            errorString = f"Error initializing Image Manager: {e}"
            self.errorSignal.emit(errorString)

    def disconnect(self):
        self.cam = None
        self.serverMessageSignal.emit("Disconnected")

    def initImagingSettings(self):
        try:
            self.mediaService = self.cam.create_media_service()
            self.profiles = self.mediaService.GetProfiles()
            if self.profiles:
                self.videoToken = self.profiles[0].VideoSourceConfiguration.SourceToken
                self.getImagingSettings()
            else:
                self.errorSignal.emit("No profiles found on the camera.")
        except Exception as e:
            self.errorSignal.emit(f"Error getting imaging settings: {e}")

    @property
    def exposure(self):
        """
        Ottiene le impostazioni correnti di esposizione della telecamera.
        Restituisce un dizionario con le impostazioni se disponibili, altrimenti un dizionario vuoto.
        """
        exposure_settings = {}
        if hasattr(self.currentSettings, 'Exposure') and self.currentSettings.Exposure is not None:
            for attr in dir(self.currentSettings.Exposure):
                if not attr.startswith('_') and hasattr(self.currentSettings.Exposure, attr):
                    value = getattr(self.currentSettings.Exposure, attr)
                    exposure_settings[attr] = value
        return exposure_settings

    def getExposureTime(self):
        try:
            # Assicurati di avere le impostazioni di imaging correnti
            self.getImagingSettings()

            if hasattr(self.currentSettings, 'Exposure') and hasattr(self.currentSettings.Exposure, 'ExposureTime'):
                return self.currentSettings.Exposure.ExposureTime
            else:
                return "No exposure time setting available"
        except Exception as e:
            self.errorSignal.emit(f"Error retrieving current exposure time: {e}")
            return f"Error: {e}"

    def setExposureTime(self, value):
        try:
            # Assicurati di avere le impostazioni di imaging correnti
            self.getImagingSettings()
            # Aggiorna solo il tempo di esposizione
            if hasattr(self.currentSettings, 'Exposure'):
                self.currentSettings.Exposure.ExposureTime = value

                self.imagingService.SetImagingSettings({
                    'VideoSourceToken': self.videoToken,
                    'ImagingSettings': self.currentSettings
                })
            else:
                self.errorSignal.emit("Exposure settings not available")
        except Exception as e:
            self.errorSignal.emit(f"Error setting exposure time: {e}")

    def getExposureModes(self):
        try:
            options = self.imagingService.GetOptions({'VideoSourceToken': self.videoToken})
            if hasattr(options, 'Exposure'):
                return options.Exposure.Mode  # Restituisce una lista delle modalità di esposizione supportate
            else:
                return ["No exposure modes available"]
        except Exception as e:
            self.errorSignal.emit(f"Error retrieving exposure modes: {e}")
            return []

    def setExposureMode(self, mode):
        try:
            # Assicurati di avere le impostazioni di imaging correnti
            self.getImagingSettings()
            # Aggiorna solo la modalità di esposizione
            if hasattr(self.currentSettings, 'Exposure'):
                self.currentSettings.Exposure.Mode = mode

                self.imagingService.SetImagingSettings({
                    'VideoSourceToken': self.videoToken,
                    'ImagingSettings': self.currentSettings
                })
            else:
                self.errorSignal.emit("Exposure settings not available")
        except Exception as e:
            self.errorSignal.emit(f"Error setting exposure mode: {e}")

    def getExposurePriority(self):
        try:
            options = self.imagingService.GetOptions({'VideoSourceToken': self.videoToken})
            if hasattr(options, 'Exposure'):
                return options.Exposure.Priority  # Restituisce una lista delle priorità di esposizione supportate
            else:
                return ["No exposure priorities available"]
        except Exception as e:
            self.errorSignal.emit(f"Error retrieving exposure priorities: {e}")
            return []

    def setExposurePriority(self, priority):
        try:
            # Assicurati di avere le impostazioni di imaging correnti
            self.getImagingSettings()
            # Aggiorna solo la modalità di esposizione
            if hasattr(self.currentSettings, 'Exposure'):
                self.currentSettings.Exposure.Priority = priority

                self.imagingService.SetImagingSettings({
                    'VideoSourceToken': self.videoToken,
                    'ImagingSettings': self.currentSettings
                })
            else:
                self.errorSignal.emit("Exposure settings not available")
        except Exception as e:
            self.errorSignal.emit(f"Error setting exposure priority: {e}")

    @property
    def iris(self) -> str:
        if hasattr(self.currentSettings, 'Exposure') and hasattr(self.currentSettings.Exposure, 'Iris'):
            return str(self.currentSettings.Exposure.Iris)
        else:
            return "Iris setting not available"

    def setIris(self, value):
        try:
            self.getImagingSettings()
            if hasattr(self.currentSettings, 'Exposure'):
                float_value = float(value)  # Converti il valore in float
                self.currentSettings.Exposure.Iris = float_value

                self.imagingService.SetImagingSettings({
                    'VideoSourceToken': self.videoToken,
                    'ImagingSettings': self.currentSettings
                })

                # Ricarica le impostazioni per verificare che l'aggiornamento sia andato a buon fine
                self.getImagingSettings()
                if self.currentSettings.Exposure.Iris == float_value:
                    print(f"Iris set to {float_value}")
                else:
                    print(f"Error setting iris to {float_value}, current iris is {self.currentSettings.Exposure.Iris}")

            else:
                self.errorSignal.emit("Iris settings not available")
        except Exception as e:
            self.errorSignal.emit(f"Error setting iris {value}: {e}")

    @property
    def whiteBalance(self) -> dict:
        white_balance_dict = {}
        if hasattr(self.currentSettings, 'WhiteBalance'):
            white_balance = self.currentSettings.WhiteBalance
            for attr in dir(white_balance):
                if not attr.startswith('_'):
                    value = getattr(white_balance, attr)
                    white_balance_dict[attr] = value
        return white_balance_dict

    @property
    def focus(self) -> dict:
        focus_dict = {}
        if hasattr(self.currentSettings, 'Focus'):
            focus = self.currentSettings.Focus
            for attr in dir(focus):
                if not attr.startswith('_'):
                    value = getattr(focus, attr)
                    focus_dict[attr] = value
        return focus_dict

    @property
    def wideDynamicRange(self) -> dict:
        wide_dynamic_range_dict = {}
        if hasattr(self.currentSettings, 'WideDynamicRange'):
            wide_dynamic_range = self.currentSettings.WideDynamicRange
            for attr in dir(wide_dynamic_range):
                if not attr.startswith('_'):
                    value = getattr(wide_dynamic_range, attr)
                    wide_dynamic_range_dict[attr] = value
        return wide_dynamic_range_dict

    @property
    def brightness(self) -> dict:
        if hasattr(self.currentSettings, 'Brightness'):
            # 'Brightness' è un valore singolo, non un oggetto complesso
            return {'Brightness': self.currentSettings.Brightness}
        else:
            return {}

    @property
    def colorSaturation(self) -> dict:
        if hasattr(self.currentSettings, 'ColorSaturation'):
            # 'ColorSaturation' è un valore singolo, non un oggetto complesso
            return {'ColorSaturation': self.currentSettings.ColorSaturation}
        else:
            return {}

    @property
    def contrast(self) -> dict:
        if hasattr(self.currentSettings, 'Contrast'):
            # 'Contrast' è un valore singolo, non un oggetto complesso
            return {'Contrast': self.currentSettings.Contrast}
        else:
            return {}

    @property
    def sharpness(self) -> dict:
        if hasattr(self.currentSettings, 'Sharpness'):
            # 'Sharpness' è un valore singolo, non un oggetto complesso
            return {'Sharpness': self.currentSettings.Sharpness}
        else:
            return {}

    @property
    def backLightCompensation(self) -> dict:
        back_light_compensation_dict = {}
        if hasattr(self.currentSettings, 'BacklightCompensation'):
            back_light_compensation = self.currentSettings.BacklightCompensation
            for attr in dir(back_light_compensation):
                if not attr.startswith('_'):
                    value = getattr(back_light_compensation, attr)
                    back_light_compensation_dict[attr] = value
        return back_light_compensation_dict

    @property
    def extention(self) -> dict:
        extention_dict = {}
        if hasattr(self.currentSettings, 'Extension'):
            extention = self.currentSettings.Extension
            for attr in dir(extention):
                if not attr.startswith('_'):
                    value = getattr(extention, attr)
                    extention_dict[attr] = value
        return extention_dict

    @property
    def IrCutFilter(self) -> dict:
        if hasattr(self.currentSettings, 'IrCutFilter'):
            # 'IrCutFilter' è un valore singolo, non un oggetto complesso
            return {'IrCutFilter': self.currentSettings.IrCutFilter}

    def getImagingSettings(self):
        try:
            self.imagingService = self.cam.create_imaging_service()
            self.currentSettings = self.imagingService.GetImagingSettings({"VideoSourceToken": self.videoToken})

            # return self.listAllProperties(self.currentSettings, "ImagingSettings")
        except Exception as e:
            self.errorSignal.emit(f"Error retrieving imaging settings: {e}")

    def listAllPropertyNames(self, obj, prefix=""):
        property_names = []
        for attr in dir(obj):
            if not attr.startswith('_'):
                if attr not in ['Exposure', 'Iris', 'Focus', 'WhiteBalance',
                                'WideDynamicRange', 'Brightness', 'ColorSaturation',
                                'Contrast', 'Sharpness',
                                'BacklightCompensation', 'Extension', 'IrCutFilter']:
                    value = getattr(obj, attr)
                    full_attr_name = f"{prefix}.{attr}" if prefix else attr
                    if isinstance(value, str) or not hasattr(value, '__dict__'):
                        property_names.append(full_attr_name)
                    else:
                        property_names.extend(self.listAllPropertyNames(value, full_attr_name))
        return property_names

    def returnNotIncludedProperties(self):
        try:
            if self.currentSettings:
                return self.listAllPropertyNames(self.currentSettings)
            else:
                return ["No current settings available"]
        except Exception as e:
            self.errorSignal.emit(f"Error retrieving property names: {e}")
            return []

    def serialize(self):
        return {
            'Exposure': self.exposure,
            'Iris': self.iris,
            'WhiteBalance': self.whiteBalance,
            'Focus': self.focus,
            'WideDynamicRange': self.wideDynamicRange,
            'Brightness': self.brightness,
            'ColorSaturation': self.colorSaturation,
            'Contrast': self.contrast,
            'Sharpness': self.sharpness,
            'BacklightCompensation': self.backLightCompensation,
            'Extension': self.extention,
            'IrCutFilter': self.IrCutFilter,
        }


# Test della classe
if __name__ == '__main__':
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
    print("Image Manager initialized.")
    print(imageManager.getExposureModes())
    print(imageManager.getExposurePriority())
    print(imageManager.iris)
    imageManager.setIris(5)
    print(imageManager.iris)
