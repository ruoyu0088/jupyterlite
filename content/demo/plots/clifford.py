import io
import cffi
import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt

from cffi import FFI

ffi = FFI()

# Declare the C function signature
ffi.cdef("""
void clifford_attractor(double a, double b, double c, double d,
                        unsigned int *image, int width, int height, int n);
""")

lib = ffi.dlopen('clifford.wasm')

def clifford_attractor(a, b, c, d, n, width=500, height=500):
    # Create a uint32 NumPy array for the image
    image = np.zeros((height, width), dtype=np.uint32)

    # Get C pointer
    ptr = ffi.cast("unsigned int *", image.ctypes.data)

    # Call the C function
    lib.clifford_attractor(a, b, c, d, ptr, width, height, n)

    return image

def clifford_gui():
    a_slider = widgets.FloatSlider(description="a", min=-2, max=2, step=0.01, value=1.9, continuous_update=False)
    b_slider = widgets.FloatSlider(description="b", min=-2, max=2, step=0.01, value=1.9, continuous_update=False)
    c_slider = widgets.FloatSlider(description="c", min=-2, max=2, step=0.01, value=1.9, continuous_update=False)
    d_slider = widgets.FloatSlider(description="d", min=-2, max=2, step=0.01, value=0.8, continuous_update=False)
    
    n_box = widgets.BoundedIntText(description="n", min=100000, max=50_000_000,
                                   step=1_000_000, value=5_000_000)
    
    cmap_dropdown = widgets.Dropdown(
        options=sorted(plt.colormaps()),
        value="magma",
        description="Colormap"
    )
    
    plot_button = widgets.Button(description="Plot", button_style="success")
    
    # --- Image output widget ---
    img_widget = widgets.Image(format="png", layout=widgets.Layout(width="400px"))
    
    # --- Function to render attractor and convert to PNG bytes ---
    def render_png(a, b, c, d, n, cmap):
        # Generate attractor
        img = clifford_attractor(a, b, c, d, n)
    
        # Plot figure without axes
        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
        ax.imshow(np.log1p(img), cmap=cmap, origin="lower")
        ax.axis("off")
    
        # Convert to PNG bytes
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        return buf.read()
    
    # --- Event handler ---
    def on_plot_clicked(_):
        plot_button.description = "Plotting..."
        plot_button.disabled = True
    
        a, b_, c, d = a_slider.value, b_slider.value, c_slider.value, d_slider.value
        n = n_box.value
        cmap = cmap_dropdown.value
    
        png_bytes = render_png(a, b_, c, d, n, cmap)
        img_widget.value = png_bytes
    
        plot_button.description = "Plot"
        plot_button.disabled = False
    
    plot_button.on_click(on_plot_clicked)
    on_plot_clicked(None)
    
    ui = widgets.VBox([
        a_slider, b_slider,
        c_slider, d_slider,
        n_box, cmap_dropdown, plot_button,
        img_widget
    ])
    return ui