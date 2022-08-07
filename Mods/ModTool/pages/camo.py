import os
from PyQt5.QtWidgets import *
from parsing import *

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
