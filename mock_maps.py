import numpy as np
import matplotlib.pyplot as plt
import healpy as hp
import astropy.units as u
import random
import time
import datetime
import os
import sys

import tools
import ellisbaldwin
import dipole
from qso_sample import QSOSample
from multipoles import compute_Cells_in_overdensity_map_Lambda, reconstruct_map, multipole_map

NSIDE = 64  # default nside

def functional_test():
    rng = np.random.default_rng(17) # the most random number
    exp_dip = generate_expected_dipole_map(.1)
    sph_harm_amp_dict = get_sph_harm_amp_dict(np.zeros(10) + 1e-4, rng)
    overdensity_map = generate_smooth_overdensity_map(sph_harm_amp_dict)
    selfunc_map = np.ones(hp.nside2npix(NSIDE))
    base_rate = 35.
    mock_map = generate_map(overdensity_map, base_rate, selfunc_map, rng)
    fig = plt.figure()
    hp.mollview(mock_map, fig=fig)
    fig.savefig('mock_maps_functional_test.png')
    
def generate_expected_dipole_map(dipole_amplitude, nside=NSIDE):
    """
    Parameters
    ----------
    dipole_amplitude : float
        The amplitude of the dipole in the normal convention (not the alm convention),
        depends on the number counts.
    """
    amps = np.zeros(4)
    amps[1:] = dipole.cmb_dipole(amplitude=dipole_amplitude, return_amps=True)
    return dipole.dipole_map(amps, NSIDE=nside)

def get_sph_harm_amp_dict(Cells, rng):
    """
    Parameters
    ----------
    Cells : ndarray, type float, shape (ellmax-1,)
        Cells for ell = 1, 2, ..., ellmax
        Note: 1-indexed
    """
    sph_harm_amp_dict = {}
    for ell in range(1, len(Cells)+1):
        sph_harm_amp_dict[ell] = np.sqrt(Cells[ell-1]) * rng.normal(size=2 * ell + 1)
    return sph_harm_amp_dict

def generate_smooth_overdensity_map(sph_harm_amp_dict, nside=NSIDE):
    """
    Parameters
    ----------
    sph_harm_amp_dict : dict
        Generated by get_sph_harm_amp_dict().
    nside : int, optional
    """
    mock_map = np.zeros((hp.nside2npix(nside)))
    for ell in sph_harm_amp_dict.keys():
        alms = sph_harm_amp_dict[ell]
        assert len(alms) == 2 * ell + 1, \
            f"incorrect number of coefficients for ell={ell} ({len(alms)}, expected {2 * ell + 1}"
        mock_map += multipole_map(alms)
    return mock_map

def generate_map(overdensity_map, base_rate, selfunc_map, rng):
    """
    Parameters
    ----------
    overdensity_map : healpix map
        Sum of expected dipole map and smooth_overdensity_map().
    base_rate : float
        Quasar rate per pixel in the overdensity=0, selection function=1 regions of the sky.
    selfunc_map : healpix map
        Selection function (mask or continuous).
    rng : numpy random number generator
    
    Bugs/Comments
    --------------
    - This function will only operate if there's a global variable called NSIDE.
    - If overdensity_map < -1 anywhere, this code will fail.
    """
    return rng.poisson((1. + overdensity_map) * base_rate * selfunc_map)


if __name__ == '__main__':
    functional_test()