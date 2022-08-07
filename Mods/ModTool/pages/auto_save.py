import os
import math
from PyQt5.QtWidgets import *
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
        self.roles = [Roles.NAMES[Roles.Garrison], Roles.NAMES[Roles.Garrison], Roles.NAMES[Roles.Strike]]
        self.role_ids = [ Roles.Garrison, Roles.Convoy, Roles.Strike ]
        self.role_widget.addItems(self.roles)
        
        if role in self.roles:
            self.role_widget.setCurrentIndex(self.role_ids.index[role])
                
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
        
class AutoSaveUpdater(QWidget):
    '''Page allowing to edit and apply simple scripts which edit/add new escadras in a randomized way'''
    
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
        self.modify_table.setColumnCount(4)
        self.modify_table.setHorizontalHeaderLabels(['Role', 'Index', 'Remove List', 'Add List'])
        
        self.modify_table_add_button = QPushButton('Add')
        self.modify_table_remove_button = QPushButton('Remove')
        #self.modify_table_add_button.clicked.connect(self.modify_table_add)
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
        text = f'Location: {loc.name}, is city: {loc.is_city}\nX: {loc.pos_x}, Y: {loc.pos_y}\nBand: {loc.radius_min}–{loc.radius_max}\nSector: {loc.sector_min}-{loc.sector_max}'
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
        UR.location = AutoSaveUpdater.Location('UR', None, None, 0, 0, 0.0, 2 * math.pi, True)
        
        KHIVA = QListWidgetItem('KHIVA')
        KHIVA.location = AutoSaveUpdater.Location('KHIVA', None, None, 0, 0, 0.0, 2 * math.pi, True)
            
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
        raise NotImplementedError('New fleet entry change is not implemented yet')
        
    def table_remove(self, table):
        def remove_row():
            table.removeRow(table.currentRow())
        return remove_row