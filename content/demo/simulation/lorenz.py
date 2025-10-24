import numpy as np
from scipy import integrate
import plotly.graph_objects as go
from ipywidgets import FloatSlider, IntSlider, VBox, interactive_output
import ipywidgets as widgets

def solve_lorenz(N=10, angle=0.0, max_time=4.0, sigma=10.0, beta=8./3, rho=28.0):
    def lorenz_deriv(x_y_z, t0, sigma=sigma, beta=beta, rho=rho):
        x, y, z = x_y_z
        return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

    np.random.seed(1)
    x0 = -15 + 30 * np.random.random((N, 3))
    t = np.linspace(0, max_time, int(250 * max_time))
    x_t = np.asarray([integrate.odeint(lorenz_deriv, x0i, t) for x0i in x0])
    return t, x_t

# Create figure widget
fig = go.FigureWidget()
fig.add_trace(go.Scatter3d(mode='lines', line=dict(width=1), showlegend=False))

def update_plot(angle=0.0, max_time=4.0, N=10, sigma=10.0, rho=28.0):
    t, x_t = solve_lorenz(N=N, angle=angle, max_time=max_time, sigma=sigma, rho=rho)
    
    current_traces = len(fig.data)

    with fig.batch_update():
        # Update existing traces
        for i in range(min(current_traces, N)):
            x, y, z = x_t[i, :, :].T
            fig.data[i].x = x
            fig.data[i].y = y
            fig.data[i].z = z
        
        # Add new traces if N > current_traces
        for i in range(current_traces, N):
            x, y, z = x_t[i, :, :].T
            fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(width=1), showlegend=False))
    
        if len(fig.data) > N:
            fig.data = fig.data[:N]
            
        # Update layout
        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                camera=dict(eye=dict(
                    x=np.cos(np.radians(angle)), 
                    y=np.sin(np.radians(angle)), 
                    z=0.5
                ))
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            width=400, height=400,
            
        )

def lorenz_attractor():
    # Slider styling for wider sliders and update on release
    slider_layout = widgets.Layout(width='350px')
    
    angle_slider = FloatSlider(value=0.0, min=0.0, max=360.0, step=1.0, description='angle',
                               layout=slider_layout, continuous_update=False)
    max_time_slider = FloatSlider(value=4.0, min=0.1, max=4.0, step=0.1, description='max_time',
                                  layout=slider_layout, continuous_update=False)
    N_slider = IntSlider(value=10, min=0, max=50, step=1, description='N',
                         layout=slider_layout, continuous_update=False)
    sigma_slider = FloatSlider(value=10.0, min=0.0, max=50.0, step=0.5, description='sigma',
                               layout=slider_layout, continuous_update=False)
    rho_slider = FloatSlider(value=28.0, min=0.0, max=50.0, step=0.5, description='rho',
                             layout=slider_layout, continuous_update=False)
    
    ui = VBox([angle_slider, max_time_slider, N_slider, sigma_slider, rho_slider])
    out = interactive_output(update_plot, {
        'angle': angle_slider,
        'max_time': max_time_slider,
        'N': N_slider,
        'sigma': sigma_slider,
        'rho': rho_slider
    })
    return VBox([ui, fig])
    # display(ui, fig, out)