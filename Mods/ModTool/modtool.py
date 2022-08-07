import sys
import math
import random
from PyQt5.QtCore import *

from pages.settings import *
from pages.updater import *
from pages.map import *
from pages.camo import *
from pages.auto_save import *

class AppState:
    '''Holds the application options, such as paths to different key files. Is shared between different application pages.'''
    def __init__(self, root, text_box):
        self.text_box = text_box
        
        #Mandatory to be in the game dir
        self.root = root
        self.OL_path = None
        self.parts_path = None
        
        #Additional files
        self.vanilla_OL_path = None
        self.sg_config_path = None
        self.localization_path = None
        
    def validate(self):
        if self.root is None or not os.path.exists(self.root):
            return [ 'The root dir does not exist.' ]
        
        retval = []
        if not os.path.exists(os.path.join(self.root, 'Highfleet.exe')):
            retval.append('Cannot find Highfleet.exe, check if you pointed to the right root directory.')
        
        OL_path = os.path.join(self.root, 'Libraries/OL.seria')
        if not os.path.exists(OL_path):
            retval.append('Cannot find OL.seria.')
            self.OL_path = None
        else:
            self.OL_path = OL_path
        
        parts_path = os.path.join(self.root, 'Libraries/parts.seria')
        if not os.path.exists(parts_path):
            retval.append('Cannot find parts.seria.')
            self.parts_path = None
        else:
            self.parts_path = parts_path
                
        localization_path = os.path.join(self.root, 'Data/Dialogs/english.seria_enc')
        if not os.path.exists(localization_path):
            retval.append('Cannot find english.seria_enc')
            self.localization_path = None
        else:
            self.localization_path = localization_path
                
        return retval
        
    def log(self, * args, ** kwargs):
        str_ = ' '.join([ str(arg) for arg in args ])
        self.text_box.append(str_)

class MainWindow(QWidget):
    '''The main window which hauls several modding tools on its tabs'''
    def __init__(self, app_state):
        super(MainWindow, self).__init__()
        self.app_state = app_state
        
        layout = QGridLayout()
        self.setLayout(layout)
        self.setWindowTitle('HF Mod Tool')
        
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setMaximumHeight(96)
        self.app_state.text_box = self.logs
        
        self.setup_page = SettingsPage(self.app_state)
        self.ship_updater_page = UpdaterPage(self.app_state)
        self.map_viewer_page = MapViewerPage(self.app_state)
        self.auto_updater = AutoSaveUpdater(self.app_state)
        self.camo_switch_page= CamoSwitchPage(self.app_state)
        
        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(self.setup_page, "Settings")
        self.tabwidget.addTab(self.ship_updater_page, "Ship Updater")
        self.tabwidget.addTab(self.map_viewer_page, "Map Viewer")
        self.tabwidget.addTab(self.auto_updater, "Save Updater")
        self.tabwidget.addTab(self.camo_switch_page, "Camo Switch")
        
        layout.addWidget(self.tabwidget, 0, 0)
        layout.addWidget(self.logs, 1, 0)

class WelcomeWindow(QWidget):
    '''Initial prompt to open the game folder'''
    def __init__(self):
        super(WelcomeWindow, self).__init__()
        
        layout = QGridLayout()
        self.setLayout(layout)
        self.setWindowTitle('HF Mod Tool')
        
        self.path_widget = QLineEdit()
        self.path_widget.setReadOnly(True)
        
        self.button_widget = QPushButton("Open HF directory...")
        self.button_widget.clicked.connect(self.get_path)
        
        
        layout.addWidget(QLabel('Set the HighFleet root directory to proceed.'), 0, 0)
        layout.addWidget(self.path_widget, 1, 0)
        layout.addWidget(self.button_widget, 1, 1)
        
    def get_path(self):
        self.root = QFileDialog.getExistingDirectory(self, 'Select game directory', 'D:\Games\Steam\steamapps\common\HighFleet')
        self.path_widget.setText(self.root)
        
        app_state = AppState(self.root, None)
        validation_failed = app_state.validate()
        
        if validation_failed:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Cannot validate the game directory.')
            msg.setInformativeText('\n'.join(validation_failed))
            msg.setWindowTitle('Validation Failed')
            msg.exec_()
        else:
            self.hide()
            self.main_window = MainWindow(app_state)
            self.main_window.show()
    
def main():
    random.seed()
    app = QApplication(sys.argv)

    screen = WelcomeWindow()
    screen.show()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()
        
#TODO: Build app state with validation
#TODO: Validate version
#TODO: Rename/update prompt icons
#TODO: Rename dialog icons
#TODO: Rename dialog buttons
#TODO: Display craft files when choosing source/dest dirs
#TODO: Better error types
#TODO: Remove ? in dialogs
#TODO: Message on no ships selected on update/rename
#TODO: Check state validation before update
#TODO: Log renaming
#TODO: Dots at message ends
#TODO: Utils descriptions
#TODO: Better updater worker with progress display
#TODO: Map resizing widgets
#TODO: Endgame spawn marks
#TODO: Parse launcher groups
#TODO: 2000km radius around Khiva
#TODO: Scale slider
#TODO: Escadra preview speed and range
#TODO: Text edit masks
#TODO: Check for possible PROFILE@No bugs
#TODO: Default output path with profile.seria
#TODO: Fix "cannot open save" message (path)
        
#classname, code, id, master_id, m_name
#children (generatae owner)
#position, alignment, target, role, inventory