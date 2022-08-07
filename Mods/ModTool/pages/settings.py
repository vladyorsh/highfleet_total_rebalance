import os
from PyQt5.QtWidgets import *

class SettingsPage(QWidget):
    def __init__(self, app_state):
        super(SettingsPage, self).__init__()
        self.app_state = app_state
            
        self.root_text = QLineEdit()
        self.root_text.setReadOnly(True)
        self.root_button = QPushButton('Open root dir...')
        self.root_button.clicked.connect(self.set_root)
        
        self.OL_text = QLineEdit()
        self.OL_text.setReadOnly(True)
        self.OL_button = QPushButton('Open OL.seria...')
        self.OL_button.clicked.connect(self.set_OL)
        
        self.parts_text = QLineEdit()
        self.parts_text.setReadOnly(True)
        self.parts_button = QPushButton('Open parts.seria...')
        self.parts_button.clicked.connect(self.set_parts)
        
        self.vanilla_OL_text = QLineEdit()
        self.vanilla_OL_text.setReadOnly(True)
        self.vanilla_OL_button = QPushButton('Open vanilla OL.seria...')
        self.vanilla_OL_button.clicked.connect(self.set_vanilla_OL)
        
        self.localization_text = QLineEdit()
        self.localization_text.setReadOnly(True)
        
        self.localization_button = QPushButton('Open localization .seria_enc...')
        self.localization_button.clicked.connect(self.set_localization)
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        layout.addWidget(self.root_text, 0, 0)
        layout.addWidget(self.root_button, 0, 1)
        layout.addWidget(self.OL_text, 1, 0)
        layout.addWidget(self.OL_button, 1, 1)
        layout.addWidget(self.parts_text, 2, 0)
        layout.addWidget(self.parts_button, 2, 1)
        layout.addWidget(self.vanilla_OL_text, 3, 0)
        layout.addWidget(self.vanilla_OL_button, 3, 1)
        layout.addWidget(self.localization_text, 4, 0)
        layout.addWidget(self.localization_button, 4, 1)
        
        self.update_text_fields()
        
    def update_text_fields(self):
        self.root_text.setText(self.app_state.root)
        self.OL_text.setText(self.app_state.OL_path)
        self.parts_text.setText(self.app_state.parts_path)
        self.vanilla_OL_text.setText(self.app_state.vanilla_OL_path)
        self.localization_text.setText(self.app_state.localization_path)
        
    def set_root(self):
        self.app_state.root = QFileDialog.getExistingDirectory(self, 'Select game directory', 'D:\Games\Steam\steamapps\common\HighFleet')
        validation_failed = app_state.validate()
        self.update_text_fields()
        
        if validation_failed:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Cannot validate the game directory.')
            msg.setInformativeText('\n'.join(validation_failed))
            msg.setWindowTitle('Validation Failed')
            msg.exec_()
            
    def set_OL(self):
        self.app_state.OL_path, _ = QFileDialog.getOpenFileName(self, 'Select OL.seria', self.app_state.root)
        self.update_text_fields()
            
    def set_parts(self):
        self.app_state.parts_path, _= QFileDialog.getOpenFileName(self, 'Select parts.seria', self.app_state.root)
        self.update_text_fields()
    
    def set_vanilla_OL(self):
        self.app_state.vanilla_OL_path, _ = QFileDialog.getOpenFileName(self, 'Select original OL.seria', self.app_state.root)
        self.update_text_fields()
        
    def set_localization(self):
        self.app_state.localization_path, _ = QFileDialog.getOpenFileName(self, 'Select localization file *.seria_enc', os.path.join(self.app_state.root, 'Data/Dialogs'))
        self.update_text_fields()
        