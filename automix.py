import click
import numpy as np
import soundfile as sf
import os.path
import logging
from scipy import signal

def window_rms(data, window_size):
    squared = np.power(data,np.float(2))
    window = np.ones(window_size)/np.float(window_size)
    return np.sqrt(signal.convolve(squared, window, 'same'))

def rms(data):
    return np.sqrt(np.mean(np.abs(data)**np.float(2)))

def rms_to_db(rms):
    return 20*np.log10(rms)

def db_to_float(db):
    return 10 ** (db / 20)

def ms_to_samples(ms, samplerate):
    return samplerate // 1000 * ms

@click.command()
@click.argument('files', nargs=2, type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--window', default=400, help='Window size in ms to smooth volume changes over (default 400ms)')
@click.option('--output', default='.', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True), help='Path to output automixed files (default CWD)')
@click.option('--verbose', is_flag=True, help='Show verbose progress')
def automix(files, window, output, verbose):
    """Automix takes two input mono wav files, and automatically mixes them together,
    lowering the volume of the non-speaking channel when the other is speaking to
    reduce bleed-through and comb-filtering.

    Three output files will be produced - an automixed file, and 2 files each containing
    the isolated channel but with the bleed attenuated"""

    if verbose:
        logging.basicConfig(style='{', format='{message}', level=logging.DEBUG)

    chan1, chan1_rate = sf.read(files[0])
    chan2, chan2_rate = sf.read(files[1])
    names = [os.path.splitext(os.path.basename(file))[0] for file in files]

    logging.debug(f"Processing {names[0]} and {names[1]}")

    chan1_win_rms = window_rms(chan1, ms_to_samples(window, chan1_rate))
    chan2_win_rms = window_rms(chan2, ms_to_samples(window, chan2_rate))

    combined_win_rms = chan1_win_rms + chan2_win_rms

    chan1_attenuated = chan1 * np.reciprocal(combined_win_rms/chan1_win_rms)
    chan2_attenuated = chan2 * np.reciprocal(combined_win_rms/chan2_win_rms)

    mixed = chan1_attenuated + chan2_attenuated

    logging.debug(f"Writing output files in directory \"{output}\"")

    sf.write(f"{output}/automixed-{names[0]}-{names[1]}.wav", mixed, chan1_rate, 'FLOAT')
    sf.write(f"{output}/attenuated-{names[0]}.wav", chan1_attenuated, chan1_rate, 'FLOAT')
    sf.write(f"{output}/attenuated-{names[1]}.wav", chan2_attenuated, chan2_rate, 'FLOAT')

    logging.debug("Done")
