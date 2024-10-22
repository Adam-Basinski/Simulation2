from random import uniform, randint
from math import sqrt, atan2, cos, sin
from numpy import nan, isnan, nanmin
from itertools import count
import tkinter as tk


class Organism2_1():
    id_iter = count()
    def __init__(self, canvas: tk.Canvas, settings: dict) -> None:
        # Unique ID
        self.ID = next(self.id_iter)
        # Position
        self.x_coord = uniform(100, settings['width']-100)
        self.y_coord = uniform(100, settings['height']-100)
        self.canvas = canvas
        if settings["animate"]:
        # Creating canvas properties
            self.image = canvas.create_oval(
                self.x_coord-settings['radius_org'],
                self.y_coord-settings['radius_org'],
                self.x_coord+settings['radius_org'],
                self.y_coord+settings['radius_org'],
                fill='green'
            )
        # Perks
        self.velocity = uniform(settings['v_min'], settings['v_max'])

        # Properties
        self.rotation = 0
        self.fitness = settings["starting_fitness"]
        self.readyToMate = False
        self.target = None
        self.type = "organism"

    ###
    # Calculation 
    def calc_distance(self, target: object) -> float:
        """ Calculate distance to target """
        if target != None:
            return sqrt((self.x_coord-target.x_coord)**2 + (self.y_coord-target.y_coord)**2)
        else:
            return nan

    ###
    # Status 
    def is_ready_to_mate(self, settings: dict) -> None:
        """Check if organism is ready to mate.
        Change .readyToMate from False to True, if 2* minimum fitness required to looking for mating partner.
        Change it back to False, if fitness is less than minimum."""
        if self.fitness >= settings["mate_search_fitness"]:
            self.readyToMate = True
        if self.readyToMate and (self.fitness < 0.7*settings["mate_search_fitness"]):
            self.readyToMate = False

    ###
    # Action 
    def rotate(self, target: object) -> None:
        """ Rotate organism to chosen target, change property rotation of the organism"""
        if target != None:
            self.rotation = atan2(target.y_coord-self.y_coord, target.x_coord-self.x_coord)
        else:
            self.rotation = 0


    def move(self, isAnyTarget: bool) -> list:
        """ Changes position based on rotation and speed """
        
        # index 0 equals move along X axis, index 1 equals move along Y axis.
        CurrentMove = [0.0, 0.0]

        if isAnyTarget and self.target is not None:
            CurrentMove[0] = self.velocity * cos(self.rotation)
            CurrentMove[1] = self.velocity * sin(self.rotation)
        else:
            CurrentMove[0] = randint(-self.velocity, self.velocity)
            CurrentMove[1] = randint(-self.velocity, self.velocity)

        self.x_coord += CurrentMove[0]
        self.y_coord += CurrentMove[1]
        return CurrentMove


    def move_canvas(self, move: list) -> None:
        "Updates canvas image."
        self.canvas.move(self.image, move[0], move[1])


    # Choosing target
    def look_for_food(self, food_list: list) -> None:
        _food_distance = list()
        for _f in food_list:
            if _f.reSpawn == False:
                _food_distance.append(self.calc_distance(_f))
            else:
                _food_distance.append(nan)
        _minDistance = nanmin(_food_distance)
        if isnan(_minDistance):
            print("O"*200)
            self.target = None
        else:
            self.target = food_list[_food_distance.index(_minDistance)]


    def look_for_mate(self, population: list) -> None:
        # Check if organism is ready
        if self.readyToMate:
            _potential_org = list()
            _org_distance = list()
            for _organism in population:
                if _organism != self and _organism.readyToMate:
                    # Creates lists of potential partners, and distance to them 
                    _potential_org.append(_organism)
                    _org_distance.append(self.calc_distance(_organism))
            try:
                # Tries to chose nearest partner 
                self.target: Organism2_1 = _potential_org[_org_distance.index(nanmin(_org_distance))]
            # If there are no valid partner, min() with empty list will rise ValueError.
            # With no potential partner there is no need to overwrite target.
            except ValueError:
                pass

    # Creating offspring        
    def produce_offspring(self, settings: dict) -> object:
        try:
            # Producing offspring cost energy, in this case half of actual fitness.
            self.fitness = int(self.fitness/2)
            self.target.fitness = int(self.fitness/2)

            print(self.canvas)
            Offspring = Organism2_1(self.canvas, settings)
            # Attributes of new organism are random, because __init__ works like for setup.
            # Corrections are made here.
            # Position
            Offspring.x_coord, Offspring.y_coord = self.x_coord, self.y_coord
            if settings["animate"]:
                Offspring.canvas.moveto(Offspring.image, self.x_coord, self.y_coord)
            # Perks
            Offspring.velocity = uniform(self.velocity, self.target.velocity)
            # Properties
            Offspring.fitness = (self.fitness + self.target.fitness)

            self.readyToMate, self.target.readyToMate = False, False
            return Offspring
        
        except AttributeError:
            False
        
class Food():
    def __init__(self, canvas: tk.Canvas, settings: dict) -> None:
        # Position
        self.x_coord = randint(100, settings['width']-100)
        self.y_coord = randint(100, settings['height']-100)

        # Creating canvas properties
        if settings["animate"]:
            self.canvas = canvas
            self.image = canvas.create_oval(
                self.x_coord-settings['radius_food'],
                self.y_coord-settings['radius_food'],
                self.x_coord+settings['radius_food'],
                self.y_coord+settings['radius_food'],
                fill='red'
            )

        # Properties
        self.energy = settings['food_energy']
        self.reSpawn = False
        self.reSpawn_counter = 0
        self.type = "Food"


    def try_reSpawn(self, settings: dict) -> None:
        """ Check current status and tries to bring this food back on screen """
        if self.reSpawn == True:
            self.reSpawn_counter += 1
            if self.reSpawn_counter >= settings['re_spawn_cycles']:
                # Makes food appears again on screen
                self.x_coord = uniform(settings['width']*0.001, settings['width']*0.999)
                self.y_coord = uniform(settings['height']*0.001, settings['height']*0.999)
                # Update status
                self.reSpawn = False
                self.reSpawn_counter = 0


    def de_spawn(self) -> None:
        """ Hide food instead of deleting object """
        self.x_coord = nan
        self.y_coord = nan


    def updateCanvas(self) -> None:
        """Replace object position on canvas or move object to hide it."""
        if isnan(self.x_coord) or isnan(self.y_coord):
            self.canvas.moveto(self.image, 99999, 99999)
        else:
            self.canvas.moveto(
                self.image,
                self.x_coord,
                self.y_coord
            )