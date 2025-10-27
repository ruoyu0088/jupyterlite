from dataclasses import dataclass, field
import math
import random
from typing import ClassVar
from matplotlib import pyplot as plt
from dataclasses import dataclass
import ipywidgets as widgets
import plotly.graph_objects as go

@dataclass
class Grass:
    status: int
    count: int
    grass_time: ClassVar[int]

    @classmethod
    def random(class_):
        status = random.randint(0, 1)
        if status == 0:
            count = random.randint(0, class_.grass_time)
        else:
            count = class_.grass_time
        return class_(status=status, count=count)

    def step(self):
        if self.status == 0:
            self.count -= 1
            if self.count <= 0:
                self.status = 1
                self.count = self.grass_time

    def clear(self):
        self.status = 0
        self.count = self.grass_time


@dataclass
class Actor:
    x: float
    y: float
    angle: float
    energy: float
    gain: ClassVar[int]
    born_rate: ClassVar[float]
    speed: ClassVar[float]

    def move(self, size):
        delta_angle = random.randint(0, 50) - random.randint(0, 50)
        self.angle += delta_angle
        angle = math.radians(self.angle)
        length = random.uniform(1, self.speed)
        self.x = (self.x + math.cos(angle) * length) % size
        self.y = (self.y + math.sin(angle) * length) % size

    @property
    def loc(self):
        return int(self.x), int(self.y)

    def die(self, cell):
        if self.energy < 0:
            cell.remove_actor(self)

    def born(self, cell):
        if random.random() < self.born_rate:
            self.energy /= 2
            new_actor = type(self)(x=self.x, y=self.y,
                                   angle=random.uniform(0, 360),
                                   energy=self.energy)
            cell.add_actor(new_actor)

    @classmethod
    def random(class_, size):
        x = random.uniform(0, size)
        y = random.uniform(0, size)
        angle = random.uniform(0, 360)
        energy = random.uniform(0, 2 * class_.gain) * 4
        return class_(x=x, y=y, angle=angle, energy=energy)

    def step(self, cell):
        self.energy -= 1
        self.eat(cell)
        self.die(cell)
        self.born(cell)


@dataclass
class Sheep(Actor):
    def eat(self, cell):
        if cell.grass.status:
            cell.grass.clear()
            self.energy += self.gain


@dataclass
class Wolf(Actor):
    def eat(self, cell):
        if cell.sheeps:
            cell.sheeps.pop()
            self.energy += self.gain


@dataclass
class Cell:
    grass: Grass
    sheeps: list = field(default_factory=list)
    wolves: list = field(default_factory=list)

    def add_actor(self, actor):
        if isinstance(actor, Sheep):
            self.sheeps.append(actor)
        else:
            self.wolves.append(actor)

    def remove_actor(self, actor):
        if isinstance(actor, Sheep):
            if actor in self.sheeps:
                self.sheeps.remove(actor)
        else:
            if actor in self.wolves:
                self.wolves.remove(actor)


