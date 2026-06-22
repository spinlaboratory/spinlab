import numpy as _np
import matplotlib.pyplot as _plt
from matplotlib.widgets import Button, Slider

from ..plotting.colors import BrukerPacific, BrukerDolomite


def show_sphere_orientations(theta, phi):
    r"""Display orientations on a unit sphere with interactive rotation sliders.

    Args:
        theta (array_like): Polar angles in radians.
        phi (array_like): Azimuthal angles in radians.

    Returns:
        Figure: Matplotlib figure with 3D scatter plot.

    """
    x = _np.sin(theta) * _np.cos(phi)
    y = _np.sin(theta) * _np.sin(phi)
    z = _np.cos(theta)
    dots = _np.column_stack([x, y, z])

    u = _np.linspace(0, 2 * _np.pi, 60)
    v = _np.linspace(0, _np.pi, 30)
    xs = _np.outer(_np.sin(v), _np.cos(u))
    ys = _np.outer(_np.sin(v), _np.sin(u))
    zs = _np.outer(_np.cos(v), _np.ones_like(u))

    fig = _plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    fig.subplots_adjust(bottom=0.3)

    ax.plot_surface(xs, ys, zs, color=BrukerDolomite, alpha=0.3, edgecolor="none")

    def _camera_vector(azim, elev):
        a = _np.deg2rad(azim)
        e = _np.deg2rad(elev)
        return _np.array([_np.cos(e) * _np.cos(a), _np.cos(e) * _np.sin(a), _np.sin(e)])

    cam = _camera_vector(ax.azim, ax.elev)
    visible = dots @ cam > 0
    scatter = ax.scatter(
        x[visible], y[visible], z[visible],
        s=10, color=BrukerPacific, depthshade=False, zorder=10,
    )

    ax.set_aspect("equal")
    ax.axis("off")

    ax_azim = fig.add_axes([0.2, 0.12, 0.6, 0.03])
    ax_elev = fig.add_axes([0.2, 0.06, 0.6, 0.03])
    slider_azim = Slider(ax_azim, "Azimuth", -180, 180, valinit=ax.azim)
    slider_elev = Slider(ax_elev, "Elevation", -90, 90, valinit=ax.elev)

    def _update(_val):
        ax.view_init(elev=slider_elev.val, azim=slider_azim.val)
        cam = _camera_vector(slider_azim.val, slider_elev.val)
        visible = dots @ cam > 0
        scatter._offsets3d = (x[visible], y[visible], z[visible])
        fig.canvas.draw_idle()

    slider_azim.on_changed(_update)
    slider_elev.on_changed(_update)

    ax_reset = fig.add_axes([0.2, 0.19, 0.08, 0.04])
    btn_reset = Button(ax_reset, "Reset", hovercolor="lightgrey")
    btn_reset.label.set_fontsize(8)

    def _reset(_event):
        slider_azim.reset()
        slider_elev.reset()

    btn_reset.on_clicked(_reset)

    fig._widgets = (slider_azim, slider_elev, btn_reset)

    _plt.show()

    return fig
