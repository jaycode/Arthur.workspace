"""
Helper functions
"""
import numpy as np

def format_size(num, suffix='B'):
    """Human readable bytesizes.
    """
    for unit in ['','Ki','Mi','Gi','TBi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def unique_rows(a):
    """Unique rows numpy array.

    Converts [[1,1], [1,1], [1,2], [2,1], [2,1]] into [[1,1], [1,2], [2,1]]

    Reference: http://stackoverflow.com/a/8567929/278191

    """
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))