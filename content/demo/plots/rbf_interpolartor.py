import numpy as np
import matplotlib.pyplot as plt

from scipy.interpolate import RBFInterpolator

import plotly.graph_objects as go

import ipywidgets as widgets
from IPython.display import display, clear_output

# ---------------------------
# Data preparation
# ---------------------------
# 1D data
x_train = np.linspace(0, 10, 8)[:, None]
y_train = np.sin(x_train).ravel()
x_eval = np.linspace(0, 10, 500)[:, None]

# 2D data
np.random.seed(0)
n_points = 50
x_train_2d = np.random.rand(n_points, 2) * 4 - 2
y_train_2d = np.sin(x_train_2d[:, 0] ** 2 + x_train_2d[:, 1] ** 2)
grid_x, grid_y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
xy_eval = np.stack([grid_x.ravel(), grid_y.ravel()], axis=1)

# ---------------------------
# Widget setup
# ---------------------------
kernel_options = [
    "linear",
    "cubic",
    "quintic",
    "thin_plate_spline",
    "multiquadric",
    "inverse_multiquadric",
    "inverse_quadratic",
    "gaussian",
]
epsilon_required = {
    "multiquadric",
    "inverse_multiquadric",
    "inverse_quadratic",
    "gaussian",
}

kernel = widgets.Dropdown(options=kernel_options, value="gaussian", description="Kernel:")
epsilon = widgets.FloatSlider(
    value=1.0, min=0.01, max=5.0, step=0.05, description="Epsilon"
)
smoothing = widgets.FloatSlider(
    value=0.0, min=0.0, max=1.0, step=0.01, description="Smoothing"
)
neighbors = widgets.IntSlider(
    value=0, min=0, max=len(x_train), step=1, description="Neighbors"
)
degree = widgets.IntSlider(
    value=-1, min=-1, max=3, step=1, description="Degree"
)

update_button = widgets.Button(description="Update Plot", button_style="success")

# Output widgets for 2D and 3D plots
output_1d = widgets.Output()
output_3d = widgets.Output()

# ---------------------------
# Update functions
# ---------------------------
def update_plots(_=None):
    kwargs = {
        "kernel": kernel.value,
        "smoothing": smoothing.value,
        "degree": degree.value,
    }
    if neighbors.value > 0:
        kwargs["neighbors"] = neighbors.value
    if kernel.value in epsilon_required:
        kwargs["epsilon"] = epsilon.value

    # ---- 1D plot ----
    with output_1d:
        clear_output(wait=True)
        try:
            rbf = RBFInterpolator(x_train, y_train, **kwargs)
            y_eval = rbf(x_eval)
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot(x_eval, y_eval, label="Interpolated")
            ax.scatter(x_train, y_train, color="black", label="Data")
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print("❌ Error:", e)

    # ---- 3D plot ----
    with output_3d:
        clear_output(wait=True)
        try:
            rbf_2d = RBFInterpolator(x_train_2d, y_train_2d, **kwargs)
            z_pred = rbf_2d(xy_eval).reshape(grid_x.shape)
            fig_3d = go.Figure()

            fig_3d.add_trace(
                go.Surface(
                    x=grid_x,
                    y=grid_y,
                    z=z_pred,
                    colorscale="Viridis",
                    opacity=0.9,
                    showscale=False,
                )
            )
            fig_3d.add_trace(
                go.Scatter3d(
                    x=x_train_2d[:, 0],
                    y=x_train_2d[:, 1],
                    z=y_train_2d,
                    mode="markers",
                    marker=dict(size=2, color="red"),
                )
            )

            fig_3d.update_layout(
                width=400,
                height=400,
                margin=dict(l=0, r=0, b=0, t=0), 
                scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="f(x, y)"),
            )
            fig_3d.update_coloraxes(showscale=False)
            fig_3d.show()
        except Exception as e:
            print("⚠️ Error:", e)

# Connect button
update_button.on_click(update_plots)

# ---------------------------
# Layout
# ---------------------------
controls = widgets.VBox([
    widgets.HTML("<h3>🎯 RBFInterpolator Demo</h3>"),
    kernel, epsilon, smoothing,
    neighbors, degree,
    update_button
])

tabs = widgets.Tab(children=[output_1d, output_3d])
tabs.set_title(0, "2D Plot")
tabs.set_title(1, "3D Plot")

ui = widgets.VBox([controls, tabs])

# Display everything
display(ui)

# Initial render
update_plots()