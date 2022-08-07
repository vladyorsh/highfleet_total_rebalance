import os
import math
from utils import *
from parsing import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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
            

