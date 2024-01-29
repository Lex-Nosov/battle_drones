# -*- coding: utf-8 -*-
from math import sqrt, sin, cos, degrees
from random import randint
from astrobox.core import Drone, MotherShip
from robogame_engine.geometry import Vector, Point


class GetSpaceFieldObjects:
    my_team = list()
    sorted_asteroids = list()
    objects_to_collect = list()

    def add_drone_my_team(self, drone):
        self.my_team.append(drone)

    def get_enemy_drones(self, unit):
        return [drone for drone in unit.scene.drones if drone not in self.my_team and drone.is_alive]

    @staticmethod
    def get_enemy_base(unit):
        return [base for base in unit.scene.motherships if base is not unit.my_mothership and base.is_alive]

    def get_all_objects_to_collect(self, unit):
        objects_to_collect = list()
        asteroids = [asteroid for asteroid in unit.asteroids if asteroid.payload > 0]
        objects_to_collect.extend(asteroids)
        base = [base for base in unit.scene.motherships if
                base is not unit.my_mothership and not base.is_alive and base.payload > 0]
        objects_to_collect.extend(base)
        drones = [drone for drone in unit.scene.drones if
                  drone not in unit.data.my_team and drone.payload > 0 and not drone.is_alive]
        objects_to_collect.extend(drones)
        return objects_to_collect

    def sorting_all_objects(self, unit):
        self.objects_to_collect.clear()
        distance = dict()
        if self.get_all_objects_to_collect(unit):

            for obj in self.get_all_objects_to_collect(unit):
                distance[obj] = int(unit.distance_to(obj))

            sorted_objects = sorted(distance.items(), key=lambda item: item[1])

            for obj in sorted_objects:
                self.objects_to_collect.append(obj[0])

    def choice_near_objects_to_collect(self, unit):
        if not self.get_all_objects_to_collect(unit) or unit.is_full:
            return unit.my_mothership
        else:
            unit.data.sorting_all_objects(unit)
            return self.objects_to_collect[0]

    def search_for_enemies_in_radius(self, unit):
        for enemy in sorted(self.get_enemy_drones(unit), key=lambda x: x.distance_to(unit)):
            if (sqrt((enemy.coord.x - unit.coord.x) ** 2 + (enemy.coord.y - unit.coord.y) ** 2) <= 600) \
                    and enemy.is_alive:
                return enemy


class Transporter:
    current_targets = []

    def choice_target_for_drone(self, unit):
        self.current_targets.clear()
        for target in unit.data.my_team.target:
            self.current_targets.extend(target)

    def move_to(self, unit, target):
        unit.move_at(target)

    def action(self, unit, target):
        self.move_to(unit, target)
        if isinstance(unit.target, MotherShip):
            unit.unload_to(target)
        else:
            unit.load_from(target)


class Shooting:

    @staticmethod
    def check_friendly_fire(unit, target):
        vector_to_target = Vector(target.x - unit.x,
                                  target.y - unit.y)
        null_vector = Vector(600 - unit.x, unit.y - unit.y)
        len_vector_to_target = vector_to_target.module
        len_null_vector = null_vector.module
        normalize_vector_to_target = Vector((vector_to_target.x / len_vector_to_target) ** 2, (
                vector_to_target.y / len_vector_to_target) ** 2)
        normalize_null_vector = Vector((null_vector.x / len_null_vector) ** 2, (null_vector.y / len_null_vector) ** 2)
        scalar = normalize_null_vector.x * normalize_vector_to_target.x + normalize_null_vector.y * normalize_vector_to_target.y
        angle = degrees(cos(scalar))
        for my_drone in unit.data.my_team:
            if my_drone is not unit:
                RADIUS_DRONE = 50
                for unit_radius in range(580):
                    x = unit.coord.x + unit_radius * cos(angle)
                    y = unit.coord.y + unit_radius * sin(angle)
                    if Point(x, y).distance_to(my_drone) <= RADIUS_DRONE and my_drone.is_alive:
                        return True

    def shoot(self, target, unit):
        dist = sqrt((unit.x - target.x) ** 2 + (unit.y - target.y) ** 2)
        time = dist / 5
        x = unit.x + 5 * time
        y = unit.y + 5 * time
        point = Point(x, y)
        unit.turn_to(target)
        unit.gun.shot(target)


