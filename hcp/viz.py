import os.path as op

import numpy as np

from mne.io.pick import _pick_data_channels, pick_info
from mne import read_trans, read_surface
from mne.transforms import apply_trans

from .io import read_info_hcp


def plot_coregistration(subject, anatomy_path, recordings_path,
                        hcp_path=op.curdir,
                        info_from=(('data_type', 'rest'), ('run_index', 0)),
                        view_init=(('azim', 0), ('elev', 0))):
    """ A diagnostic plot to show the HCP coregistration

    Parameters
    ----------

    subject : str
        The subject
    anatomy_path : str
        The path corresponding to MNE/freesurfer SUBJECTS_DIR (to be created)
    hcp_path : str
        The path where the HCP files can be found. defaults to op.curdir.
    info_from : tuple of tuples | dict
        The reader info concerning the data from which sensor positions
        should be read.
        Must not be empty room as sensor positions are in head
        coordinates for 4D systems, hence not available in that case.
        Note that differences between the sensor positions across runs
        are smaller than 12 digits, hence negligible.
    view_init : tuple of tuples | dict
        The initival view, defaults to azimuth and elevation of 0,
        a simple lateral view
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    if isinstance(info_from, tuple):
        info_from = dict(info_from)
    if isinstance(view_init, tuple):
        view_init = dict(view_init)

    head_mri_t = read_trans(
        op.join(recordings_path, subject,
                '{}-head_mri-trans.fif'.format(subject)))

    info = read_info_hcp(subject=subject, hcp_path=hcp_path, **info_from)

    info = pick_info(info, _pick_data_channels(info, with_ref_meg=False))
    sens_pnts = np.array([c['loc'][:3] for c in info['chs']])
    sens_pnts = apply_trans(head_mri_t, sens_pnts)
    sens_pnts *= 1e3  # put in mm scale

    pnts, tris = read_surface(
        op.join(anatomy_path, subject, 'bem', 'inner_skull.surf'))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(*sens_pnts.T, color='purple', marker='o')
    ax.scatter(*pnts.T, color='green', alpha=0.3)
    ax.view_init(**view_init)
    fig.tight_layout()
    return fig
