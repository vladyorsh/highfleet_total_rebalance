class ShipEntry(object):
    def __init__(self, ship_names, difficulties=['easy', 'normal', 'hard'], spawn_chance=1.0):
        self.names = ship_names
        self.difficulties = difficulties
        self.spawn_chance = spawn_chance

STRIKE_GROUPS = {
'default'	: [
    ShipEntry([ 'Gryphon' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry(['Tarantul ARM'], ['hard']),
],
0			: {
    ShipEntry([ 'Gryphon' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry(['Tarantul ARM'], ['hard']),
},
1			: [
    ShipEntry([ 'Gryphon' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry(['Tarantul ARM'], ['hard']),
],
2			: [
    ShipEntry([ 'Gryphon' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry(['Tarantul ARM'], ['hard']),
],
3			: [
    ShipEntry([ 'Nomad' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
],
4			: [
    ShipEntry([ 'Nomad' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
],
5			: [
    ShipEntry([ 'Nomad' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
    ShipEntry([ 'Gryphon', 'Borey', 'Kormoran', 'Negev' ]),
],
}