class Hunter:

    def regroup(self, unit):
        damaged = []
        for friend in unit.team:
            if friend.meter_2 < 0.7:
                damaged.extend(friend)
            if len(damaged) >= 2:
                pass

    def search_new_place_for_attack(self, unit, target):
        vector_to_target = Vector(unit.coord.x - target.coord.x, unit.coord.y - target.coord.y)
        len_vector_to_target = vector_to_target.module
        normalize_vector_to_target = Vector((vector_to_target.x / len_vector_to_target) ** 2, (
                vector_to_target.y / len_vector_to_target) ** 2)
        vector_gun_range = normalize_vector_to_target * 550
        point_to_attack = Point(target.x - vector_gun_range.x, target.y - vector_gun_range.y)
        return point_to_attack
        # for dist in range(max(int(unit.distance_to(target)), 580), 200, -50):
        #     for angle in range(15):
        #         vector_gun_range = normalize_vector_to_target * dist
        #         dice = randint(-5, 6)
        #         vector_gun_range.rotate(dice * 5)
        #         point_to_attack = Point(target.x - vector_gun_range.x, target.y - vector_gun_range.y)
        #         # print(point_to_attack)
        #         # if not unit.shoot.check_friendly_fire(unit, target):
        #         return point_to_attack

    def action(self, unit, target):
        if unit.distance_to(target) > 580:
            point = self.search_new_place_for_attack(target=target, unit=unit)
            unit.move_at(point)
            # unit.shoot.shoot(target=target, unit=unit)
        else:
            if unit.shoot.check_friendly_fire(unit, target):
                unit.shoot.shoot(target=target, unit=unit)


class Turel:

    def go_to_point(self, unit, target):
        distance_from_base = 300
        step_deviation = -17.5
        vector = Vector(unit.scene.field[0] / 2 - unit.my_mothership.coord.x,
                        unit.scene.field[1] / 2 - unit.my_mothership.coord.y)
        vector.rotate(35)
        vector_len = vector.module
        vector_norm = Vector(vector.x / vector_len, vector.y / vector_len)
        final_vector = vector_norm * distance_from_base
        final_vector.rotate(step_deviation * (unit.id - 1))
        point = Point(final_vector.x, final_vector.y)
        unit.move_at(point)

    def action(self, unit, target):
        if unit.near(unit.my_mothership):
            self.go_to_point(unit, target)
        else:
            unit.shoot.shoot(target, unit)


class Healing:

    def action(self, unit, target):
        unit.move_at(unit.my_mothership)


class MyDrones(Drone):
    full_load = 0
    not_full_load = 0
    empty_load = 0

    def __init__(self):
        super().__init__()
        self.data = GetSpaceFieldObjects()
        self.transporter = Transporter()
        self.turel = Turel()
        self.shoot = Shooting()
        self.hunter = Hunter()
        self.healing = Healing()
        self._state = None
        self.target = None

    def on_born(self):
        self.data.add_drone_my_team(self)
        self.change_state()

    def change_state(self):
        if self.meter_2 < 0.7:
            self._state = self.healing
        elif not self.data.get_enemy_drones(unit=self):
            self._state = self.transporter
            return
        elif self.scene._step > 3000:
            self._state = self.hunter
            return
        else:
            self._state = self.turel

    def choice_target(self):
        if isinstance(self._state, Transporter):
            self.target = self.data.choice_near_objects_to_collect(unit=self)
        elif isinstance(self._state, Turel):
            self.target = self.data.search_for_enemies_in_radius(unit=self)
            if not self.target:
                self.target = self.data.get_enemy_drones(unit=self)[0]
        elif isinstance(self._state, Hunter):
            self.target = self.data.get_enemy_drones(unit=self)[0]
            if not self.target:
                self.target = self.data.get_enemy_base(unit=self)

    def get_action(self):
        self.choice_target()
        self._state.action(self, self.target)

    def on_stop_at_point(self, target):
        self.change_state()
        self.get_action()

    def on_load_complete(self):
        self.change_state()
        self.get_action()

    def on_stop_at_mothership(self, mothership):
        self.change_state()
        self.get_action()

    def on_unload_complete(self):
        self.change_state()
        self.get_action()

    def on_heartbeat(self):
        pass

    def on_wake_up(self):
        self.change_state()
        self.get_action()
