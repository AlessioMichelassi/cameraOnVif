import zeep
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QHBoxLayout, QTabWidget

from scratch.test import onvifCam


class ProfileViewer(QWidget):
    def __init__(self, profile_list):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget)
        self.create_profile_tabs(profile_list)

    def create_profile_tabs(self, profile_list):
        for profile_data in profile_list:
            profile_name = getattr(profile_data, 'Name', 'Unknown Profile')
            profile_tab = QWidget()
            profile_tab_layout = QVBoxLayout(profile_tab)

            # Creazione del QTabWidget secondario
            sub_tab_widget = QTabWidget()
            profile_tab_layout.addWidget(sub_tab_widget)

            for attr in profile_data:
                if attr == 'Name':
                    continue
                value = getattr(profile_data, attr)

                # Creare un tab per ogni categoria
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)

                if isinstance(value, zeep.xsd.valueobjects.CompoundValue):
                    group_box = self.createGroupBox(attr)  # Usa attr come titolo del gruppo
                    group_layout = QVBoxLayout(group_box)

                    for sub_attr in value:
                        sub_value = getattr(value, sub_attr)
                        self.create_label_and_field(group_layout, sub_attr, sub_value)

                    group_box.setLayout(group_layout)
                    tab_layout.addWidget(group_box)
                else:
                    self.create_label_and_field(tab_layout, attr, value)

                tab.setLayout(tab_layout)
                sub_tab_widget.addTab(tab, attr)

            profile_tab.setLayout(profile_tab_layout)
            self.tab_widget.addTab(profile_tab, profile_name)

    def create_label_and_field(self, layout, key, value):
        row_layout = QHBoxLayout()
        label = QLabel(key)
        edit = QLineEdit(str(value))
        row_layout.addWidget(label)
        row_layout.addWidget(edit)
        layout.addLayout(row_layout)

    def createGroupBox(self, name):
        return QGroupBox(name)


# Test del Viewer
if __name__ == '__main__':
    app = QApplication([])
    credential = {
        "ip": "192.168.1.51",
        "port": 2000,
    }
    cam = onvifCam()
    cam.errorSignal.connect(print)
    cam.initCredential(credential)
    cam.connectCam()
    profile_data = cam.get_media_profiles()
    viewer = ProfileViewer(profile_data)
    viewer.show()
    app.exec()
