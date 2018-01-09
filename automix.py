import click
import numpy as np
import soundfile as sf
import os.path
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
@click.argument('files', nargs=2, type=click.Path(readable=True))
def automix(files):
    chan1, chan1_rate = sf.read(files[0])
    chan2, chan2_rate = sf.read(files[1])
    names = [os.path.splitext(os.path.basename(file))[0] for file in files]

    chan1_win_rms = window_rms(chan1, ms_to_samples(400, chan1_rate))
    chan2_win_rms = window_rms(chan2, ms_to_samples(400, chan2_rate))

    combined_win_rms = chan1_win_rms + chan2_win_rms

    chan1_attenuated = chan1 * np.reciprocal(combined_win_rms/chan1_win_rms)
    chan2_attenuated = chan2 * np.reciprocal(combined_win_rms/chan2_win_rms)

    mixed = chan1_attenuated + chan2_attenuated

    sf.write(f"automixed-{names[0]}-{names[1]}.wav", mixed, chan1_rate, 'FLOAT')
    sf.write(f"attenuated-{names[0]}.wav", chan1_attenuated, chan1_rate, 'FLOAT')
    sf.write(f"attenuated-{names[1]}.wav", chan2_attenuated, chan2_rate, 'FLOAT')
