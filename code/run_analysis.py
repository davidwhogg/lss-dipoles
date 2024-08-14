"""
# run multiple analyses of mocks and real data

## License
Copyright 2024 The authors.
This code is released for re-use under the open-source MIT License.

## Authors:
- **Abby Williams** (Chicago)
- **David W. Hogg** (NYU)
- **Kate Storey-Fisher** (DIPC)

## To-do / bugs / projects / comments
- This code has no clobber mode; if you want to overwrite the files you must delete them first.
- The `for` loops here should me `map()`.
- Name synchronization between the analyses on the mocks and the real data (which "deeply upsets" Hogg).
"""

import numpy as np
import glob
import os
from pathlib import Path

import generate_mocks as gm
import dipole
import tools


def main():

    analyze_mocks(overwrite=False)
    analyze_data(overwrite=False)

def analyze_mocks(overwrite=False):
    """
    Analyzes the mock data generated by the `generate_mocks` module.

    This function is a wrapper of the analysis function 'analyze' for the mock data;
    it reads the mock data from the specified directory for the set of cases in
    'case_set()' and loops over them.

    Parameters:
        overwrite (bool)

    Returns:
        None
    """
    dir_mocks = '../data/mocks'
    dir_results = '../results/results_mocks'
    Path.mkdir(Path(dir_results), exist_ok=True, parents=True)

    case_dicts = gm.case_set(set_name='full')

    for case_dict in case_dicts:
        pattern = f"{dir_mocks}/*{case_dict['tag']}*.npy"
        fns_mock = glob.glob(pattern)
        for i, fn_mock in enumerate(fns_mock):
            fn_res = os.path.join(dir_results, f"dipole_comps_lambdas_" + fn_mock.split('/')[-1])
            if os.path.exists(fn_res) and not overwrite:
                # wouldn't work if we switch to map
                continue
            print(f"analyze_mocks(): reading file {fn_mock}")
            mock = np.load(fn_mock, allow_pickle=True)

            Lambdas, comps = analyze(mock, case_dict)
            result_dict = {
                "Lambdas" : Lambdas,
                "dipole_comps" : comps
            }
            print(f"analyze_mocks(): writing file {fn_res}")
            np.save(fn_res, result_dict)

def analyze_data(overwrite=False):
    """
    Analyzes the data from the specified catalog file and saves the results.

    This function is a wrapper of the analysis function 'analyze' for the data;
    there are cases for both quaia and catwise to pull the proper paths.

    Parameters:
        overwrite (bool)

    Returns:
        None
    """
    # quaia settings
    catalog_name = 'quaia_G20.0'
    fn_cat = '../data/catalogs/quaia/quaia_G20.0.fits'
    selfunc_mode = 'quaia_G20.0_orig'

    #catwise settings
    # catalog_name = 'catwise'
    # fn_cat = f'../data/catalogs/catwise_agns/catwise_agns_master.fits'
    # selfunc_mode = 'catwise_zodi'

    nside = 64  # magic
    dir_results = '../results/results_data'
    Path.mkdir(Path(dir_results), exist_ok=True, parents=True)
    qmap = tools.load_catalog_as_map(fn_cat, frame='icrs', NSIDE=nside)
    case_dict = {
        "catalog_name": catalog_name, #maybe we shouldnt need this here...? think about it!
        "selfunc_mode": selfunc_mode, #this also multiplies in the mask
        "tag": f"_case-{selfunc_mode}"
    }
    fn_res = os.path.join(dir_results, f"dipole_comps_lambdas_{case_dict['catalog_name']}{case_dict['tag']}.npy")
    if os.path.exists(fn_res) and not overwrite:
        return
    Lambdas, comps = analyze(qmap, case_dict)
    result_dict = {
        "Lambdas" : Lambdas,
        "dipole_comps" : comps
    }
    np.save(fn_res, result_dict)
    print("Saved results to", fn_res)

def analyze(qmap, case_dict):
    Lambdas = np.geomspace(1e-3, 1e0, 33)
    comps = np.zeros((len(Lambdas), 3))
    for i, Lambda in enumerate(Lambdas):
        comps[i] = dipole.measure_dipole_in_overdensity_map_Lambda(qmap,
                                                                   selfunc=gm.get_selfunc_map(case_dict['selfunc_mode']), Lambda=Lambda)
    return Lambdas, comps

if __name__ == "__main__":
    main()