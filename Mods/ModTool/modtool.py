import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from parsing import *

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
        
    def validate(self):
        if self.root is None or not os.path.exists(self.root):
            return 'The root dir does not exist.'
        
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
                
        return retval
        
    def log(self, * args, ** kwargs):
        str_ = ' '.join([ str(arg) for arg in args ])
        self.text_box.append(str_)

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
        
        self.update_text_fields()
        
    def update_text_fields(self):
        self.root_text.setText(self.app_state.root)
        self.OL_text.setText(self.app_state.OL_path)
        self.parts_text.setText(self.app_state.parts_path)
        self.vanilla_OL_text.setText(self.app_state.vanilla_OL_path)
        
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
        
class RenameDialog(QDialog):
    '''Dialog for renaming ships, subclassed to return a custom state info'''
    signal = pyqtSignal(int)

    def __init__(self, ship_name, parent=None):
        super(RenameDialog, self).__init__(parent)
        
        self.setWindowTitle(f'Rename ship: {ship_name}')

        QBtn = QDialogButtonBox.Apply | QDialogButtonBox.Discard | QDialogButtonBox.Cancel
        
        #https://stackoverflow.com/questions/71335524/return-clicked-button-id-instead-of-accept-reject-flags-on-qdialog-pyqt5
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(lambda: self.customSlot(QDialogButtonBox.Apply))
        self.buttonBox.button(QDialogButtonBox.Discard).clicked.connect(lambda: self.customSlot(QDialogButtonBox.Discard))
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(lambda: self.customSlot(QDialogButtonBox.Cancel))

        self.signal.connect(self.done)
        
        self.layout = QVBoxLayout()
        message = QLabel('Enter a new ship name')
        self.name_widget = QLineEdit()
        self.name_widget.setText(ship_name)

        self.layout.addWidget(message)
        self.layout.addWidget(self.name_widget)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def customSlot(self, button_id):
        # emit button's id
        self.signal.emit(button_id)
        
    def execute(self):
        ans = self.exec_()
        if ans == QMessageBox.Apply:
            return True, self.name_widget.text()
        elif ans == QMessageBox.Discard:
            return False, 'discard'
        elif ans == QMessageBox.Cancel:
            return False, 'cancel'
        else:
            return False, 'error'


