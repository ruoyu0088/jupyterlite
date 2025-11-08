import random
import asyncio
import pythreejs as p3j
import numpy as np
import ipywidgets as widgets
from matplotlib import cm


def surf_pillow(N):
    u = np.random.uniform(0, np.pi, N)
    v = np.random.uniform(-np.pi, np.pi, N)
    x = np.cos(u)
    y = np.cos(v)
    z = 0.5 * np.sin(u) * np.sin(v)
    return x, y, z


def surf_apple(N):
    u = np.random.uniform(0, 2 * np.pi, N)
    v = np.random.uniform(-np.pi, np.pi, N)
    x = np.cos(u) * (4 + 3.8 * np.cos(v))
    y = np.sin(u) * (4 + 3.8 * np.cos(v))
    z = (np.cos(v) + np.sin(v) - 1) * (1 + np.sin(v)) * np.log(
        1 - np.pi * v / 10
    ) + 7.5 * np.sin(v)
    return x / 6, y / 6, z / 6


def surf_sine(N):
    u = np.random.uniform(-np.pi, np.pi, N)
    v = np.random.uniform(-np.pi, np.pi, N)
    x = np.sin(u)
    y = np.sin(v)
    z = np.sin(u + v)
    return x, y, z


def surf_helicoid(N):
    u = np.random.uniform(-2, 2, N)
    v = np.random.uniform(-np.pi, np.pi, N)
    c = 1.0

    x = u * np.cos(v)
    y = u * np.sin(v)
    z = c * v
    return x / 2, y / 2, z / np.pi


def surf_umbrella(N):
    u = np.random.uniform(-1.5, 1.5, N)
    v = np.random.uniform(-1.5, 1.5, N)
    x = u * v
    y = u
    z = v**2
    return x / 2.2, y / 1.5, z / 2 - 1


def surf_sphere(N):
    u = np.random.uniform(0, np.pi, N)
    v = np.random.uniform(0, 2 * np.pi, N)
    x = np.sin(u) * np.cos(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(u)
    return x, y, z


def surf_torus(N):
    u = np.random.uniform(0, 2 * np.pi, N)
    v = np.random.uniform(0, 2 * np.pi, N)
    R, r = 0.7, 0.3
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)
    return x, y, z


def surf_mobius(N):
    u = np.random.uniform(0, 2 * np.pi, N)
    v = np.random.uniform(-0.3, 0.3, N)
    x = (1 + v * np.cos(u / 2)) * np.cos(u)
    y = (1 + v * np.cos(u / 2)) * np.sin(u)
    z = v * np.sin(u / 2)
    return x, y, z


def surf_klein(N):
    u = np.random.uniform(0, 2 * np.pi, N)
    v = np.random.uniform(0, 2 * np.pi, N)
    x = (2 + np.cos(u / 2) * np.sin(v) - np.sin(u / 2) * np.sin(2 * v)) * np.cos(u)
    y = (2 + np.cos(u / 2) * np.sin(v) - np.sin(u / 2) * np.sin(2 * v)) * np.sin(u)
    z = np.sin(u / 2) * np.sin(v) + np.cos(u / 2) * np.sin(2 * v)
    return x / 3, y / 3, z / 3


def surf_wave(N):
    u = np.random.uniform(-np.pi, np.pi, N)
    v = np.random.uniform(-np.pi, np.pi, N)
    x = u / np.pi
    y = v / np.pi
    z = 0.3 * np.sin(3 * u) * np.cos(3 * v)
    return x, y, z


def surf_saddle(N):
    u = np.random.uniform(-1, 1, N)
    v = np.random.uniform(-1, 1, N)
    x = u
    y = v
    z = u**2 - v**2
    return x, y, z / 2


def surf_cone(N):
    u = np.random.uniform(0, 1, N)
    v = np.random.uniform(0, 2 * np.pi, N)
    x = u * np.cos(v)
    y = u * np.sin(v)
    z = 1 - 2 * u
    return x, y, z


def surf_spiral(N):
    u = np.random.uniform(0, 4 * np.pi, N)
    v = np.random.uniform(-1, 1, N)
    r = 0.2 + 0.8 * v
    x = r * np.cos(u)
    y = r * np.sin(u)
    z = u / (2 * np.pi) - 1
    return x, y, z


def surf_enneper(N):
    u = np.random.uniform(-1, 1, N)
    v = np.random.uniform(-1, 1, N)
    x = u - (u**3) / 3 + u * v**2
    y = v - (v**3) / 3 + v * u**2
    z = u**2 - v**2
    return x / 2, y / 2, z / 2


def surf_cubeish(N):
    u = np.random.uniform(-1, 1, N)
    v = np.random.uniform(-1, 1, N)
    w = np.random.uniform(-1, 1, N)
    x = np.tanh(2 * u)
    y = np.tanh(2 * v)
    z = np.tanh(2 * w)
    return x, y, z


