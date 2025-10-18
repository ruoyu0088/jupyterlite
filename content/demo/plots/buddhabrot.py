import numpy as np
from cffi import FFI
import matplotlib.pyplot as plt
from ipywidgets import (
    VBox, HBox, RadioButtons, Dropdown, IntSlider, Button, Output
)
from IPython.display import display


ffi = FFI()

ffi.cdef("""
void buddhabrot_random(
    int width,
    int height,
    int max_iter,
    int n_samples,
    double x_min,
    double x_max,
    double y_min,
    double y_max,
    double *path_real,
    double *path_imag,
    double *image
);

void buddhabrot_grid(
    int width,
    int height,
    int max_iter,
    double x_min,
    double x_max,
    double y_min,
    double y_max,
    int scale,
    double *path_real,
    double *path_imag,
    double *image
);
""")


lib = ffi.dlopen("buddhabrot.wasm")

def buddhabrot_grid(width, height, max_iter, scale, x_range=(-2.0, 1.0), y_range=(-1.5, 1.5)):
    x_min, x_max = x_range
    y_min, y_max = y_range
    
    path_real = np.empty(max_iter, dtype=np.float64)
    path_imag = np.empty(max_iter, dtype=np.float64)
    image = np.zeros((height, width), dtype=np.float64)
    
    lib.buddhabrot_grid(
        width,
        height,
        max_iter,
        x_min,
        x_max,
        y_min,
        y_max,
        scale,
        ffi.cast("double *", path_real.ctypes.data),
        ffi.cast("double *", path_imag.ctypes.data),
        ffi.cast("double *", image.ctypes.data),
    )
    return np.rot90(image) / image.max()

def buddhabrot_random(width, height, max_iter, n_samples, x_range=(-2.0, 1.0), y_range=(-1.5, 1.5)):
    x_min, x_max = x_range
    y_min, y_max = y_range
    
    path_real = np.empty(max_iter, dtype=np.float64)
    path_imag = np.empty(max_iter, dtype=np.float64)
    image = np.zeros((height, width), dtype=np.float64)
    
    lib.buddhabrot_random(
        width, height, max_iter, n_samples,
        x_min, x_max, y_min, y_max,
        ffi.cast("double *", path_real.ctypes.data),
        ffi.cast("double *", path_imag.ctypes.data),
        ffi.cast("double *", image.ctypes.data)
    )
    return np.rot90(image) / image.max()


def buddhabrot_gui():
    func_selector = RadioButtons(
    options=["buddhabrot_grid", "buddhabrot_random"],
    value="buddhabrot_random",
    description="Function:",
)

    size_selector = Dropdown(
        options=[200, 300, 400, 500, 600, 700, 800],
        value=300,
        description="Size:",
    )
    
    scale_slider = IntSlider(
        value=4,
        min=1,
        max=10,
        step=1,
        description="Scale:",
    )
    
    samples_slider = IntSlider(
        value=1_000_000,
        min=10_000,
        max=10_000_000,
        step=10_000,
        description="Samples:",
    )
    
    # get all matplotlib colormaps
    colormap_selector = Dropdown(
        options=sorted(plt.colormaps()),
        value="hot",
        description="Colormap:",
    )
    
    run_button = Button(
        description="Generate",
        button_style="success",
        tooltip="Run calculation and display image",
        icon="play",
    )
    
    output = Output()
    
    def on_run_button_clicked(b):
        with output:
            output.clear_output()
            width = height = size_selector.value
            max_iter = 500
            scale = scale_slider.value
            cmap = colormap_selector.value
    
            print(f"Calculating {func_selector.value}...")
    
            if func_selector.value == "buddhabrot_grid":
                img = buddhabrot_grid(width, height, max_iter, scale)
            else:
                n_samples = samples_slider.value
                img = buddhabrot_random(width, height, max_iter, n_samples)
    
            plt.figure(figsize=(5, 5))
            plt.imshow(np.log1p(img), cmap=cmap, origin="lower")
            plt.title(f"{func_selector.value} (size={width}, scale={scale})")
            plt.axis("off")
            plt.show()
    
    run_button.on_click(on_run_button_clicked)
    
    ui = VBox([
        HBox([func_selector, size_selector]),
        HBox([scale_slider, samples_slider]),
        HBox([colormap_selector, run_button]),
        output
    ])
    
    return ui