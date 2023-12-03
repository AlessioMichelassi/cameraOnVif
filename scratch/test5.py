from onvif import ONVIFCamera
from time import sleep

# Dati per l'accesso alla telecamera
mycam = ONVIFCamera('192.168.1.51', 2000, 'admin', 'admin')

# Crea il servizio Imaging
imaging_service = mycam.create_imaging_service()

# Ottieni il token del profilo video
media_service = mycam.create_media_service()
profiles = media_service.GetProfiles()
video_source_token = profiles[0].VideoSourceConfiguration.SourceToken
if isinstance(video_source_token, str):
    print(f"video_source_token: {type(video_source_token)}")
    print(f"video_source_token: {video_source_token}")
    # Ottieni le impostazioni correnti dell'imaging
    imaging_settings = imaging_service.GetImagingSettings({'VideoSourceToken': video_source_token})
    print("imaging_settings Ok")
    if hasattr(imaging_settings, 'Exposure'):
        # stampa le impostazioni correnti dell'esposizione
        print('Exposure settings:')
        print(f"\tMode: {imaging_settings.Exposure.Mode}")
        """imaging_settings.Exposure.Mode = 'MANUAL'  # o 'AUTO' se supportato
        # Assicurati di impostare un valore valido per il tuo dispositivo
        imaging_settings.Exposure.ShutterSpeed = '1/30'  # Esempio di valore

    # Invia le nuove impostazioni al servizio Imaging
    imaging_service.SetImagingSettings({
        'VideoSourceToken': video_source_token,
        'ImagingSettings': imaging_settings
    })"""
else:
    print('Error getting video source token')
    print(f"video_source_token: {type(video_source_token)}")
    print(f"video_source_token: {video_source_token}")
