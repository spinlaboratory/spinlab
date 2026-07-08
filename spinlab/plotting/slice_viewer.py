import numpy as _np
import matplotlib.pyplot as _plt
from matplotlib.widgets import Slider as _Slider

from .colors import BrukerPacific


def slice_viewer(data, scroll_dim=None):
    """Interactive viewer for 2D SpinData objects with a slider to scroll
    through one dimension.

    Args:
        data (SpinData): 2D SpinData object.
        scroll_dim (str, optional): Dimension to scroll through. If None,
            the first dimension is used.

    Returns:
        Figure: Matplotlib figure.

    Examples:

        View a 2D data set, scrolling through the 'idx' dimension:

        >>> sl.slice_viewer(data, scroll_dim='idx')

    """
    if data.ndim != 2:
        raise ValueError(f"slice_viewer requires 2D data, got {data.ndim}D.")

    if scroll_dim is None:
        scroll_dim = data.dims[0]

    scroll_idx = data.dims.index(scroll_dim)
    plot_dim = data.dims[1 - scroll_idx]

    scroll_coord = data.coords[scroll_dim]
    plot_coord = data.coords[plot_dim]
    n_slices = len(scroll_coord)

    fig, ax = _plt.subplots()
    fig.subplots_adjust(bottom=0.25)

    def _get_slice(i):
        if scroll_idx == 0:
            return data.values[i, :]
        return data.values[:, i]

    slice_data = _get_slice(0)
    if _np.iscomplexobj(slice_data):
        (line_re,) = ax.plot(
            plot_coord, slice_data.real, color=BrukerPacific, label="Re"
        )
        (line_im,) = ax.plot(
            plot_coord, slice_data.imag, color="grey", alpha=0.6, label="Im"
        )
        ax.legend(loc="upper right", fontsize=10)
    else:
        (line_re,) = ax.plot(plot_coord, slice_data, color=BrukerPacific)
        line_im = None

    ax.set_xlabel(plot_dim)
    ax.set_ylabel("Intensity")
    ax.set_title(f"{scroll_dim} = {scroll_coord[0]:.6g}")
    ax.grid(True, ls=":")

    ax_slider = fig.add_axes([0.2, 0.08, 0.6, 0.03])
    slider = _Slider(
        ax_slider,
        scroll_dim,
        0,
        n_slices - 1,
        valinit=0,
        valstep=1,
        valfmt="%d",
    )

    def _update(_val):
        i = int(slider.val)
        s = _get_slice(i)
        if _np.iscomplexobj(s):
            line_re.set_ydata(s.real)
            if line_im is not None:
                line_im.set_ydata(s.imag)
        else:
            line_re.set_ydata(s)
        ax.set_title(f"{scroll_dim} = {scroll_coord[i]:.6g}")
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()

    slider.on_changed(_update)

    fig._widgets = (slider,)

    _plt.show()

    return fig
