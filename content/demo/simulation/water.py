import numpy as np
import random
import base64
import cv2
import asyncio
from matplotlib import cm
import ipywidgets as widgets
from IPython.display import display
import anywidget
from traitlets import Int, Unicode, Dict


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
          await new Promise((resolve) => {
            img.onload = resolve;
          });
        }
      }

      async function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (img) {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }
      }

      async function init() {
        await loadImage();
        draw();
      }

      // Initial draw
      init();

      model.on("change:image", async () => {
        await loadImage();
        draw();
      });

      canvas.addEventListener("mousemove", (event) => {
          const rect = canvas.getBoundingClientRect();
          const mouseX = event.clientX - rect.left;
          const mouseY = event.clientY - rect.top;

          model.set("move_event", {
            x: mouseX,
            y: mouseY
          });
          model.save_changes();
        }
      );
    }

    export default { render };
    """

    width = Int(default_value=400).tag(sync=True)
    height = Int(default_value=400).tag(sync=True)
    image = Unicode(default_value="").tag(sync=True)
    move_event = Dict(default_value={}).tag(sync=True)

    def set_image(self, array):
        success, buffer = cv2.imencode(".png", array[:, :, ::-1])
        data = base64.b64encode(buffer).decode()
        src = f"data:image/png;base64,{data}"
        height, width = array.shape[:2]
        self.image = src


def kernel_numpy(u, u2, dump):
    out = np.empty_like(u)
    out[1:-1, 1:-1] = (
        0.25
        * (
            u[0:-2, 1:-1]
            + u[2:, 1:-1]
            + u[1:-1, 0:-2]
            + u[1:-1, 2:]
            - 4 * u[1:-1, 1:-1]
        )
        + 2 * u[1:-1, 1:-1]
        - u2[1:-1, 1:-1]
    ) * dump
    out[0, :] = out[-1, :] = out[:, 0] = out[:, -1] = 0
    return out


def sim_water(width=300, height=300, dump=0.98):
    cmap = cm.Blues
    image_widget = ImageWidget(width=width, height=height)
    
    water1 = np.zeros((height, width), dtype=np.float64)
    water2 = np.zeros((height, width), dtype=np.float64)
    current_pos = {}

    async def update_image():
        water1 = np.zeros((height, width), dtype=np.float64)
        water2 = np.zeros((height, width), dtype=np.float64)
        current_pos = {}
    
        while True:
            pos = image_widget.move_event
            water3 = kernel_numpy(water1, water2, 0.98)
            water1, water2 = water3, water1
    
            if current_pos != pos:
                current_pos = pos
                y, x = int(pos['y']), int(pos['x'])
                if 1 <= x < width - 2 and 1 <= y < height -2:
                    water1[y, x] = 120
    
            if random.random() < 0.1:
                water1[random.randint(1, height - 2), random.randint(1, width - 2)] = 120.0
            image = (water1 + 20) / 40
            image = (cmap(image)[:, :, :3] * 255).astype(np.uint8)
            image_widget.set_image(image)
            await asyncio.sleep(0.02)
    
    for _task in asyncio.all_tasks():
        if _task.get_coro().__name__ == "update_image":
            _task.cancel()
    
    task = asyncio.create_task(update_image())
    display(image_widget)
    return task