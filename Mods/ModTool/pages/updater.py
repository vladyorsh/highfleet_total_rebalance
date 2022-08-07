import os
from parsing import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal


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
        
