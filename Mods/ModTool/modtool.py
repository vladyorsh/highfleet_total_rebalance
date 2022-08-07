import sys
import os
import math
import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from parsing import *
from tools import *

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
        
        
class MapWidget(QWidget):
    '''The key widget for displaying the map or manipulating escadras'''
    clicked = pyqtSignal()
    
    def __init__(self, width, height, scale=1.0, city_scale=1.0):
        super(MapWidget, self).__init__()
        
        self.save = None
        self.locations= None
        self.escadras = None
        
        self.city_scale = city_scale
        self.scale = scale
        self.selection_range=50 #50px
        
        self.mouse_clicked_x = -1
        self.mouse_clicked_y = -1
        
        self.mouse_x = -1
        self.mouse_y = -1
        
        self.resize(width, height)
        self.setMouseTracking(True)
        self.update()
        
    def set_save(self, save):
        self.save = save
        self.locations = save.get_children_by_name('m_locations')
        self.escadras  = save.get_children_by_name('m_escadras')
        self.update()
        
    def selection_radius(self):
        return self.selection_range * 10 / self.scale
    
    def find_escadras_in_region(self, x, y, radius):
        x, y = self.unmap_coords(x, y)
        chosen_escadras = []
        if self.escadras is not None:
            for escadra in self.escadras:
                e_x, e_y = getattr(escadra, 'm_position.x', 0.0), getattr(escadra, 'm_position.y', 0.0)
                distance = ((x - e_x) ** 2 + (y - e_y) ** 2) ** (1/2)
                if distance < radius:
                    chosen_escadras.append(escadra)
        return chosen_escadras
        
    def mouseMoveEvent(self, event):
        self.mouse_x, self.mouse_y = event.x(), event.y()
        self.update()
        
    def map_coords(self, x, y):
        x = self.width()  / 2 + x * self.scale / 10
        y = self.height() / 2 + y * self.scale / 10
        
        return int(x), int(y)
        
    def unmap_coords(self, x, y):
        x = (x - self.width()  / 2) / self.scale * 10
        y = (y - self.height() / 2) / self.scale * 10
        
        return x, y
        
    def diamond_poly(self, x, y, side):
        poly = QPolygon()
        side = side / 2 * (2 ** 1/2)
        side = int(side)
        poly.append(QPoint(x - side, y))
        poly.append(QPoint(x, y - side))
        poly.append(QPoint(x + side, y))
        poly.append(QPoint(x, y + side))
        
        return poly
    
    def triangle_poly(self, x, y, side, rotated=False):
        radius = side * (3 ** 1/2)/3
        big_shift = int(radius * math.sin(math.pi/3))
        small_shift = int(radius * math.sin(math.pi/6))
        poly = QPolygon()
        if not rotated:
            poly.append(QPoint(x - big_shift, y + small_shift))
            poly.append(QPoint(x + big_shift, y + small_shift))
            poly.append(QPoint(x, y - big_shift))
        else:
            poly.append(QPoint(x - big_shift, y - small_shift))
            poly.append(QPoint(x + big_shift, y - small_shift))
            poly.append(QPoint(x, y + big_shift))
        
        return poly
        
    def paintEvent(self, event):
        
        painter = QPainter(self)
        background = QRect(0, 0, self.width(), self.height())
        painter.fillRect(background, QBrush(QColor(119, 144, 148)))
        
        if self.locations is not None:
            for location in self.locations:
                x = getattr(location, 'm_position.x', 0)
                y = getattr(location, 'm_position.y', 0)
                size = int(location.m_citysize * self.city_scale * self.scale / 500)
                
                pen_thickness = max(1, int(self.scale))
                large_font = int(8 * self.scale)
                small_font = int(6 * self.scale)
                offset = int(10 * self.scale)
                
                x, y = self.map_coords(x, y)
                painter.setPen(QPen(QColor(255, 255, 255), pen_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawEllipse(QPoint(x, y), size, size)
                
                painter.setFont(QFont("Verdana", large_font ))
                painter.drawText(QPoint(x + offset, y), location.m_name)
                painter.setFont(QFont("Verdana", small_font))
                painter.drawText(QPoint(x + offset, y + offset), location.m_codename)
                
                if hasattr(location, 'm_quest'):
                    pen_thickness = max(1, int(2 * self.scale))
                    half_side = int(8 * self.scale)
                    very_large_font = int(10 * self.scale)
                    offset = int(4 * self.scale)
                        
                    painter.setPen(QPen(QColor(255, 255, 0), pen_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    rect = QRect(x - half_side, y - half_side, 2 * half_side, 2 * half_side)
                    painter.setFont(QFont("Verdana", very_large_font))
                    painter.drawText(QPoint(x - offset, y + offset), '?')
                    painter.drawRect(rect)
        
        if self.escadras is not None:     
            for escadra in self.escadras:
                x = getattr(escadra, 'm_position.x', 0)
                y = getattr(escadra, 'm_position.y', 0)
                x, y = self.map_coords(x, y)
                
                side = int(10 * self.scale)
                half_side = int(side / 2)
                pen_thickness = max(1, int(2 * self.scale))
                small_font = int(6 * self.scale)
                offset = int(15 * self.scale)
                
                if getattr(escadra, 'm_role', 0) == 5: #Strike group
                    rect = QRect(x - half_side, y - half_side, side, side)
                    painter.setPen(QPen(QColor(255, 0, 0), pen_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.drawRect(rect)
                    painter.setFont(QFont("Verdana", small_font))
                    painter.drawText(QPoint(x - 2 * offset, y + offset), escadra.m_name)
                elif getattr(escadra, 'm_role', 0) == 1: #Convoy
                    poly = self.triangle_poly(x, y, side, rotated=True)
                    painter.setPen(QPen(QColor(0, 123, 0), pen_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.drawPolygon(poly)
                    painter.setFont(QFont("Verdana", small_font))
                    painter.drawText(QPoint(x - offset, y - offset // 2), escadra.m_name)
                elif getattr(escadra, 'm_role', 0) == 2: #Garrison
                    AG = False
                    MG = False
                    
                    stats = [ ship.find_by_attr('m_code', 47)[0] for ship in escadra.get_children_by_name('m_children') ]
                    
                    for stat in stats:
                        if getattr(stat, 'm_tele_crafts', 0) > 0: AG = True
                        if getattr(stat, 'm_tele_nukes', 0) > 0: MG =  True
                    
                    if AG:
                        poly = self.diamond_poly(x, y, side)
                        painter.setPen(QPen(QColor(255, 0, 0), pen_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                        painter.drawPolygon(poly)
                        painter.setFont(QFont("Verdana", small_font))
                        painter.drawText(QPoint(x + offset // 2, y - offset // 2), escadra.m_name)
                    if MG:
                        poly = self.triangle_poly(x, y, side)
                        painter.setPen(QPen(QColor(255, 0, 0), pen_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                        painter.drawPolygon(poly)
                        painter.setFont(QFont("Verdana", small_font))
                        painter.drawText(QPoint(x + offset // 2, y - offset // 2), escadra.m_name)
                    
        if self.mouse_x != -1:
        
            coord_x, coord_y = self.unmap_coords(self.mouse_x, self.mouse_y)
            pen_thickness = max(1, int(1 * self.scale))
            small_font = int(6 * self.scale)
            
            painter.setFont(QFont("Verdana", small_font))
            painter.setPen(QPen(QColor(255, 255, 255), pen_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))    
            painter.drawText(QPoint(self.mouse_x, self.mouse_y), f'{coord_x:.1f}, {coord_y:.1f}')
       
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.press_pos = event.pos()
            
    def mouseReleaseEvent(self, event):
        
        if (self.press_pos is not None and 
            event.button() == Qt.LeftButton and 
            event.pos() in self.rect()):
                self.clicked.emit()
                self.mouse_clicked_x, self.mouse_clicked_y = event.x(), event.y()
        self.press_pos = None

class NewEscadraDialog(QDialog):
    
    def __init__(self, app_state, map_widget):
        super(NewEscadraDialog, self).__init__()
        
        self.map_widget = map_widget
        self.app_state = app_state
            
        self.setWindowTitle('Add new escadra')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.m_name_widget = QLineEdit(text='DERBENT')
        
        x, y = map_widget.unmap_coords(map_widget.mouse_clicked_x, map_widget.mouse_clicked_y)
        
        self.m_position_x_widget = QLineEdit(text=str(x))
        self.m_position_y_widget = QLineEdit(text=str(y))
        
        self.target_pos_x_widget = QLineEdit(text=str(x))
        self.target_pos_y_widget = QLineEdit(text=str(y))
        
        self.role_widget = QComboBox()
        
        self.roles = ['Garrison', 'Convoy', 'Strike Group']
        self.role_ids = [ 2, 1, 5 ]
        
        self.role_widget.addItems(self.roles)
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        self.annot = QLabel(text='Callsign may be any, but it\'s recommended to pick an existing callsign unused by escadras of the same role. No spaces, numbers or special symbols allowed.')
        self.annot.setWordWrap(True)
        layout.addWidget(self.annot, 0, 1)
        
        layout.addWidget(QLabel(text='Callsign:'), 1, 0)
        layout.addWidget(self.m_name_widget, 1, 1)
        
        layout.addWidget(QLabel(text='Role:'), 2, 0)
        layout.addWidget(self.role_widget, 2, 1)
        
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(self.m_position_x_widget)
        pos_layout.addWidget(self.m_position_y_widget)
        
        layout.addWidget(QLabel(text='Pos:'), 3, 0)
        layout.addLayout(pos_layout, 3, 1)
        
        tgt_layout = QHBoxLayout()
        tgt_layout.addWidget(self.target_pos_x_widget)
        tgt_layout.addWidget(self.target_pos_y_widget)
        
        layout.addWidget(QLabel(text='Tgt:'), 4, 0)
        layout.addLayout(tgt_layout, 4, 1)
        
        ships_available = [ ship for ship in os.listdir(os.path.join(app_state.root, 'Objects/Designs')) if ship.endswith('.seria') ]
        ships_available+= [ ship for ship in os.listdir(os.path.join(app_state.root, 'Ships')) if ship.endswith('.seria') ]
        
        self.sel_button  = QPushButton('>')
        self.desel_button = QPushButton('<')
        self.sel_button.clicked.connect(self.select_ships)
        self.desel_button.clicked.connect(self.deselect_ships)
        self.sel_layout = QVBoxLayout()
        self.sel_layout.addWidget(self.sel_button)
        self.sel_layout.addWidget(self.desel_button)
        
        self.menu_available = QListWidget()
        self.menu_chosen = QListWidget()
        [ self.menu_available.addItem(ship) for ship in ships_available ]
        self.menu_available.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        self.menu_available.setSortingEnabled(True)
        self.menu_chosen.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        self.menu_chosen.setSortingEnabled(True)
        
        self.ship_selection_layout = QHBoxLayout()
        self.ship_selection_layout.addWidget(self.menu_available)
        self.ship_selection_layout.addLayout(self.sel_layout)
        self.ship_selection_layout.addWidget(self.menu_chosen)
        
        layout.addWidget(QLabel(text='Select ships:'), 5, 0)
        layout.addLayout(self.ship_selection_layout, 5, 1)
        
        layout.addWidget(self.buttonBox, 6, 1)
    
    def select_ships(self):
        selection = self.menu_available.selectedItems()
        for item in selection:
            self.menu_chosen.addItem(item.text())
                
    def deselect_ships(self):
        selection = self.menu_chosen.selectedItems()
        for item in selection:
            self.menu_chosen.takeItem(self.menu_chosen.row(item))
                
    def extract_escadra(self):
        #Init escadra with utility vars
        escadra = Node()
        escadra.set('m_classname', 'Escadra')
        escadra.set('m_code', 327)
        escadra.set('m_id', generate_id())
        escadra.set('m_name', self.m_name_widget.text())
        
        #Add compacted ship representations
        for i in range(self.menu_chosen.count()):
            ship = self.menu_chosen.item(i).text()
            
            vanilla_path = os.path.join(os.path.join(self.app_state.root, 'Objects/Designs'), ship)
            ships_path = os.path.join(os.path.join(self.app_state.root, 'Ships'), ship)
                
            if os.path.exists(vanilla_path):
                ship = Ship.from_file(vanilla_path)
            elif os.path.exists(ships_path):
                ship = Ship.from_file(ships_path)
            else:
                raise FileNotFoundError(f'Cannot find ship file {ship} in Objects/Designs or Ships folders.')
            
            ship = get_compacted_ship_repr(ship, escadra.m_id, i + 1)
        
            escadra.output_order.append((('m_children', 7), ship))
        
        #Define escadra type and initial behavior
        escadra.set('m_position.x', float(self.m_position_x_widget.text()))
        escadra.set('m_position.y', float(self.m_position_y_widget.text()))
        escadra.set('m_alignment', -1)
        escadra.set('m_target_pos.x', float(self.target_pos_x_widget.text()))
        escadra.set('m_target_pos.y', float(self.target_pos_y_widget.text()))
        role = self.role_ids[self.role_widget.currentIndex()]
        escadra.set('m_role', role)
        
        inventory = Node()
        inventory.set('m_classname', 'Node')
        inventory.set('m_code', 7)
        inventory.set('m_id', generate_id())
        
        escadra.output_order.append((('m_inventory', 7), inventory))
        
        #Make an intel node so an escadra will have a name on a map
        intel = Node()
        intel.set('m_classname', 'Intel')
        intel.set('m_code', 515)
        intel.set('m_mark.id', generate_id())
        #Unknown vars
        intel.set('m_age', 0)
        intel.set('m_age_max', 28800)
        intel.set('m_type', 8)
        #Known vars
        intel.set('m_name', escadra.m_name)
        intel.set('m_position.x', getattr(escadra, 'm_position.x'))
        intel.set('m_position.y', getattr(escadra, 'm_position.y'))
        #Unknown vars
        intel.set('m_rad_encrypted', 'true')
        intel.set('m_size', 2)
        
        escadra.output_order.append((('m_intels', 515), intel))
        
        return escadra
        
class DelEscadraDialog(QDialog):
    def __init__(self, escadra):
        super(DelEscadraDialog, self).__init__()
        
        self.setWindowTitle('Delete escadra')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.label = QLabel(text=f'Delete escadra {escadra.m_name}?')
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.label)
        layout.addWidget(self.buttonBox)
        
class EditEscadraDialog(QDialog):
    def __init__(self, app_state, escadra):
        super(EditEscadraDialog, self).__init__()
        
        self.app_state = app_state
            
        self.setWindowTitle('Edit escadra')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.m_name_widget = QLineEdit(text=escadra.m_name)
        
        x, y = getattr(escadra, 'm_position.x', 0.0), getattr(escadra, 'm_position.y', 0.0)
        
        self.m_position_x_widget = QLineEdit(text=str(x))
        self.m_position_y_widget = QLineEdit(text=str(y))
        
        x, y = getattr(escadra, 'm_target_pos.x', 0.0), getattr(escadra, 'm_target_pos.y', 0.0)
        
        self.target_pos_x_widget = QLineEdit(text=str(x))
        self.target_pos_y_widget = QLineEdit(text=str(y))
        
        self.role_widget = QComboBox()
        
        self.roles = ['Garrison', 'Convoy', 'Strike Group']
        self.role_ids = [ 2, 1, 5]
        role = getattr(escadra, 'm_role', 0)
        if role == 0:
            self.role_widget.addItems(['Player'])
            self.role_widget.setEnabled(False)
        else:
            self.role_widget.addItems(self.roles)
            self.role_widget.setCurrentIndex(self.role_ids.index(role))
        
                
        layout = QGridLayout()
        self.setLayout(layout)
        
        self.annot = QLabel(text='Edit escadra parameters. Ship names beginning with "*" denote ships already present in the escadra.')
        self.annot.setWordWrap(True)
        layout.addWidget(self.annot, 0, 1)
        
        layout.addWidget(QLabel(text='Callsign:'), 1, 0)
        layout.addWidget(self.m_name_widget, 1, 1)
        
        layout.addWidget(QLabel(text='Role:'), 2, 0)
        layout.addWidget(self.role_widget, 2, 1)
        
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(self.m_position_x_widget)
        pos_layout.addWidget(self.m_position_y_widget)
        
        layout.addWidget(QLabel(text='Pos:'), 3, 0)
        layout.addLayout(pos_layout, 3, 1)
        
        tgt_layout = QHBoxLayout()
        tgt_layout.addWidget(self.target_pos_x_widget)
        tgt_layout.addWidget(self.target_pos_y_widget)
        
        layout.addWidget(QLabel(text='Tgt:'), 4, 0)
        layout.addLayout(tgt_layout, 4, 1)
        
        #Make available new ships, move old ships from left to right and preserve them if not deleted
        base_ships = [ ship for ship in os.listdir(os.path.join(app_state.root, 'Objects/Designs')) if ship.endswith('.seria') ]
        base_ships+= [ ship for ship in os.listdir(os.path.join(app_state.root, 'Ships')) if ship.endswith('.seria') ]
        
        self.sel_button  = QPushButton('>')
        self.desel_button = QPushButton('<')
        self.sel_button.clicked.connect(self.select_ships)
        self.desel_button.clicked.connect(self.deselect_ships)
        self.sel_layout = QVBoxLayout()
        self.sel_layout.addWidget(self.sel_button)
        self.sel_layout.addWidget(self.desel_button)
        
        self.menu_available = QListWidget()
        self.menu_chosen = QListWidget()
        [ self.menu_available.addItem(ship) for ship in base_ships ]
        self.menu_available.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        self.menu_available.setSortingEnabled(True)
        self.menu_chosen.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        self.menu_chosen.setSortingEnabled(True)
        
        escadra_ships = [ item for item in escadra.output_order if isinstance(item, tuple) and item[0][0] == 'm_children' ]
        for ship in escadra_ships:
            item = QListWidgetItem('*' + ship[1].m_name)
            item.ship = ship
            self.menu_chosen.addItem(item)
        
        self.ship_selection_layout = QHBoxLayout()
        self.ship_selection_layout.addWidget(self.menu_available)
        self.ship_selection_layout.addLayout(self.sel_layout)
        self.ship_selection_layout.addWidget(self.menu_chosen)
        
        layout.addWidget(QLabel(text='Select ships:'), 5, 0)
        layout.addLayout(self.ship_selection_layout, 5, 1)
        
        layout.addWidget(self.buttonBox, 6, 1)
        
    def select_ships(self):
        #If ship is base (no .ship attr) -> add without removal
        #Else move right
        selection = self.menu_available.selectedItems()
        for item in selection:
            new_item = QListWidgetItem(item.text())
            if hasattr(item, 'ship'):
                new_item.ship = item.ship
                self.menu_available.takeItem(self.menu_available.row(item))
            self.menu_chosen.addItem(new_item)
            
    def deselect_ships(self):
        selection = self.menu_chosen.selectedItems()
        #If ship is base (no. ship attr) -> remove completely
        #Else move left
        for item in selection:
            if hasattr(item, 'ship'):
                new_item = QListWidgetItem(item.text())
                new_item.ship = item.ship
                self.menu_available.addItem(new_item)
            self.menu_chosen.takeItem(self.menu_chosen.row(item))
        
    def modify_escadra(self, escadra):
        
        first_ship_index = 0
        for i, item in enumerate(escadra.output_order):
            if isinstance(item, tuple) and item[0][0] == 'm_children':
                first_ship_index = i
                break
        escadra.output_order = [ item for item in escadra.output_order if not isinstance(item, tuple) or item[0][0] != 'm_children' ]
        escadra.set('m_name', self.m_name_widget.text())
        
        ships = []
        
        #Add initial ships or compacted ship representations
        for i in range(self.menu_chosen.count()):
            ship = self.menu_chosen.item(i)
            if hasattr(ship, 'ship'):
                ship = ship.ship
                ship[1].find_by_attr('m_code', 47)[0].set('m_escadra_index', i + 1)
                ships.append(ship)
            else:
                ship = ship.text()
                vanilla_path = os.path.join(os.path.join(self.app_state.root, 'Objects/Designs'), ship)
                ships_path = os.path.join(os.path.join(self.app_state.root, 'Ships'), ship)
                    
                if os.path.exists(vanilla_path):
                    ship = Ship.from_file(vanilla_path)
                elif os.path.exists(ships_path):
                    ship = Ship.from_file(ships_path)
                else:
                    raise FileNotFoundError(f'Cannot find ship file {ship} in Objects/Designs or Ships folders.')
                
                ship = get_compacted_ship_repr(ship, escadra.m_id, i + 1)
            
                ships.append((('m_children', 7), ship))
        
        [ escadra.output_order.append(ship) for ship in ships ]
                
        #Define escadra type and initial behavior
        escadra.set('m_position.x', float(self.m_position_x_widget.text()))
        escadra.set('m_position.y', float(self.m_position_y_widget.text()))
        escadra.set('m_target_pos.x', float(self.target_pos_x_widget.text()))
        escadra.set('m_target_pos.y', float(self.target_pos_y_widget.text()))
        role = getattr(escadra, 'm_role', 0)
        if role != 0:
            role = self.role_ids[self.role_widget.currentIndex()]
            escadra.set('m_role', role)
        
        return escadra
        
class MapViewerPage(QWidget):
    def __init__(self, app_state):
        '''Tool page containing the map widget and buttons'''
        super(MapViewerPage, self).__init__()
        
        self.app_state = app_state
        
        self.save_path = None
        self.save_path_field = QLineEdit()
        self.save_path_field.setReadOnly(True)
        
        self.open_button = QPushButton('Open save...')
        self.open_button.clicked.connect(self.open_save)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(False)
        
        scale = 1.5
        map_width, map_height = int(1000 * scale), int(2500 * scale)
        
        self.map_widget = MapWidget(map_width, map_height, scale)
        self.map_widget.clicked.connect(self.map_click)
        self.scroll.setWidget(self.map_widget)
        
        self.chosen_enemy_list = QListWidget()
        self.chosen_enemy_list.setMaximumWidth(192)
        self.chosen_enemy_list.itemClicked.connect(self.display_escadra)
        self.chosen_escadras = None
        
        self.add_new_button = QPushButton('Add escadra...')
        self.add_new_button.clicked.connect(self.add_new)
        self.edit_button = QPushButton('Edit escadra...')
        self.edit_button.clicked.connect(self.edit_escadra)
        self.delete_button = QPushButton('Delete escadra...')
        self.delete_button.clicked.connect(self.delete_escadra)
        self.save_button = QPushButton('Export modified save...')
        self.save_button.clicked.connect(self.export_save)
        self.escadra_data = QTextEdit()
        self.escadra_data.setReadOnly(True)
        self.escadra_data.setMaximumWidth(192)
        
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.chosen_enemy_list)
        v_layout.addWidget(self.escadra_data)
        v_layout.addWidget(self.edit_button)
        v_layout.addWidget(self.delete_button)
        v_layout.addWidget(self.add_new_button)
        v_layout.addWidget(self.save_button)
        
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        layout.addWidget(self.save_path_field, 0, 0)
        layout.addWidget(self.open_button, 0, 1)
        layout.addWidget(self.scroll, 1, 0)
        layout.addLayout(v_layout, 1, 1)
        
        
    def open_save(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, 'Open save', os.path.join(self.app_state.root, 'Saves'))
            save = Node.from_file(path)
        except:
            self.app_state.log('Cannot open save:')
            self.app_state.log(path)
            return
        self.save_path_field.setText(path)
        self.map_widget.set_save(save)
    
    def escadra_preview_text(self, escadra):
        
        m_name = escadra.m_name
        ships = [ ship.m_name for ship in escadra.get_children_by_name('m_children') ]
        role = getattr(escadra, 'm_role', 0)
        crafts, nukes = 0, 0
        if role == 5:
            role = 'Strike Group'
        elif role == 1:
            role = 'Convoy'
        elif role == 2:
            role = 'Garrison'            
            AG = False
            MG = False
            stats = [ ship.find_by_attr('m_code', 47)[0] for ship in escadra.get_children_by_name('m_children') ]
                    
            for stat in stats:
                if getattr(stat, 'm_tele_crafts', 0) > 0:
                    AG = True
                    crafts += getattr(stat, 'm_tele_crafts', 0)
                if getattr(stat, 'm_tele_nukes', 0) > 0:
                    MG =  True
                    nukes += getattr(stat, 'm_tele_nukes', 0)
            if AG: role += ', Aircraft'
            if MG: role += ', Missile'
        elif role == 0:
            role = 'Player'
        else:
            role = 'None'
                
        loc_x, loc_y = getattr(escadra, 'm_position.x', 0.0), getattr(escadra, 'm_position.y', 0.0)
        target_x, target_y = getattr(escadra, 'm_target_pos.x', 0.0), getattr(escadra, 'm_target_pos.y', 0.0)
        
        speed, heading = getattr(escadra, 'm_velocity', 0.0), getattr(escadra, 'm_course', 0.0)
        
        #m_velocity=35.3369
        #m_course=2.34466
        #m_altitude=9000
        #m_signature=84.0257
        #m_signature_rd=5544.49
        #m_signature_ir=40
        #m_alignment=-1
        #m_reaction_time=385.85
        #m_alert=3.99972
        #m_rad_freq=95.652
        #m_rad_duration=1800
        
        str_ = m_name + '\n' 
        str_ += role + '\n'
        str_ += ', '.join(ships) + '\n'
        str_ += f'Pos: {loc_x}, {loc_y}\n'
        str_ += f'Tgt: {target_x}, {target_y}\n'
        str_ += f'Spd: {speed}, Hdg: {heading}'
        if nukes:
            str_ += f'Nukes: {nukes}\n'
        if crafts:
            str_ += f'Crafts: {crafts}\n'
        
        return str_
        
    def display_escadra(self):
        self.escadra_data.clear()
        idx = self.chosen_enemy_list.currentRow()
        escadra = self.chosen_enemy_list.item(idx).escadra
        self.escadra_data.setText(escadra.output())
        self.app_state.log(self.escadra_preview_text(escadra))
        
    def map_click(self):
        self.chosen_enemy_list.clear()
        self.chosen_escadras = self.map_widget.find_escadras_in_region(self.map_widget.mouse_clicked_x, self.map_widget.mouse_clicked_y, self.map_widget.selection_radius())
        for escadra in self.chosen_escadras:
            item = QListWidgetItem(escadra.m_name)
            item.escadra = escadra
            self.chosen_enemy_list.addItem(item)
        
    def add_new(self):
        dialog = NewEscadraDialog(self.app_state, self.map_widget)
        retval = dialog.exec_()
        if retval == QDialog.Accepted:
            escadra = dialog.extract_escadra()
            self.map_widget.escadras.append(escadra)
            self.map_widget.update()
        else:
            pass
           
    def export_save(self):
        save = self.map_widget.save
        if save is None:
            return
        output_path, _ = QFileDialog.getSaveFileName(self, 'Export Save', self.app_state.root)
        if output_path is None or not output_path:
            return
        escadras = self.map_widget.escadras
        
        first_escadra_index = 0
        for i, item in enumerate(save.output_order):
            if isinstance(item, tuple) and item[0][0] == 'm_escadras':
                first_escadra_index = i
                break
                    
        save.output_order = [ item for item in save.output_order if not isinstance(item, tuple) or item[0][0] != 'm_escadras' ]
        save.output_order = save.output_order[:first_escadra_index] + [ (('m_escadras', 327), escadra) for escadra in escadras ] + save.output_order[first_escadra_index:]
        
        save.write(output_path)
        
    def edit_escadra(self):
        selection = self.chosen_enemy_list.currentItem()
        if selection is None or not selection:
            return
        escadra = selection.escadra
        dlg = EditEscadraDialog(self.app_state, escadra)
        retval = dlg.exec_()
        
        if retval == QDialog.Accepted:
            escadra = dlg.modify_escadra(escadra)
            self.map_widget.update()
        else:
            pass
            
    def delete_escadra(self):
        selection = self.chosen_enemy_list.currentItem()
        if selection is None or not selection:
            return
        escadra = selection.escadra
        retval = DelEscadraDialog(escadra).exec_()
        
        if retval == QDialog.Accepted:
            index = -1
            for i, e in enumerate(self.map_widget.escadras):
                if e.m_id == escadra.m_id:
                    index = i
                    break
            if index != -1:
                del self.map_widget.escadras[index]
                self.map_widget.update()
        else:
            pass
            

class CamoSwitchPage(QWidget):
    def __init__(self, app_state):
        super(CamoSwitchPage, self).__init__()
            
        self.app_state = app_state
        self.save = None
        
        self.garrisons = []
        self.convoys = []
        self.sgs = []
        self.playable = []
        
        self.save_path = None
        self.save_path_field = QLineEdit()
        self.save_path_field.setReadOnly(True)
        
        self.open_button = QPushButton('Open save...')
        self.open_button.clicked.connect(self.open_save)
        
        self.camo_list = QListWidget()
        self.find_camos()
        
        self.player_button = QPushButton('Apply on player ships')
        self.player_button.clicked.connect(self.apply_on_player_ships)
        self.garrisons_button = QPushButton('Apply on enemy garrisons')
        self.garrisons_button.clicked.connect(self.apply_on_garrisons)
        self.convoys_button = QPushButton('Apply on enemy convoys')
        self.convoys_button.clicked.connect(self.apply_on_convoys)
        self.sgs_button = QPushButton('Apply on enemy SGs')
        self.sgs_button.clicked.connect(self.apply_on_sgs)
        self.export_button = QPushButton('Export save')
        self.export_button.clicked.connect(self.export)
        
        button_box = QVBoxLayout()
        button_box.addWidget(self.player_button)
        button_box.addWidget(self.garrisons_button)
        button_box.addWidget(self.convoys_button)
        button_box.addWidget(self.sgs_button)
        button_box.addWidget(self.export_button)
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        layout.addWidget(self.save_path_field, 0, 0)
        layout.addWidget(self.open_button, 0, 1)
        layout.addWidget(self.camo_list, 1, 0)
        layout.addLayout(button_box, 1, 1)
        
        
    def open_save(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, 'Open save', os.path.join(self.app_state.root, 'Saves'))
            self.save = Node.from_file(path)
            for escadra in self.save.get_children_by_name('m_escadras'):
                role = getattr(escadra, 'm_role', 0)
                if role == 0:
                    self.playable.append(escadra)
                elif role == 1:
                    self.convoys.append(escadra)
                elif role == 2:
                    self.garrisons.append(escadra)
                elif role == 5:
                    self.sgs.append(escadra)
                else:
                    self.app_state.log(f'Unidentified role {role}, escadra {escadra.m_name} will not be considered.')
        except:
            self.app_state.log(f'Cannot open save: {path}')
            return
        self.save_path_field.setText(path)

    def find_camos(self):
        camos = [ item for item in os.listdir(os.path.join(self.app_state.root, 'Media/Tex')) if item.startswith('Ships1') and item.endswith('.res') ]
        camos = [ item.replace('.res', '').replace('Ships1_', '') for item in camos ]
        camos = [ item if item != 'Ships1' else 'Vanilla' for item in camos ]
        
        for camo in camos:
            self.camo_list.addItem(camo)
    
    def apply_on_role(self, role):
        if self.save is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("You need to open a save first to apply a camo.")
            msg.setWindowTitle("No save opened")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return
            
        camo = self.camo_list.currentItem().text()
        escadras = []
        msg = 'undefined'
        
        if role == 0:
            escadras = self.playable
            msg = 'player ships'
        elif role == 1:
            escadras = self.convoys
            msg = 'enemy convoys'
        elif role == 2:
            escadras = self.garrisons
            msg = 'enemy garrisons'
        elif role == 5:
            escadras = self.sgs
            msg = 'enemy strike groups'
        else:
            return
        
        for escadra in escadras: #TODO: Can be optimized if we store sprites immediately after opening a save
            sprites = escadra.get_subnodes_as_list()
            sprites = [ sprite for sprite in sprites if getattr(sprite, 'm_classname', '') == 'Sprite' ]
            
            for sprite in sprites:
                sprite_name = sprite.m_animation_name
                
                #Check if we already applied some camo
                for i in range(self.camo_list.count()):
                    c = self.camo_list.item(i).text()
                    if c == 'Vanilla':
                        continue
                    if sprite_name.endswith('_' + c):
                        sprite_name = sprite_name.replace('_' + c, '')
                        break
                
                if camo != 'Vanilla':
                    sprite_name = sprite_name + '_' + camo
                
                sprite.set('m_animation_name', sprite_name)
        
        self.app_state.log('Applied camo', camo, 'on', msg)
        
    def apply_on_convoys(self):
        self.apply_on_role(1)
    
    def apply_on_garrisons(self):
        self.apply_on_role(2)
    
    def apply_on_player_ships(self):
        self.apply_on_role(0)
    
    def apply_on_sgs(self):
        self.apply_on_role(5)
        
    def export(self):
        if self.save is None:
            return
        output_path, _ = QFileDialog.getSaveFileName(self, 'Export Save', self.app_state.root)
        if output_path is None or not output_path:
            return
        self.save.write(output_path)

        
class AutoSaveUpdater(QWidget):
    '''Page allowing to edit and apply simple scripts which edit/add new escadras in a randomized way'''
    
    class Location:
        def __init__(self, name, pos_x, pos_y, radius_min, radius_max, is_city):
            self.name = name
            self.pos_x = pos_x
            self.pos_y = pos_y
            self.radius_min = radius_min
            self.radius_max = radius_max
            self.is_city = is_city
            
    class ShipEntry(object):
        def __init__(self, ship_names, difficulties=['easy', 'normal', 'hard'], spawn_chance=1.0):
            self.names = ship_names
            self.difficulties = difficulties
            self.spawn_chance = spawn_chance
            
    class Fleet:
        def __init__(self, name, ship_entries):
            self.name = name
            self.ship_entries = ship_entries
                
        def roll(self, difficulty):
            valid_ships = [ ship for ship in self.ship_entries if difficulty in ship.difficulties ]
            filtered_ships = [ ship for ship in valid_ships is random.random() <= ship.spawn_chance() ]
            sampled_ships = [ random.choice(ship.names) for ship in filtered_ships ]
            
            return sampled_ships
        
    def __init__(self, app_state):
        super(AutoSaveUpdater, self).__init__()
            
        self.app_state = app_state
        
        self.custom_locations = None
        self.custom_fleets = None
        
        #Table of new enemies
        self.add_table = QTableWidget()
        self.add_table.setColumnCount(4)
        self.add_table.setHorizontalHeaderLabels(['Role', 'Ref. Location', 'Ship List'])
        
        self.add_table_add_button = QPushButton('Add')
        self.add_table_remove_button = QPushButton('Remove')
        self.add_table_add_button.clicked.connect(self.table_add(self.add_table))
        self.add_table_remove_button.clicked.connect(self.table_remove(self.add_table))
        
        
        self.add_table_button_box = QVBoxLayout()
        self.add_table_button_box.addWidget(self.add_table_add_button)
        self.add_table_button_box.addWidget(self.add_table_remove_button)
        
        self.add_table_layout = QHBoxLayout()
        self.add_table_layout.addWidget(self.add_table)
        self.add_table_layout.addLayout(self.add_table_button_box)
        
        #Table of enemy modifications
        self.modify_table = QTableWidget()
        self.modify_table.setColumnCount(4)
        self.modify_table.setHorizontalHeaderLabels(['Role', 'Index', 'Remove List', 'Add List'])
        
        self.modify_table_add_button = QPushButton('Add')
        self.modify_table_remove_button = QPushButton('Remove')
        self.modify_table_add_button.clicked.connect(self.table_add(self.modify_table))
        self.modify_table_remove_button.clicked.connect(self.table_remove(self.modify_table))
        
        self.modify_table_button_box = QVBoxLayout()
        self.modify_table_button_box.addWidget(self.modify_table_add_button)
        self.modify_table_button_box.addWidget(self.modify_table_remove_button)
        
        self.modify_table_layout = QHBoxLayout()
        self.modify_table_layout.addWidget(self.modify_table)
        self.modify_table_layout.addLayout(self.modify_table_button_box)
        
        #Compositions list
        self.compositions_list = QListWidget()
        self.compositions_list.itemClicked.connect(self.display_fleet)
            
        self.compositions_add_button = QPushButton('Add')
        self.compositions_remove_button = QPushButton('Remove')
        
        self.compositions_button_box = QVBoxLayout()
        self.compositions_button_box.addWidget(self.compositions_add_button)
        self.compositions_button_box.addWidget(self.compositions_remove_button)
        
        self.compositions_layout = QHBoxLayout()
        self.compositions_layout.addWidget(self.compositions_list)
        self.compositions_layout.addLayout(self.compositions_button_box)
        
        self.init_compositions()
        
        #Locations list
        self.locations_list = QListWidget()
        self.locations_list.itemClicked.connect(self.display_location)
            
        self.locations_add_button = QPushButton('Add')
        self.locations_remove_button = QPushButton('Remove')
        
        self.locations_button_box = QVBoxLayout()
        self.locations_button_box.addWidget(self.locations_add_button)
        self.locations_button_box.addWidget(self.locations_remove_button)
        
        self.locations_layout = QHBoxLayout()
        self.locations_layout.addWidget(self.locations_list)
        self.locations_layout.addLayout(self.locations_button_box)
        
        self.init_locations()
        
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        
        #Main buttons
        self.load_button  = QPushButton('Load config...')
        self.store_button = QPushButton('Save config...')
        self.apply_button = QPushButton('Select save and apply...')
        
        self.main_button_box = QVBoxLayout()
        self.main_button_box.addWidget(self.load_button)
        self.main_button_box.addWidget(self.store_button)
        self.main_button_box.addWidget(self.apply_button)
        
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addLayout(self.add_table_layout, 0, 0)
        layout.addLayout(self.modify_table_layout, 0, 1)
        layout.addLayout(self.compositions_layout, 1, 0)
        layout.addLayout(self.locations_layout, 1, 1)
        layout.addWidget(self.info_label, 2, 0)
        layout.addLayout(self.main_button_box, 2, 1)
        
    def display_location(self):
        loc = self.locations_list.currentItem().location
        text = f'Location: {loc.name}, is city: {loc.is_city}\nX: {loc.pos_x}, Y: {loc.pos_y}\nBand: {loc.radius_min}–{loc.radius_max}'
        self.info_label.setText(text)

    def display_fleet(self):
        fleet = self.compositions_list.currentItem().fleet
        
        text = f'Composition: {fleet.name}\n'
        for entry in fleet.ship_entries:
            difficulties = ', '.join(entry.difficulties)
            ship_names = ', '.join(entry.names)
            spawn_chance = entry.spawn_chance
            
            text += f'{difficulties}: {ship_names} x {spawn_chance}\n'
            
        self.info_label.setText(text)
        
    def open_save(self):
        path = None
        try:
            path, _ = QFileDialog.getOpenFileName(self, 'Open save', os.path.join(self.app_state.root, 'Saves'))
            save = Node.from_file(path)
            return save
        except:
            self.app_state.log('Cannot open save:')
            self.app_state.log(path)
            return
        
    def init_compositions(self):
        self.compositions_list.clear()
            
        #Initializing default fleets
            
        DEFAULT = QListWidgetItem('Default')
        SG0 = QListWidgetItem('SG0')
        SG1 = QListWidgetItem('SG1')
        SG2 = QListWidgetItem('SG2')
        SG3 = QListWidgetItem('SG3')
        SG4 = QListWidgetItem('SG4')
        SG5 = QListWidgetItem('SG5')
        SG_END = QListWidgetItem('SG_END')
        LAUNCHER = QListWidgetItem('LAUNCHER')
            
        DEFAULT.fleet = AutoSaveUpdater.Fleet('Default',
        [
        ShipEntry([ 'Gryphon' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry(['Tarantul ARM'], ['hard']),
        ])
        
        SG0.fleet = AutoSaveUpdater.Fleet('SG0',
        [
        ShipEntry([ 'Gryphon' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry(['Tarantul ARM'], ['hard']),
        ])
        
        SG1.fleet = AutoSaveUpdater.Fleet('SG1',
        [
        ShipEntry([ 'Gryphon' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry(['Tarantul ARM'], ['hard']),
        ])
        
        SG2.fleet = AutoSaveUpdater.Fleet('SG2',
        [
        ShipEntry([ 'Gryphon' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry(['Tarantul ARM'], ['hard']),
        ])
        
        SG3.fleet = AutoSaveUpdater.Fleet('SG3',
        [
        ShipEntry([ 'Nomad' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        SG4.fleet = AutoSaveUpdater.Fleet('SG4',
        [
        ShipEntry([ 'Nomad' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        SG5.fleet = AutoSaveUpdater.Fleet('SG5',
        [
        ShipEntry([ 'Nomad' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        SG_END.fleet = AutoSaveUpdater.Fleet('SG_END',
        [
        ShipEntry([ 'Nomad' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        LAUNCHER.fleet = AutoSaveUpdater.Fleet('LAUNCHER',
        [
        ShipEntry([ 'Typhon' ]), #Mandatory ship for a launcher group
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        self.compositions_list.addItem(DEFAULT)
        self.compositions_list.addItem(SG0)
        self.compositions_list.addItem(SG1)
        self.compositions_list.addItem(SG2)
        self.compositions_list.addItem(SG3)
        self.compositions_list.addItem(SG4)
        self.compositions_list.addItem(SG5)
        self.compositions_list.addItem(SG_END)
        self.compositions_list.addItem(LAUNCHER)
        
        
        
    def init_locations(self):
        self.locations_list.clear()
        
        UR = QListWidgetItem('UR')
        UR.location = AutoSaveUpdater.Location('UR', None, None, 0, 0, True)
        
        KHIVA = QListWidgetItem('KHIVA')
        KHIVA.location = AutoSaveUpdater.Location('KHIVA', None, None, 0, 0, True)
            
        self.locations_list.addItem(UR)
        self.locations_list.addItem(KHIVA)
        
    def table_add(self, table):
        def add_row():
            table.insertRow(table.rowCount())
        return add_row
        
    def table_remove(self, table):
        def remove_row():
            table.removeRow(table.currentRow())
        return remove_row

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