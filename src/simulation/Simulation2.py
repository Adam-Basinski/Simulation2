import tkinter as tk
from time import sleep
from simulation_settings2 import settings
import Organisms2 


def create_init_cond(settings: dict, canvas: tk.Canvas) -> None:

    # Lists prepare
    food = []
    population = []

    for _i in range(0, settings["food_number"]):
        food.append(Organisms2.Food(canvas = canvas, settings=settings))

    for _i in range(0, settings["start_population"]):
        population.append(Organisms2.Organism2_1(canvas = canvas, settings=settings))

    return (population, food)


def prepare_canvas(settings: dict) -> tuple:
    """Creates window and canvas for simulation"""
    if settings["animate"]:
        window = tk.Tk()
        window.geometry(f"{settings['width']+10}x{settings['height']+10}")
        canvas = tk.Canvas(window, width=settings['width'], height=settings['height'], bg="gray")
        canvas.pack()
        return (window, canvas)
    else:
        return (0, 0)
    

def is_any_food(food_list: list) -> bool:
    """ Checks is there any food present """
    for _f in food_list:
        if _f.reSpawn == False:
            return True
    return False


def eating(org: Organisms2.Organism2_1, food: Organisms2.Food) -> None:
    """ Updates organism and food status """
    # Organism update
    org.fitness += food.energy
    org.target_distance = 10000
    # Food update
    food.reSpawn = True
    food.de_spawn()


def delete_org(organism: Organisms2.Organism2_1, population) -> None:
    """ Delete selected organism """
    if settings["animate"]:
        organism.canvas.itemconfig(organism.image, fill="black")
    del population[population.index(organism)]


def simulate(settings: dict, population: list, food:list, window: tk.Tk) -> None:
    for _org in population:

        if settings["debug"]:
            debug(_org)

        # Eating
        for _f in food:
            _f.try_reSpawn(settings)
            # Check if food is edible and close enough 
            if _f.reSpawn == False and _org.calc_distance(_f) <= _org.velocity:
                eating(_org, _f)
                    
        # Offsprings
        if _org.readyToMate and _org.calc_distance(_org.target) <= _org.velocity:
            Offspring = _org.produce_offspring(settings)
            # In case something happened, this if statement prevent adding NoneType to population list. 
            if Offspring:
                population.append(Offspring)

        # Hunger - drops food by predefined value
        _org.fitness -= settings['food_drop']

        # Starvation - Delete organism if .fitness drops to 0 or below
        if _org.fitness <= 0:
            delete_org(_org, population)

        # Check if ready to mate
        _org.is_ready_to_mate(settings)

        # Targeting food or mate - updates organism's target
        # Search for nearest food
        _org.look_for_food(food)

        # Or search for valid mate
        _org.look_for_mate(population)

        # Move to target 
        _org.rotate(_org.target)
        moving = _org.move((is_any_food(food) or _org.readyToMate))

        # Borders - Delete organism if it hit the border
        if _org.x_coord > settings['width']\
        or _org.x_coord < 0\
        or _org.y_coord > settings['height']\
        or _org.y_coord < 0:
            delete_org(_org)

        # Check if current run is animated and update organism position.
        if settings["animate"]:
            _org.move_canvas(moving)

    # Check if current run is animated and update food position and refresh window.
    if settings["animate"]:
        for _food in food:
            _food.updateCanvas()

        window.update()
        sleep(0.01)


def debug(_org: Organisms2.Organism2_1):
    if _org.target == None:
        _t, _x, _y = [None for i in range(3)]
    else: 
        _t = _org.target.type
        _x = _org.target.x_coord
        _y = _org.target.y_coord
    print(f"Organism {_org}:\
        \n\tFitness: {_org.fitness},\
        \n\tTarget: {_org.target}, {_t}, X:{_x}, Y:{_y}\
        \n\tX: {_org.x_coord},\
        \n\tY: {_org.y_coord},\
        \n\tRotation: {_org.rotation},\
        \n\tMating: {_org.readyToMate}.")
    print('='*60)


def main():
    window, canvas = prepare_canvas(settings)

    population, food = create_init_cond(
        settings=settings,
        canvas=canvas,
    )
    
    while True:
        simulate(settings, population, food, window)

    window.mainloop()


if __name__ == "__main__":
    window, canvas = prepare_canvas(settings)

    population, food = create_init_cond(
        settings=settings,
        canvas=canvas,
    )
    
    while True:
        simulate(settings, population, food, window)

    window.mainloop()
    

    