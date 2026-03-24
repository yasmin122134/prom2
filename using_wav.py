import os

import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
# Source - https://stackoverflow.com/a/6743593
# Posted by cryo, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-23, License - CC BY-SA 4.0

from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave


THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    silence = [0] * int(seconds * RATE)
    r = array('h', silence)
    r.extend(snd_data)
    r.extend(silence)
    return r

def record():
    sample_rate = 44100
    duration = 2
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1,
                       dtype='float64')
    # waits till ur finished recording
    sd.wait(duration)
    return recording

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()



def load_mono(path):
    sr, data = wavfile.read(path)
    print("Loaded:", path, "Sample Rate:", sr)

    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
        print("Info: converted int16 to float32 in [-1, 1].")

    return sr, data

def save_float_wav(path, sr, data):
    wavfile.write(path, sr, data.astype(np.float32))


def plot_spectrogram_pair(orig, mod, sr,
                          title_orig='Original',
                          title_mod='Modified',
                          fmin=0,
                          fmax=None):

    if fmax is None:
        fmax = sr / 2  # Nyquist

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(10, 6))

    # Original
    axes[0].specgram(orig, NFFT=2048, Fs=sr, noverlap=1024)
    axes[0].set_title(title_orig)
    axes[0].set_ylabel('Frequency (Hz)')
    axes[0].set_ylim(fmin, fmax)

    # Modified
    axes[1].specgram(mod, NFFT=2048, Fs=sr, noverlap=1024)
    axes[1].set_title(title_mod)
    axes[1].set_xlabel('Time (s)')
    axes[1].set_ylabel('Frequency (Hz)')
    axes[1].set_ylim(fmin, fmax)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    print("please speak a word into the microphone")
    record_to_file('demo.wav')
    print("done - result written to demo.wav")


    sample_rate, samples = load_mono("demo.wav")
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)

    plt.pcolormesh(times, frequencies, spectrogram)
    plt.imshow(spectrogram)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()