class World:
    def __init__(self, size, init_sheep_count, init_wolf_count,
                 sheep_born_rate, wolf_born_rate,
                 sheep_gain, wolf_gain, grass_time,
                 sheep_speed, wolf_speed):
        self.size = size
        Sheep.born_rate = sheep_born_rate
        Wolf.born_rate = wolf_born_rate
        Sheep.gain = sheep_gain
        Wolf.gain = wolf_gain
        Grass.grass_time = grass_time
        Sheep.speed = sheep_speed
        Wolf.speed = wolf_speed

        self.cells = {(i, j): Cell(Grass.random())
                      for i in range(size) for j in range(size)}

        self.sheeps = []
        for _ in range(init_sheep_count):
            sheep = Sheep.random(size)
            self.sheeps.append(sheep)
            self.cells[sheep.loc].add_actor(sheep)

        self.wolves = []
        for _ in range(init_wolf_count):
            wolf = Wolf.random(size)
            self.wolves.append(wolf)
            self.cells[wolf.loc].add_actor(wolf)

    def step(self):
        self.grass_count = 0
        for cell in self.cells.values():
            cell.grass.step()
            self.grass_count += cell.grass.status
            cell.sheeps.clear()
            cell.wolves.clear()

        for actor in self.sheeps + self.wolves:
            actor.move(self.size)
            cell = self.cells[actor.loc]
            cell.add_actor(actor)
            actor.step(cell)

        self.sheeps = [s for cell in self.cells.values() for s in cell.sheeps]
        self.wolves = [w for cell in self.cells.values() for w in cell.wolves]
        self.sheep_count = len(self.sheeps)
        self.wolf_count = len(self.wolves)

    def run(self, steps, fig=None):
        g, s, w = [], [], []
        for i in range(steps):
            self.step()
            g.append(self.grass_count / Sheep.gain)
            s.append(self.sheep_count)
            w.append(self.wolf_count)
            if fig and i % 100 == 0:
                with fig.batch_update():
                    fig.data[0].y = g
                    fig.data[1].y = s
                    fig.data[2].y = w
                    fig.data[0].x = fig.data[1].x = fig.data[2].x = list(range(len(g)))
        return dict(grass=g, sheep=s, wolf=w)

def gui():
    def run_simulation(init_sheep_count, init_wolf_count,
                       sheep_born_rate, wolf_born_rate,
                       sheep_gain, wolf_gain,
                       grass_time, sheep_speed, wolf_speed,
                       steps):
        global world
    
        world = World(size=50,
                      init_sheep_count=init_sheep_count,
                      init_wolf_count=init_wolf_count,
                      sheep_born_rate=sheep_born_rate,
                      wolf_born_rate=wolf_born_rate,
                      sheep_gain=sheep_gain,
                      wolf_gain=wolf_gain,
                      grass_time=grass_time,
                      sheep_speed=sheep_speed,
                      wolf_speed=wolf_speed)
    
        world.run(steps=int(steps), fig=fig)
    
    controls = {
        'init_sheep_count': widgets.IntSlider(100, 10, 500, 10, description='Init Sheep'),
        'init_wolf_count': widgets.IntSlider(50, 10, 300, 10, description='Init Wolf'),
        'sheep_born_rate': widgets.FloatSlider(0.05, min=0.0, max=0.2, step=0.01, description='Sheep Born'),
        'wolf_born_rate': widgets.FloatSlider(0.03, min=0.0, max=0.2, step=0.01, description='Wolf Born'),
        'sheep_gain': widgets.IntSlider(4, 1, 20, 1, description='Sheep Gain'),
        'wolf_gain': widgets.IntSlider(20, 1, 50, 1, description='Wolf Gain'),
        'grass_time': widgets.IntSlider(30, 5, 100, 5, description='Grass Time'),
        'sheep_speed': widgets.FloatSlider(1, min=0.5, max=5, step=0.1, description='Sheep Speed'),
        'wolf_speed': widgets.FloatSlider(2, min=0.5, max=5, step=0.1, description='Wolf Speed'),
        'steps': widgets.IntSlider(1000, 100, 3000, 100, description='Steps')
    }
    
    fig = go.FigureWidget()
    fig.add_scatter(y=[], mode="lines", name="Grass/SheepGain", line=dict(color="green"))
    fig.add_scatter(y=[], mode="lines", name="Sheep", line=dict(color="blue"))
    fig.add_scatter(y=[], mode="lines", name="Wolf", line=dict(color="red"))
    fig.update_layout(title="Wolf–Sheep–Grass Simulation",
                      xaxis_title="Step", yaxis_title="Count")
    
    run_button = widgets.Button(description="Run Simulation", button_style='success')
    
    ui = widgets.VBox(list(controls.values()) + [run_button, fig])
    
    def on_run_clicked(_):
        run_simulation(**{k: w.value for k, w in controls.items()})
    
    run_button.on_click(on_run_clicked)
    return ui