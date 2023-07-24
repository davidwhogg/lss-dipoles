"""
Helper functions.
"""

import numpy as np
from astropy.table import Table
import os
import healpy as hp
from healpy.newvisufunc import projview

def load_catalog_as_map(filename, frame='icrs', NSIDE=64):
    tab = Table.read(filename, format='fits')
    if frame=='galactic':
        try:
            lon, lat = tab['l'], tab['b']
        except KeyError:
            print("galactic coordinates not found, defaulting to ICRS")
            frame = 'icrs'
    else:
        assert frame=='icrs', "invalid 'frame'"
        lon, lat = tab['ra'], tab['dec']
    # format into healpy map
    pix_idx = hp.ang2pix(NSIDE, lon, lat, lonlat=True)
    hpmap = np.bincount(pix_idx, minlength=hp.nside2npix(NSIDE))
    return hpmap


def flatten_map(sf_map):
    newarr = np.array([row[0] for row in sf_map])
    return np.reshape(newarr, (newarr.size,))


def plot_map(map, projection_type='mollweide', coord=['C'],
             graticule=True, graticule_labels=True, **kwargs):
    projview(map, projection_type=projection_type, coord=coord,
             graticule=graticule, graticule_labels=graticule_labels, **kwargs)

def lstsq(Y, A, Cinv):
    """
    Return the least-squares solution to a linear matrix equation,
    given data Y, design matrix A, and inverse covariance Cinv.
    BUG:
    - This should catch warnings and errors in the `res` object.
    """
    if len(Cinv.shape)==1:
        a = A.T @ (Cinv[:,None] * A)
        b = A.T @ (Cinv * Y)
    else:
        a = A.T @ Cinv @ A
        b = A.T @ Cinv @ Y
    res = np.linalg.lstsq(a, b, rcond=None)
    return res[0], a