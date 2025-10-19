import asyncio
import base64
import cv2
import numpy as np
from matplotlib import cm
from matplotlib.colors import Colormap
import ipywidgets as widgets
import anywidget
from traitlets import Int, Unicode, Dict
import cffi
from IPython.display import display


class ImageWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let count = 0;
        const canvas = document.createElement("canvas");
        canvas.width = model.get("width");
        canvas.height = model.get("height");
        canvas.style.border = "1px solid black";
        el.appendChild(canvas);
        const ctx = canvas.getContext("2d");
        let img = null;

        async function loadImage() {
            const src = model.get("image");
            if (src) {
                img = new Image();
                img.src = src;
                await new Promise(resolve => img.onload = resolve);
            }
        }

        async function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (img) ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }

        async function init() {
            await loadImage();
            draw();
        }
        init();

        model.on("change:image", async () => { await loadImage(); draw(); });

        // Zoom
        canvas.addEventListener("wheel", event => {
            event.preventDefault();
            const rect = canvas.getBoundingClientRect();
            model.set("zoom_event", { 
                count: count,
                x: event.clientX - rect.left,
                y: event.clientY - rect.top,
                delta: event.deltaY
            });
            model.save_changes();
            count += 1;
        });

        // Pan
        let isPanning = false, panStartX = 0, panStartY = 0;
        canvas.addEventListener("mousedown", e => {
            const rect = canvas.getBoundingClientRect();
            panStartX = e.clientX - rect.left;
            panStartY = e.clientY - rect.top;
            isPanning = true;
        });
        canvas.addEventListener("mousemove", e => {
            if (isPanning) {
                const rect = canvas.getBoundingClientRect();
                model.set("pan_event", { x0: panStartX, y0: panStartY,
                                         x1: e.clientX - rect.left, y1: e.clientY - rect.top });
                model.save_changes();
            }
        });
        canvas.addEventListener("mouseup", e => {
            if (isPanning) {
                const rect = canvas.getBoundingClientRect();
                model.set("pan_event", { dx: (e.clientX - rect.left - panStartX), 
                                         dy: (e.clientY - rect.top - panStartY) });
                model.save_changes();
                isPanning = false;
            }
        });
        canvas.addEventListener("mouseleave", () => { isPanning = false; });
    }
    export default { render };
    """

    width = Int(default_value=400).tag(sync=True)
    height = Int(default_value=400).tag(sync=True)
    image = Unicode(default_value="").tag(sync=True)
    zoom_event = Dict(default_value={}).tag(sync=True)
    pan_event = Dict(default_value={}).tag(sync=True)

    def set_image(self, array):
        success, buffer = cv2.imencode(".png", array[:, :, ::-1])
        data = base64.b64encode(buffer).decode()
        self.image = f"data:image/png;base64,{data}"

# =====================
# Setup CFFI and WASM
# =====================
ffi = cffi.FFI()
ffi.cdef("""
void mandelbrot(double cx, double cy, double d, int h, int w,
                double* result, int n, double R);
""")
lib = ffi.dlopen("mandelbrot.wasm")  # Your compiled WASM

def zoom(cx, cy, d, width, height, mx, my, wheel_delta, zoom_factor=1.2):
    x0, x1 = cx - d, cx + d
    y0, y1 = cy - d, cy + d
    x = x0 + (mx / width) * (x1 - x0)
    y = y0 + (my / height) * (y1 - y0)
    factor = zoom_factor if wheel_delta > 0 else 1 / zoom_factor
    d *= factor
    x0 = x - (x - x0) * factor
    y0 = y - (y - y0) * factor
    x1 = x - (x - x1) * factor
    y1 = y - (y - y1) * factor
    return (x0 + x1) * 0.5, (y0 + y1) * 0.5, d

class Drawer:
    def __init__(self, image_widget, max_iter, escape_radius, cmap_selector, result):
        self.center_x = -0.5
        self.center_y = 0.0
        self.d = 1.5
        self.image_widget = image_widget
        self.max_iter = max_iter
        self.width = self.image_widget.width
        self.height = self.image_widget.height
        self.result = result
        self.p_result = ffi.from_buffer("double *", result)
        self.escape_radius = escape_radius
        self.cmap_selector = cmap_selector
        self.show_mandelbrot()

    def show_mandelbrot(self, dx=0, dy=0):
        iter = min(int(self.max_iter / self.d), 500)
        lib.mandelbrot(self.center_x+dx, self.center_y+dy, self.d, self.height, self.width,
                       self.p_result, iter, self.escape_radius)
        cmap = getattr(cm, self.cmap_selector.value)
        _data = (cmap(self.result / (self.result.max()+1e-6))*255).astype(np.uint8)[:, :, :3]
        self.image_widget.set_image(_data)

    def on_zoom_change(self, event):
        x, y, delta = event["x"], event["y"], event["delta"]
        self.center_x, self.center_y, self.d = zoom(
            self.center_x, self.center_y, self.d, self.width, self.height, x, y, delta
        )
        self.show_mandelbrot()

    def on_pan_change(self, event):
        width = self.width
        height = self.height
        
        if "dx" in event:
            self.center_x -= event["dx"] * 2 * self.d / width
            self.center_y -= event["dy"] * 2 * self.d / height
            self.show_mandelbrot()
        elif "x0" in event:
            dx = (event["x1"] - event["x0"]) * 2 * self.d / width
            dy = (event["y1"] - event["y0"]) * 2 * self.d / height
            self.show_mandelbrot(-dx, -dy)

def mandelbrot_gui(width=400, height=400, max_iter=100, escape_radius=10.0):
    result = np.zeros((height, width), dtype=np.float64)
    
    cmap_names = [name for name in dir(cm) if isinstance(getattr(cm, name), Colormap)]
    cmap_selector = widgets.Dropdown(options=cmap_names, value='hot', description='Colormap:')
    
    image_widget = ImageWidget(width=width, height=height)
    drawer = Drawer(image_widget, max_iter=max_iter, escape_radius=escape_radius, cmap_selector=cmap_selector, result=result)

    async def update_loop():
        current_zoom = image_widget.zoom_event
        current_pan = image_widget.pan_event
        current_cmap = cmap_selector.value
        while True:
            if current_zoom != image_widget.zoom_event:
                current_zoom = image_widget.zoom_event
                drawer.on_zoom_change(current_zoom)
            if current_pan != image_widget.pan_event:
                current_pan = image_widget.pan_event
                drawer.on_pan_change(current_pan)
            if current_cmap != cmap_selector.value:
                current_cmap = cmap_selector.value
                drawer.show_mandelbrot()
            await asyncio.sleep(0.02)
    
    asyncio.create_task(update_loop())
    return widgets.VBox([cmap_selector, image_widget])