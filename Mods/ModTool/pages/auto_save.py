import os
import math
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from parsing import *

class Roles:
    Player = 0
    Convoy = 1
    Garrison = 2
    Strike = 5
    
    NAMES = {
        Player : 'Player',
        Convoy : 'Convoy',
        Garrison : 'Garrison',
        Strike : 'Strike Group',
    }

class Location:
    def __init__(self, name, pos_x, pos_y, radius_min, radius_max, sector_min, sector_max, is_city):
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.radius_min = radius_min
        self.radius_max = radius_max
        self.sector_min = sector_min
        self.sector_max = sector_max
        self.is_city = is_city
        
class ShipEntry:
    def __init__(self, ship_names, difficulties=['easy', 'normal', 'hard'], spawn_chance=1.0):
        self.names = ship_names
        self.difficulties = difficulties
        self.spawn_chance = spawn_chance
        
    def __repr__(self):
        s = '['
        symb = { 'easy' : 'E', 'normal' : 'N', 'hard' : 'H' }
        s += ', '.join([symb[d] for d in self.difficulties])
        s += '] '
        
        s += ', '.join(self.names)
        s += ' x ' + str(self.spawn_chance)
        
        return s
        
    def __str__(self):
        return repr(self)
        
class Fleet:
    def __init__(self, name, ship_entries):
        self.name = name
        self.ship_entries = ship_entries
            
    def roll(self, difficulty):
        valid_ships = [ ship for ship in self.ship_entries if difficulty in ship.difficulties ]
        filtered_ships = [ ship for ship in valid_ships is random.random() <= ship.spawn_chance() ]
        sampled_ships = [ random.choice(ship.names) for ship in filtered_ships ]
        
        return sampled_ships
        
    def __repr__(self):
        s = self.name + '\n'
        s += '\n'.join([ str(e) for e in self.ship_entries ])
        
        return s
    
    def __str__(self):
        return repr(self)
    
class NewEscadraEntryDialog(QDialog):
    def __init__(self, app_state, role, location_item, fleet_item, locations_list, fleets_list):
        super(NewEscadraEntryDialog, self).__init__()
        
        self.app_state = app_state
        self.locations_list = locations_list
        self.fleets_list = fleets_list
        
        self.setWindowTitle('Edit entry')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.role_widget = QComboBox()
        self.roles = [Roles.NAMES[Roles.Garrison], Roles.NAMES[Roles.Convoy], Roles.NAMES[Roles.Strike]]
        self.role_ids = [ Roles.Garrison, Roles.Convoy, Roles.Strike ]
        self.role_widget.addItems(self.roles)
        
        if role in self.role_ids:
            self.role_widget.setCurrentIndex(self.role_ids.index(role))
                
        self.fleet_widget = QComboBox()
        self.fleet_names = [ fleet.fleet.name for fleet in fleets_list ]
        self.fleet_widget.addItems(self.fleet_names)
        
        if fleet_item is not None and fleet_item.fleet.name in self.fleet_names:
            self.fleet_widget.setCurrentIndex(self.fleet_names.index(fleet_item.fleet.name))
                
        self.loc_widget = QComboBox()
        self.loc_names  = [ loc.location.name for loc in locations_list ]
        self.loc_widget.addItems(self.loc_names)
        
        if location_item is not None and location_item.location.name in self.loc_names:
            self.loc_widget.setCurrentIndex(self.loc_names.index(location_item.location.name))
                
        layout = QGridLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel(text='Role:'), 0, 0)
        layout.addWidget(self.role_widget, 0, 1)
        layout.addWidget(QLabel(text='Fleet:'), 1, 0)
        layout.addWidget(self.fleet_widget, 1, 1)
        layout.addWidget(QLabel(text='Location:'), 2, 0)
        layout.addWidget(self.loc_widget, 2, 1)
        layout.addWidget(self.buttonBox, 3, 1)
        
                
    def extract_choice(self):
        role = self.role_ids[self.role_widget.currentIndex()]
        fleet= self.fleets_list[self.fleet_widget.currentIndex()].fleet
        loc  = self.locations_list[self.loc_widget.currentIndex()].location
        
        return role, fleet, loc
        