class ScatterAnimation:
    def __init__(self, n=5000):
        self.n = n

        # Available colormaps
        self.cmaps = {
            "Blues": cm.Blues,
            "Reds": cm.Reds,
            "Greens": cm.Greens,
            "Viridis": cm.viridis,
            "Plasma": cm.plasma,
            "Inferno": cm.inferno,
            "Magma": cm.magma,
            "Cividis": cm.cividis,
        }
        self.cmap = self.cmaps["Blues"]

        # Collect surface functions
        self.calc_functions = [
            globals()[name] for name in globals() if name.startswith("surf_")
        ]

        self.current_func = random.choice(self.calc_functions)
        self.x, self.y, self.z = self.current_func(self.n)

        # Geometry and Material
        self.geometry = p3j.BufferGeometry(
            attributes={
                "position": p3j.BufferAttribute(
                    np.c_[self.x, self.y, self.z].astype(np.float32), normalized=False
                ),
                "color": p3j.BufferAttribute(
                    self.calc_colors(self.x, self.y, self.z), normalized=False
                ),
            }
        )

        self.material = p3j.PointsMaterial(
            size=0.05, vertexColors="VertexColors", transparent=True, opacity=1
        )

        points = p3j.Points(geometry=self.geometry, material=self.material)
        scene = p3j.Scene(children=[points], background="black")
        camera = p3j.PerspectiveCamera(position=[2, 2, 2], up=[0, 1, 0], aspect=1)
        self.renderer = p3j.Renderer(
            camera=camera,
            scene=scene,
            controls=[p3j.OrbitControls(controlling=camera)],
            width=350,
            height=350,
        )

        # Control widgets
        self.start_button = widgets.Button(description="Start", button_style="info")
        self.stop_button = widgets.Button(description="Stop", button_style="warning")
        self.size_slider = widgets.FloatSlider(
            value=0.05, min=0.01, max=0.2, step=0.01, description="Point Size"
        )
        self.opacity_slider = widgets.FloatSlider(
            value=1.0, min=0.1, max=1.0, step=0.05, description="Opacity"
        )
        self.cmap_dropdown = widgets.Dropdown(
            options=list(self.cmaps.keys()), value="Blues", description="Colormap"
        )

        # Event bindings
        self.size_slider.observe(self.update_size, names="value")
        self.opacity_slider.observe(self.update_opacity, names="value")
        self.cmap_dropdown.observe(self.update_colormap, names="value")
        self.start_button.on_click(self.on_start)
        self.stop_button.on_click(self.on_stop)

        self.name_label = widgets.Label()
        self.update_name()
        self.task = None

        # Layout
        self.layout = widgets.VBox(
            [
                widgets.HBox([self.start_button, self.stop_button]),
                self.size_slider,
                self.opacity_slider,
                self.cmap_dropdown,
                self.name_label,
                self.renderer,
            ]
        )

    def update_name(self):
        self.name_label.value = self.current_func.__name__.split("_")[1]

    # Update methods
    def update_size(self, change):
        self.material.size = change["new"]

    def update_opacity(self, change):
        self.material.opacity = change["new"]

    def update_colormap(self, change):
        self.cmap = self.cmaps[change["new"]]
        self.geometry.attributes["color"].array = self.calc_colors(
            self.x, self.y, self.z
        )
        self.geometry.attributes["color"].needsUpdate = True

    def on_start(self, b):
        if self.task is None:
            self.task = asyncio.create_task(self.animate())

    def on_stop(self, b):
        if self.task is not None:
            self.task.cancel()
            self.task = None

    def calc_colors(self, x, y, z):
        dist = np.sqrt(x**2 + y**2 + z**2)
        dist /= dist.max()
        colors = self.cmap(dist)
        return colors[:, :3].astype(np.float32)

    async def animate(self, k=0.1, steps=50, delay=0.05):
        while True:
            # Pick a different surface
            while True:
                func = random.choice(self.calc_functions)
                if func != self.current_func:
                    break
                self.current_func = func
                self.update_name()

            self.name_label.value = func.__name__.split("_")[1]

            x2, y2, z2 = func(self.n)

            # Smooth morphing
            for _ in range(steps):
                self.x += k * (x2 - self.x)
                self.y += k * (y2 - self.y)
                self.z += k * (z2 - self.z)

                self.geometry.attributes["position"].array = np.c_[
                    self.x, self.y, self.z
                ].astype(np.float32)
                self.geometry.attributes["color"].array = self.calc_colors(
                    self.x, self.y, self.z
                )
                self.geometry.attributes["position"].needsUpdate = True
                self.geometry.attributes["color"].needsUpdate = True
                await asyncio.sleep(delay)
