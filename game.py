# -*- coding: utf-8 -*-

# pip install -r requirements.txt

from astrobox.space_field import SpaceField
from stage_03_harvesters.driller import DrillerDrone
from drones import MyDrones
# from probe import KimDrone

NUMBER_OF_DRONES = 5

if __name__ == '__main__':
    scene = SpaceField(
        speed=5,
        asteroids_count=20,
    )
    team_1 = [MyDrones() for _ in range(NUMBER_OF_DRONES)]
    team_2 = [DrillerDrone() for _ in range(NUMBER_OF_DRONES)]
    scene.go()