class ModifyEscadraDialog(QDialog):
    def __init__(self, app_state, role, current_index, remove_fleet_item, add_fleet_item, fleets_list):
        super(ModifyEscadraDialog, self).__init__()
        
        self.app_state = app_state
        self.fleets_list = fleets_list
        
        self.setWindowTitle('Edit entry')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.role_widget = QComboBox()
        self.roles = [Roles.NAMES[Roles.Garrison], Roles.NAMES[Roles.Convoy], Roles.NAMES[Roles.Strike]]
        self.role_ids = [ Roles.Garrison, Roles.Convoy, Roles.Strike ]
        self.role_widget.addItems(self.roles)
        
        if role in self.role_ids:
            self.role_widget.setCurrentIndex(self.role_ids.index(role))
        
        self.fleet_names = [ fleet.fleet.name for fleet in fleets_list ]
                
        self.remove_fleet_widget = QComboBox()
        self.remove_fleet_widget.addItems(self.fleet_names)
        
        self.add_fleet_widget = QComboBox()
        self.add_fleet_widget.addItems(self.fleet_names)
        
        if remove_fleet_item is not None and remove_fleet_item.fleet.name in self.fleet_names:
            self.remove_fleet_widget.setCurrentIndex(self.fleet_names.index(remove_fleet_item.fleet.name))
                
        if add_fleet_item is not None and add_fleet_item.fleet.name in self.fleet_names:
            self.add_fleet_widget.setCurrentIndex(self.fleet_names.index(add_fleet_item.fleet.name))
        
        self.index_widget = QSpinBox()
        self.index_widget.setMinimum(0)
        
        if isinstance(current_index, int) and current_index >= 0:
            self.index_widget.setValue(current_index)
                
        layout = QGridLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel(text='Role:'), 0, 0)
        layout.addWidget(self.role_widget, 0, 1)
        layout.addWidget(QLabel(text='Remove fleet:'), 1, 0)
        layout.addWidget(self.remove_fleet_widget, 1, 1)
        layout.addWidget(QLabel(text='Add fleet:'), 2, 0)
        layout.addWidget(self.add_fleet_widget, 2, 1)
        layout.addWidget(QLabel(text='Index:'), 3, 0)
        layout.addWidget(self.index_widget, 3, 1)
        layout.addWidget(self.buttonBox, 4, 1)
    
    def extract_choice(self):
        role = self.role_ids[self.role_widget.currentIndex()]
        remove_fleet= self.fleets_list[self.remove_fleet_widget.currentIndex()].fleet
        add_fleet = self.fleets_list[self.add_fleet_widget.currentIndex()].fleet
        idx  = self.index_widget.value()
        
        return role, remove_fleet, add_fleet, idx
        
