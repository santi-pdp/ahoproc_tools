"""
Here are the main options to interpolate Ahocoder features
(either can be lf0 or voided-frequency).
"""

from __future__ import print_function
import numpy as np
import argparse
import os

def linear_interpolation(tbounds, fbounds):
    """Linear interpolation between the specified bounds"""
    interp = []
    for t in range(tbounds[0],tbounds[1]):
        interp.append(fbounds[0] + (t - tbounds[0])*((fbounds[1] - fbounds[0]) /
                                                     (tbounds[1] - tbounds[0])))
    return interp

def interpolation(signal, unvoiced_symbol):
    tbound = [None, None]
    fbound = [None, None]
    signal_t_1 = signal[0]
    isignal = np.copy(signal)
    for t in range(1, signal.shape[0]):
        if signal[t] > unvoiced_symbol and signal_t_1 <= unvoiced_symbol and tbound == [None, None]:
            # First part of signal is unvoiced, set to constant first voiced
            isignal[:t] = signal[t]
        elif signal[t] <= unvoiced_symbol and signal_t_1 > unvoiced_symbol:
            tbound[0] = t - 1
            fbound[0] = signal_t_1
        elif signal[t] > unvoiced_symbol and signal_t_1 <= unvoiced_symbol:
            tbound[1] = t
            fbound[1] = signal[t]
            isignal[tbound[0]:tbound[1]] = linear_interpolation(tbound, fbound)
            # reset values
            tbound = [None, None]
            fbound = [None, None]
        signal_t_1 = signal[t]
    # now end of signal if necessary
    if tbound[0] is not None:
        isignal[tbound[0]:] = fbound[0]
    return isignal


def process_guia(guia_file, unvoiced_symbol):
    # Interpolate files values
    with open(guia_file) as fh:
        for i, filename in enumerate(fh):
            if i == 0:
                dire, fullname = os.path.split(filename.rstrip())
            basename, ext = os.path.splitext(fullname)
            raw = np.loadtxt(filename.rstrip())
            interp = interpolation(raw, unvoiced_symbol)
            np.savetxt(os.path.join(dire, basename + '.i' + ext), interp)
            print('Writing interplation to {}'.format(os.path.join(dire,
                                                                   basename +
                                                                   '.i' + ext)))
    return interp

def main(opts):
    if opts.f0_guia:
        process_guia(opts.f0_guia, -10000000000)
    if opts.vf_guia:
        process_guia(opts.vf_guia, 1e3)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Here are the main options to interpolate'
                                     ' Ahocoder features')
    parser.add_argument('--f0_guia', type=str,
                        default=None, help='Guia file containing pointers to '
                                            'the different lf0 files to '
                                            'interpolate.')
    parser.add_argument('--vf_guia', type=str,
                        default=None, help='Guia file containing pointers to '
                                           'the different vf files to '
                                           'interpolate.')
    """
    TODO: add this?
    parser.add_argument('--no-uv', dest='gen_uv',
                        action='store_false', help='U/V masks are NOT '
                                                   'generated.')
    """
    parser.set_defaults(gen_uv=True)
    opts = parser.parse_args()
    main(opts)
