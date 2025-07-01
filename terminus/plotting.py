'''
A collection of helper methods and classes for simplified plotting calls
'''

import matplotlib.pyplot as plt

from pathlib import Path

class MidpointNormalize(colors.Normalize):
    '''
    Normalise the colorbar so that diverging bars work there way either side 
    from a prescribed midpoint value)

    e.g.:
    im = ax1.imshow(
       array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100)
       )

    Parameters
    ----------
    vmin : float
        Minimum value of the color scale.
    vmax : float
        Maximum value of the color scale.
    midpoint : float, optional
        The value at which the color scale is centered. Default is 0.
    clip : bool, optional
        Whether to clip values outside the range [vmin, vmax]. Default is False.
    '''

    def __init__(self, vmin, vmax, midpoint=0, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

        return

    def __call__(self, value, clip=None):

        try:
            normalized_min = max(
                0,
                1 / 2 * (
                    1 - abs((self.midpoint - self.vmin) / (self.midpoint - self.vmax))
                    )
                )
        except ZeroDivisionError:
            normalized_min = self.midpoint-1

        try:
            normalized_max = min(
                1,
                1 / 2 * (
                    1 + abs((self.vmax - self.midpoint) / (self.midpoint - self.vmin))
                    )
                )
        except ZeroDivisionError:
            normalized_max = self.midpoint+1

        normalized_mid = 0.5
        x = [self.vmin, self.midpoint, self.vmax]
        y = [normalized_min, normalized_mid, normalized_max]

        return np.ma.masked_array(np.interp(value, x, y))


def plot(show, out_file=None, overwrite=False, dpi=300):
    '''
    Helper function to streamline plotting options

    Parameters
    ----------
    show : bool
        Whether to display the plot.
    overwrite : bool
        Whether to overwrite existing files.
        Default is False.
    out_file : str
        The output file to save the plot to, if desired. Default is None; the 
        plot will not be saved.
    dpi : int
        The resolution of the plot. Default is 300.
    '''

    if out_file is not None:
        if overwrite is False and Path(out_file).exists():
            raise FileExistsError(
                f'{out_file} already exists and overwrite is set to False.'
            )
        plt.savefig(out_file, dpi=dpi)

    if show is True:
        plt.show()
    else:
        plt.close()

    return