class NewFleetDialog(QDialog):
        
    class NewEntryDialog(QDialog):
        def __init__(self, app_state):
            super(NewFleetDialog.NewEntryDialog, self).__init__()
            
            self.app_state = app_state
            self.setWindowTitle('New entry')
            QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            self.buttonBox = QDialogButtonBox(QBtn)
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)
            
            self.easy = QCheckBox(text='Easy')
            self.normal = QCheckBox(text='Normal')
            self.hard = QCheckBox(text='Hard')
            
            self.easy.setChecked(True)
            self.normal.setChecked(True)
            self.hard.setChecked(True)
            
            self.diff_layout = QVBoxLayout()
            self.diff_layout.addWidget(self.easy)
            self.diff_layout.addWidget(self.normal)
            self.diff_layout.addWidget(self.hard)
            
            self.source_list = QListWidget()
            self.target_list = QListWidget()
            
            self.init_list()
            
            self.add_button = QPushButton('>')
            self.del_button = QPushButton('<')
            self.del_all_button = QPushButton('<<')
            
            self.manip_box = QVBoxLayout()
            self.manip_box.addWidget(self.add_button)
            self.manip_box.addWidget(self.del_button)
            self.manip_box.addWidget(self.del_all_button)
            
            self.list_layout = QHBoxLayout()
            self.list_layout.addWidget(self.source_list)
            self.list_layout.addLayout(self.manip_box)
            self.list_layout.addWidget(self.target_list)
            
            self.add_button.clicked.connect(self.move_right)
            self.del_button.clicked.connect(self.move_left)
            self.del_all_button.clicked.connect(self.move_left_all)
            
            self.chance = QDoubleSpinBox()
            self.chance.setMinimum(0)
            self.chance.setMaximum(1)
            self.chance.setSingleStep(0.01)
            self.chance.setValue(1.0)
            
            self.chance_layout = QHBoxLayout()
            self.chance_layout.addWidget(QLabel(text='Spawn chance:'))
            self.chance_layout.addWidget(self.chance)
            
            layout = QVBoxLayout()
            self.setLayout(layout)
            layout.addLayout(self.chance_layout)
            layout.addLayout(self.diff_layout)
            layout.addLayout(self.list_layout)
            layout.addWidget(self.buttonBox)
            
            
        def init_list(self):
            names = os.listdir(os.path.join(self.app_state.root, 'Objects/Designs')) + os.listdir(os.path.join(self.app_state.root, 'Ships'))
            for name in names:
                if name.endswith('.seria'):
                    self.source_list.addItem(name)
                        
        def move_right(self):
            selection = self.source_list.selectedItems()
            for item in selection:
                self.target_list.addItem(item.text())
                
        def move_left(self):
            selection = self.target_list.selectedItems()
            for item in selection:
                self.target_list.takeItem(self.target_list.row(item))
                
        def move_left_all(self):
            while self.target_list.count():
                item = self.target_list.item(0)
                self.target_list.takeItem(0)
        
        def extract_choice(self):
            ship_names = [ self.target_list.item(i).text() for i in range(self.target_list.count()) ]
            difficulties = []
            if self.easy.isChecked():
                difficulties.append('easy')
            if self.normal.isChecked():
                difficulties.append('normal')
            if self.hard.isChecked():
                difficulties.append('hard')
                    
            spawn_chance = self.chance.value()
            
            return ShipEntry(ship_names, difficulties, spawn_chance)
                
    def __init__(self, app_state):
        super(NewFleetDialog, self).__init__()
            
        self.app_state = app_state
            
        self.setWindowTitle('New fleet')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.name_field = QLineEdit(text='New Fleet')
        
        self.new_entry_button = QPushButton('New ship entry')
        self.del_entry_button = QPushButton('Remove entry')
        
        self.new_entry_button.clicked.connect(self.add_entry)
        self.del_entry_button.clicked.connect(self.del_entry)
        
        self.edit_layout = QVBoxLayout()
        self.edit_layout.addWidget(self.new_entry_button)
        self.edit_layout.addWidget(self.del_entry_button)
        
        self.entries_list = QListWidget()
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel(text='Name:'), 0, 0)
        layout.addWidget(self.name_field, 0, 1)
        layout.addLayout(self.edit_layout, 1, 0)
        layout.addWidget(self.entries_list, 1, 1)
        layout.addWidget(self.buttonBox, 2, 1)
        
    def add_entry(self):
        dlg = NewFleetDialog.NewEntryDialog(self.app_state)
        retval = dlg.exec_()
        if retval == QDialog.Accepted:
            entry = dlg.extract_choice()
            item = QListWidgetItem(str(entry))
            item.entry = entry
            self.entries_list.addItem(item)
        else:
            pass
            
    def del_entry(self):
        for item in self.entries_list.selectedItems():
            self.entries_list.takeItem(self.entries_list.row(item))
        
    def extract_choice(self):
        entries = [ self.entries_list.item(i).entry for i in range(self.entries_list.count()) ]
        name = self.name_field.text()
        
        return Fleet(name, entries)
        
class NewLocDialog(QDialog):
    def __init__(self, app_state):
        super(NewLocDialog, self).__init__()
        self.app_state = app_state
        
        self.setWindowTitle('New location')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        
        