class UpdaterPage(QWidget):
    '''A tab for ship updater/renamer'''
    def __init__(self, app_state):
        super(UpdaterPage, self).__init__()
        
        self.app_state = app_state
        self.source_path = None
        self.target_path = None
        
        self.source_widget = QLineEdit()
        self.source_widget.setReadOnly(True)
        self.source_button = QPushButton("Open source dir...")
        self.source_button.clicked.connect(self.get_source_path)
        
        self.target_widget = QLineEdit()
        self.target_widget.setReadOnly(True)
        self.target_button = QPushButton("Open target dir...")
        self.target_button.clicked.connect(self.get_target_path)
        
        self.source_list = QListWidget()
        self.target_list = QListWidget()
        self.source_list.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        self.target_list.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        self.source_list.setSortingEnabled(True)
        self.target_list.setSortingEnabled(True)
        
        self.sel_button  = QPushButton('>')
        self.sel_all_button = QPushButton('>>')
        self.desel_button = QPushButton('<')
        self.desel_all_button = QPushButton('<<')
        self.sel_button.clicked.connect(self.move_right)
        self.sel_all_button.clicked.connect(self.move_right_all)
        self.desel_button.clicked.connect(self.move_left)
        self.desel_all_button.clicked.connect(self.move_left_all)
        
        self.button_stack = QVBoxLayout()
        [ self.button_stack.addWidget(w) for w in [ self.sel_button, self.desel_button, self.sel_all_button, self.desel_all_button ] ]
        
        self.selection_stack = QHBoxLayout()
        self.selection_stack.addWidget(self.source_list)
        self.selection_stack.addLayout(self.button_stack)
        self.selection_stack.addWidget(self.target_list)
        
        self.how_to_label = QLabel('How to update:\n\
        1. Select source and target dirs;\n\
        2. Hit the Update button;\n\
        3. Back up your Ships folder;\n\
        4. Move partially updated ships there;\n\
        5. Open Config.ini;\n\
        6. Change the game version to 1.14;\n\
        7. Launch the game and quit;\n\
        Now ships are fully updated.')
        self.update_button = QPushButton('Update')
        self.update_button.clicked.connect(self.update)
        self.rename_button = QPushButton('Rename')
        self.rename_button.clicked.connect(self.rename)
        
        self.update_layout = QVBoxLayout()
        self.update_layout.addWidget(self.how_to_label)
        self.update_layout.addWidget(self.update_button)
        self.update_layout.addWidget(self.rename_button)
        
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.source_widget, 0, 0)
        layout.addWidget(self.target_widget, 1, 0)
        layout.addWidget(self.source_button, 0, 1)
        layout.addWidget(self.target_button, 1, 1)
        
        layout.addLayout(self.selection_stack, 2, 0)
        layout.addLayout(self.update_layout, 2, 1)
                        
        
    def update(self):
        if self.target_path is None or not self.target_list.count():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Select an appropriate target directory and at least one ship.")
            msg.setWindowTitle("No target directory")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return
        
        msg = 'This will write partially updated copies of the selected ships to the destination directory. Files in the target directory with the identical names will be overwritten. Proceed?'
        
        answer = QMessageBox.question(self, 'Update ships?', msg, QMessageBox.Yes, QMessageBox.No)
        
        if answer == QMessageBox.Yes:
            try:
                OL_lib = OL.from_file(self.app_state.OL_path)
                vanilla_OL_lib = OL.from_file(self.app_state.vanilla_OL_path) if self.app_state.vanilla_OL_path is not None else None
                parts_lib = Parts.from_file(self.app_state.parts_path)
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText('Cannot update ships: error while reading .seria libraries. Ensure that you have set correct paths to them.')
                msg.exec_()
                return
            
            if vanilla_OL_lib is None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText('Vanilla OL.seria file is missing. Sensor/EWAR stats will not be updated.')
                msg.exec_()
            
            for idx in range(self.target_list.count()):
                item = self.target_list.item(idx).text()
                self.app_state.log(f'Updating {item}')
                path = os.path.join(self.source_path, item)
                out_path = os.path.join(self.target_path, item)
                
                ship = Ship.from_file(path, self.app_state)
                
                try:
                    ship.recompute_stats(OL_lib, vanilla_OL_lib, parts_lib, logger=self.app_state, verbose=True)
                    ship.write(out_path, logger=self.app_state)
                except:
                    try:
                        self.app_state.log('Cannot update global stats, recomputing local only.')
                        ship = Ship.from_file(path, logger=self.app_state)
                        ship.update_modules(parts_lib, OL_lib, vanilla_OL_lib)
                        ship.write(out_path, logger=self.app_state)
                    except:
                        self.app_state.log('Cannot update')
                        self.app_state.log('---------------------------')
                self.app_state.log('')
        else:
            pass
                
    def rename(self):
        if self.target_path is None or not self.target_list.count():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Select an appropriate target directory and at least one ship.")
            msg.setWindowTitle("No target directory")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return
                
        msg = 'This will write renamed copies of the selected ships to the destination directory. Files in the target directory with the identical names will be overwritten. Proceed?'
            
        answer = QMessageBox.question(self, 'Rename ships?', msg, QMessageBox.Yes, QMessageBox.No)
        if answer == QMessageBox.Yes:
            for idx in range(self.target_list.count()):
                item = self.target_list.item(idx).text()
                path = os.path.join(self.source_path, item)
                
                ship = Ship.from_file(path)
                old_name = ship.m_name
                do_rename, state = RenameDialog(old_name, self).execute()
                
                if do_rename:
                    if state.endswith('.seria'): state = state[:-6]
                    ship.rename(state)
                    output_path = os.path.join(self.target_path, state + '.seria')
                    ship.write(output_path)
                elif state == 'discard':
                    pass
                elif state == 'cancel' or 'error':
                    break
                else:
                    raise ValueError(f'Undefined state on ship rename {do_rename}, {state}')
        else:
            pass
        
    def move_right(self):
        selection = self.source_list.selectedItems()
        if not selection: return        
        for item in selection:
            self.source_list.takeItem(self.source_list.row(item))
            self.target_list.addItem(item)
            
    def move_left(self):
        selection = self.target_list.selectedItems()
        if not selection: return        
        for item in selection:
            self.target_list.takeItem(self.target_list.row(item))
            self.source_list.addItem(item)
            
    def move_right_all(self):
        while self.source_list.count():
            item = self.source_list.item(0)
            self.source_list.takeItem(0)
            self.target_list.addItem(item)
    
    def move_left_all(self):
        while self.target_list.count():
            item = self.target_list.item(0)
            self.target_list.takeItem(0)
            self.source_list.addItem(item)
        
    def get_source_path(self):
        self.source_path = QFileDialog.getExistingDirectory(self, 'Select source ships folder', os.path.join(self.app_state.root, 'Objects/Designs'))
        self.source_widget.setText(self.source_path)
        
        self.source_list.clear()
        self.target_list.clear()
        
        for item in os.listdir(self.source_path):
            if item.endswith('.seria'):
                self.source_list.addItem(item)
            
    def get_target_path(self):
        self.target_path = QFileDialog.getExistingDirectory(self, 'Select target ships folder', self.app_state.root)
        self.target_widget.setText(self.target_path)
        
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
        self.app_state.text_box = self.logs
        
        self.setup_page = SettingsPage(self.app_state)
        self.ship_updater_page = UpdaterPage(self.app_state)
        
        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(self.setup_page, "Settings")
        self.tabwidget.addTab(self.ship_updater_page, "Ship Updater")
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