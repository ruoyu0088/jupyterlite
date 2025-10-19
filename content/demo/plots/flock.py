import ipywidgets as widgets
from IPython.display import display
import anywidget
from traitlets import List, Int
import polars as pl
import numpy as np
import time
import asyncio

class LineCanvasWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
      const canvas = document.createElement("canvas");
      canvas.width = model.get("width");
      canvas.height = model.get("height");
      canvas.style.border = "1px solid black";
      el.appendChild(canvas);
      const ctx = canvas.getContext("2d");

      function drawLines(lines) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = "black";
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (const [x1, y1, x2, y2] of lines) {
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
        }
        ctx.stroke();
      }

      drawLines(model.get("lines"));
      model.on("change:lines", () => drawLines(model.get("lines")));
    }
    export default { render };
    """
    width = Int(400).tag(sync=True)
    height = Int(400).tag(sync=True)
    lines = List([]).tag(sync=True)


def init_data(n, width, height):
    return pl.DataFrame(
        {
            "id": np.arange(n, dtype=np.int16),
            "x": np.random.randint(0, width - 1, n).astype(np.float64),
            "y": np.random.randint(0, height - 1, n).astype(np.float64),
            "vx": np.random.randn(n),
            "vy": np.random.randn(n),
        }
    )

def hypot(x, y):
    if isinstance(x, str):
        x = pl.col(x)
    if isinstance(y, str):
        y = pl.col(y)

    return (x**2 + y**2).sqrt()


def norm(x, y):
    if isinstance(x, str):
        x = pl.col(x)

    if isinstance(y, str):
        y = pl.col(y)

    length = hypot(x, y)
    return x / length, y / length


def dist(x1, y1, x2, y2):
    if isinstance(x1, str):
        x1 = pl.col(x1)

    if isinstance(x2, str):
        x2 = pl.col(x2)

    if isinstance(y1, str):
        y1 = pl.col(y1)

    if isinstance(y2, str):
        y2 = pl.col(y2)

    return hypot(x1 - x2, y1 - y2)

expr_dist = dist("x", "y", "x2", "y2")
expr_v2_length = hypot("vx2", "vy2")
expr_v_length = hypot("vx", "vy")

def update(
    df, width, height, alignment_range, cohesion_range, separation_range
):
    df_dist = (
        df.join(df, how="cross", suffix="2")
        .filter(pl.col("id") != pl.col("id2"))
        .with_columns(dist=expr_dist)
    )

    return (
        df_dist.lazy()
        .with_columns(
            ax1=pl.when(pl.col("dist").is_between(*alignment_range))
            .then(pl.col("vx2") / expr_v2_length)
            .otherwise(None),
            ay1=pl.when(pl.col("dist").is_between(*alignment_range))
            .then(pl.col("vy2") / expr_v2_length)
            .otherwise(None),
            ax2=pl.when(pl.col("dist").is_between(*cohesion_range))
            .then((pl.col("x2") - pl.col("x")) / pl.col("dist"))
            .otherwise(None),
            ay2=pl.when(pl.col("dist").is_between(*cohesion_range))
            .then((pl.col("y2") - pl.col("y")) / pl.col("dist"))
            .otherwise(None),
            ax3=pl.when(pl.col("dist").is_between(*separation_range))
            .then((pl.col("x") - pl.col("x2")) / pl.col("dist"))
            .otherwise(None)
            .fill_nan(None),
            ay3=pl.when(pl.col("dist").is_between(*separation_range))
            .then((pl.col("y") - pl.col("y2")) / pl.col("dist"))
            .otherwise(None)
            .fill_nan(None),
        )
        .group_by("id", maintain_order=True)
        .agg(
            x=pl.col("x").first(),
            y=pl.col("y").first(),
            vx=pl.col("vx").first(),
            vy=pl.col("vy").first(),
            ax1=pl.col("ax1").sum(),
            ay1=pl.col("ay1").sum(),
            ax2=pl.col("ax2").sum(),
            ay2=pl.col("ay2").sum(),
            ax3=pl.col("ax3").sum(),
            ay3=pl.col("ay3").sum(),
        )
        .with_columns(
            ax1=(pl.col("ax1") / hypot("ax1", "ay1")).fill_nan(0),
            ay1=(pl.col("ay1") / hypot("ax1", "ay1")).fill_nan(0),
            ax2=(pl.col("ax2") / hypot("ax2", "ay2")).fill_nan(0),
            ay2=(pl.col("ay2") / hypot("ax2", "ay2")).fill_nan(0),
            ax3=(pl.col("ax3") / hypot("ax3", "ay3")).fill_nan(0),
            ay3=(pl.col("ay3") / hypot("ax3", "ay3")).fill_nan(0),
        )
        .with_columns(
            ax=pl.col("ax1") + pl.col("ax2") + pl.col("ax3"),
            ay=pl.col("ay1") + pl.col("ay2") + pl.col("ay3"),
        )
        .with_columns(
            x=pl.col("x") + pl.col("vx"),
            y=pl.col("y") + pl.col("vy"),
            vx=pl.col("vx") + 0.5 * pl.col("ax"),
            vy=pl.col("vy") + 0.5 * pl.col("ay"),
        )
        .with_columns(
            pl.col("vx")
            .map_batches(lambda v: v + np.random.normal(0, 1, len(v)))
            .clip(-5, 5),
            pl.col("vy")
            .map_batches(lambda v: v + np.random.normal(0, 1, len(v)))
            .clip(-5, 5),
        )
        .with_columns(
            pl.col("x").clip(1, width - 1),
            pl.col("y").clip(1, height - 1),
            pl.when((pl.col("x") < 0) | (pl.col("x") > width))
            .then(-pl.col("vx"))
            .otherwise(pl.col("vx"))
            .alias("vx"),
            pl.when((pl.col("y") < 0) | (pl.col("y") > height))
            .then(-pl.col("vy"))
            .otherwise(pl.col("vy"))
            .alias("vy"),
        )
        .select("id", "x", "y", "vx", "vy")
        .collect()
    )
    return df


def gui():
    width, height, n = 400, 400, 150
    canvas = LineCanvasWidget(lines=[], width=width, height=height)
    
    alignment_slider = widgets.IntRangeSlider(
        value=[30, 40], min=10, max=100, step=1, description="Alignment", continuous_update=False
    )
    cohesion_slider = widgets.IntRangeSlider(
        value=[40, 60], min=10, max=100, step=1, description="Cohesion", continuous_update=False
    )
    separation_slider = widgets.IntRangeSlider(
        value=[0, 25], min=0, max=50, step=1, description="Separation", continuous_update=False
    )
    init_button = widgets.Button(description="Init", button_style="info")
    
    df = init_data(n, width, height)
    
    async def run_sim():
        nonlocal df
        while True:
            df = update(
                df,
                width,
                height,
                alignment_slider.value,
                cohesion_slider.value,
                separation_slider.value,
            )
            segments = (
                df.select(
                    "x", "y",
                    x2=pl.col("x") + pl.col("vx") / expr_v_length * 5,
                    y2=pl.col("y") + pl.col("vy") / expr_v_length * 5,
                ).to_numpy().tolist()
            )
            canvas.lines = segments
            await asyncio.sleep(0.033)
    
    def on_init_clicked(_):
        nonlocal df
        df = init_data(n, width, height)

    for _task in asyncio.all_tasks():
        if _task.get_coro().__name__ == "run_sim":
            _task.cancel() 
    
    init_button.on_click(on_init_clicked)
    task = asyncio.create_task(run_sim())
    
    return widgets.VBox([
        alignment_slider,
        cohesion_slider,
        separation_slider,
        init_button,
        canvas
    ])