# TODO: Most of the util code has been moved into separate, thematic modules, but a few stragglers remain here

from astropy.table import Table
import numpy as np
from astropy.io import fits
import astropy.wcs as wcs

def sigma2fwhm(sigma):
    c = np.sqrt(8.*np.log(2))
    return c * sigma

def fwhm2sigma(fwhm):
    c = np.sqrt(8.*np.log(2))
    return fwhm / c

def get_pixel_scale(image_filename):
    '''
    use astropy.wcs to obtain the pixel scale (a/k/a plate scale)
    for the input image. Returns pixel scale in arcsec/pixels.

    image_filename: str
        FITS image for which pixel scale is desired

    Return:
    pix_scale: float
        Image pixel scale in arcsec/pixel
    '''

    # Get coadd image header
    hdr = fits.getheader(image_filename)

    # Instantiate astropy.wcs.WCS header
    w = wcs.WCS(hdr)

    # Obtain pixel scale in degrees/pix & convert to arcsec/pix
    cd1_1 = wcs.utils.proj_plane_pixel_scales(w)[0]
    pix_scale = cd1_1 * 3600

    return pix_scale