class AutoSaveUpdater(QWidget):
    '''Page allowing to edit and apply simple scripts which edit/add new escadras in a randomized way'''
        
    def __init__(self, app_state):
        super(AutoSaveUpdater, self).__init__()
            
        self.app_state = app_state
        
        self.custom_locations = None
        self.custom_fleets = None
        
        #Table of new enemies
        self.add_table = QTableWidget()
        self.add_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.add_table.setColumnCount(3)
        self.add_table.setHorizontalHeaderLabels(['Role', 'Ref. Location', 'Ship List'])
        
        self.add_table_add_button = QPushButton('Add')
        self.add_table_remove_button = QPushButton('Remove')
        self.add_table_change_button = QPushButton('Change')
        self.add_table_add_button.clicked.connect(self.add_table_add)
        self.add_table_remove_button.clicked.connect(self.table_remove(self.add_table))
        self.add_table_change_button.clicked.connect(self.add_table_change)
        
        
        self.add_table_button_box = QVBoxLayout()
        self.add_table_button_box.addWidget(self.add_table_add_button)
        self.add_table_button_box.addWidget(self.add_table_change_button)
        self.add_table_button_box.addWidget(self.add_table_remove_button)
        
        self.add_table_layout = QHBoxLayout()
        self.add_table_layout.addWidget(self.add_table)
        self.add_table_layout.addLayout(self.add_table_button_box)
        
        #Table of enemy modifications
        self.modify_table = QTableWidget()
        self.modify_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.modify_table.setColumnCount(4)
        self.modify_table.setHorizontalHeaderLabels(['Role', 'Index', 'Remove List', 'Add List'])
        
        self.modify_table_add_button = QPushButton('Add')
        self.modify_table_change_button = QPushButton('Change')
        self.modify_table_remove_button = QPushButton('Remove')
        self.modify_table_add_button.clicked.connect(self.modify_table_add)
        self.modify_table_change_button.clicked.connect(self.modify_table_change)
        self.modify_table_remove_button.clicked.connect(self.table_remove(self.modify_table))
        
        self.modify_table_button_box = QVBoxLayout()
        self.modify_table_button_box.addWidget(self.modify_table_add_button)
        self.modify_table_button_box.addWidget(self.modify_table_change_button)
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
        
        self.default_compositions = set()
        self.init_compositions()
        
        self.compositions_add_button.clicked.connect(self.add_composition)
        self.compositions_remove_button.clicked.connect(self.list_remove(self.compositions_list, self.default_compositions))
        
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
        
        self.default_locations = set()
        self.init_locations()
        
        self.locations_remove_button.clicked.connect(self.list_remove(self.locations_list, self.default_locations))
        
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
        text = f'Location: {loc.name}, is city: {loc.is_city}\nX: {loc.pos_x}, Y: {loc.pos_y}\nBand: {loc.radius_min}–{loc.radius_max}\nSector: {loc.sector_min}-{loc.sector_max}'
        self.info_label.setText(text)

    def display_fleet(self):
        fleet = self.compositions_list.currentItem().fleet
        text = 'Composition: ' + str(fleet)
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
        
        self.default_compositions |= { 'Default', 'SG0', 'SG1', 'SG2', 'SG3', 'SG4', 'SG5', 'SG_END', 'LAUNCHER' } 
            
        DEFAULT.fleet = Fleet('Default',
        [
        ShipEntry([ 'Gryphon' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry(['Tarantul ARM'], ['hard']),
        ])
        
        SG0.fleet = Fleet('SG0',
        [
        ShipEntry([ 'Gryphon' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry(['Tarantul ARM'], ['hard']),
        ])
        
        SG1.fleet = Fleet('SG1',
        [
        ShipEntry([ 'Gryphon' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry(['Tarantul ARM'], ['hard']),
        ])
        
        SG2.fleet = Fleet('SG2',
        [
        ShipEntry([ 'Gryphon' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry(['Tarantul ARM'], ['hard']),
        ])
        
        SG3.fleet = Fleet('SG3',
        [
        ShipEntry([ 'Nomad' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        SG4.fleet = Fleet('SG4',
        [
        ShipEntry([ 'Nomad' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        SG5.fleet = Fleet('SG5',
        [
        ShipEntry([ 'Nomad' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        SG_END.fleet = Fleet('SG_END',
        [
        ShipEntry([ 'Nomad' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
        ])
        
        LAUNCHER.fleet = Fleet('LAUNCHER',
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
        UR.location = Location('UR', None, None, 0, 0, 0.0, 2 * math.pi, True)
        
        KHIVA = QListWidgetItem('KHIVA')
        KHIVA.location = Location('KHIVA', None, None, 0, 0, 0.0, 2 * math.pi, True)
        
        self.default_locations |= { 'UR', 'KHIVA' }
            
        self.locations_list.addItem(UR)
        self.locations_list.addItem(KHIVA)
        
    def add_table_add(self):
        locations = [ self.locations_list.item(i) for i in range(self.locations_list.count()) ]
        compositions = [ self.compositions_list.item(i) for i in range(self.compositions_list.count()) ]
        dialog = NewEscadraEntryDialog(self.app_state, None, None, None, locations, compositions)
        retval = dialog.exec_()
        if retval == QDialog.Accepted:
            row = self.add_table.rowCount()
            role, fleet, location = dialog.extract_choice()
            
            self.add_table.insertRow(row)
            
            role_item = QTableWidgetItem(Roles.NAMES[role])
            role_item.role = role
            
            loc_item = QTableWidgetItem(location.name)
            loc_item.location = location
            
            fleet_item = QTableWidgetItem(fleet.name)
            fleet_item.fleet = fleet
            
            self.add_table.setItem(row, 0, role_item)
            self.add_table.setItem(row, 1, loc_item)
            self.add_table.setItem(row, 2, fleet_item)
        else:
            pass
                
    def add_table_change(self):
        locations = [ self.locations_list.item(i) for i in range(self.locations_list.count()) ]
        compositions = [ self.compositions_list.item(i) for i in range(self.compositions_list.count()) ]
        
        row = self.add_table.currentRow()
        if row < 0:
            return
        role, location, fleet = self.add_table.item(row, 0).role, self.add_table.item(row, 1), self.add_table.item(row, 2)
        dialog = NewEscadraEntryDialog(self.app_state, role, location, fleet, locations, compositions)
        retval = dialog.exec_()
        if retval == QDialog.Accepted:
            role, fleet, location = dialog.extract_choice()
            
            role_item = QTableWidgetItem(Roles.NAMES[role])
            role_item.role = role
            
            loc_item = QTableWidgetItem(location.name)
            loc_item.location = location
            
            fleet_item = QTableWidgetItem(fleet.name)
            fleet_item.fleet = fleet
            
            self.add_table.setItem(row, 0, role_item)
            self.add_table.setItem(row, 1, loc_item)
            self.add_table.setItem(row, 2, fleet_item)
        else:
            pass
        
    def modify_table_add(self):
        compositions = [ self.compositions_list.item(i) for i in range(self.compositions_list.count()) ]
        
        dialog = ModifyEscadraDialog(self.app_state, None, None, None, None, compositions)
        retval = dialog.exec_()
        if retval == QDialog.Accepted:
            row = self.modify_table.rowCount()
            role, remove, add, index = dialog.extract_choice()
            
            self.modify_table.insertRow(row)
            
            role_item = QTableWidgetItem(Roles.NAMES[role])
            role_item.role = role
            
            remove_fleet_item = QTableWidgetItem(remove.name)
            remove_fleet_item.fleet = remove
            
            add_fleet_item = QTableWidgetItem(add.name)
            add_fleet_item.fleet = add
            
            index_item = QTableWidgetItem(str(index))
            
            self.modify_table.setItem(row, 0, role_item)
            self.modify_table.setItem(row, 1, index_item)
            self.modify_table.setItem(row, 2, remove_fleet_item)
            self.modify_table.setItem(row, 3, add_fleet_item)
        else:
            pass
        
    def modify_table_change(self):
        compositions = [ self.compositions_list.item(i) for i in range(self.compositions_list.count()) ]
        
        row = self.modify_table.currentRow()
        if row < 0:
            return
        role, index, remove_fleet, add_fleet = [ self.modify_table.item(row, i) for i in range(4) ]
        role, index = role.role, int(index.text())
        
        dialog = ModifyEscadraDialog(self.app_state, role, index, remove_fleet, add_fleet, compositions)
        retval = dialog.exec_()
        if retval == QDialog.Accepted:
            role, remove, add, index = dialog.extract_choice()
            
            role_item = QTableWidgetItem(Roles.NAMES[role])
            role_item.role = role
            
            remove_fleet_item = QTableWidgetItem(remove.name)
            remove_fleet_item.fleet = remove
            
            add_fleet_item = QTableWidgetItem(add.name)
            add_fleet_item.fleet = add
            
            index_item = QTableWidgetItem(str(index))
            
            self.modify_table.setItem(row, 0, role_item)
            self.modify_table.setItem(row, 1, index_item)
            self.modify_table.setItem(row, 2, remove_fleet_item)
            self.modify_table.setItem(row, 3, add_fleet_item)
        else:
            pass
        
    def add_composition(self):
        dlg = NewFleetDialog(self.app_state)
        retval = dlg.exec_()
        if retval == QDialog.Accepted:
            fleet = dlg.extract_choice()
            item = QListWidgetItem(fleet.name)
            item.fleet = fleet
            self.compositions_list.addItem(item)
        else:
            pass
                
    def table_remove(self, table):
        def remove_row():
            table.removeRow(table.currentRow())
        return remove_row
        
    def list_remove(self, list, defaults):
        def remove_row():
            for item in list.selectedItems():
                if item.text() not in defaults:
                    list.takeItem(list.row(item))
        return remove_row