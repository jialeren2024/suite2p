import numpy as np

from .masks import circle_mask
from .utils import fitMVGaus


def mean_r_squared(y, x, estimator=np.median):
    return np.mean(np.sqrt((y - estimator(y)) ** 2 + ((x - estimator(x)) ** 2)))


def roi_stats(ops, stats):
    """ computes statistics of ROIs

    Parameters
    ----------
    ops : dictionary
        'aspect', 'diameter'

    stats : dictionary
        'ypix', 'xpix', 'lam'

    Returns
    -------
    stat : dictionary
        adds 'npix', 'npix_norm', 'med', 'footprint', 'compact', 'radius', 'aspect_ratio'

    """
    if 'aspect' in ops:
        d0 = np.array([int(ops['aspect']*10), 10])
    else:
        d0 = ops['diameter']
        if isinstance(d0, int):
            d0 = [d0,d0]

    rs = circle_mask(np.array([30, 30]))
    rsort = np.sort(rs.flatten())
    for stat in stats:
        ypix, xpix, lam = stat['ypix'], stat['xpix'], stat['lam']

        # compute compactness of ROI
        mrs_val = mean_r_squared(y=ypix, x=xpix)
        stat['mrs'] = mrs_val
        stat['mrs0'] = np.mean(rsort[:ypix.size])
        stat['compact'] = stat['mrs'] / (1e-10 + stat['mrs0'])
        stat['med'] = [np.median(ypix), np.median(xpix)]
        stat['npix'] = xpix.size
        if 'radius' not in stat:
            radius = fitMVGaus(ypix / d0[0], xpix / d0[1], lam, 2)[2]
            stat['radius'] = radius[0] * d0.mean()
            stat['aspect_ratio'] = 2 * radius[0]/(.01 + radius[0] + radius[1])


    mmrs = np.nanmedian([stat['mrs'] for stat in stats[:100]])  # todo: why only include the first 100?
    for stat in stats:
        stat['mrs'] = stat['mrs'] / (1e-10 + mmrs)

    npix = np.array([stat['npix'] for stat in stats], dtype='float32')
    npix /= np.mean(npix[:100])  # todo: why only include the first 100?
    for stat, npix0 in zip(stats, npix):
        stat['npix_norm'] = npix0

    for stat in stats:
        if 'footprint' not in stat:
            stat['footprint'] = 0

    return np.array(stats)