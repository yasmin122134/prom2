import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import soundfile as sf
import threading

from scipy.signal import hilbert


def _play_array(sound, samplerate=44100):
    sound = np.asarray(sound, dtype=np.float32)
    sd.play(sound, samplerate)
    sd.wait()


def _playsound(sound, samplerate=44100):
    new_thread = threading.Thread(target=_play_array, args=(sound, samplerate))
    new_thread.start()
    return new_thread


data_freq = 3
data_amp = 1.0

base_freq = 10
base_amp = 1.0

duration = 3
def main():
    my_modulation = sine_tone(data_freq, duration)
    am_sound = am_synthesis(base_freq,base_amp, my_modulation,modulation_index=1)
    d = am_demodulate(am_sound,base_freq,base_amp,duration)


    plot_sound(my_modulation, duration, title="my modulation")
    plot_sound(am_sound, duration, title="am sound")
    plot_sound(d, 5, title="demodulation")
    t2 = _playsound(am_sound)


    # t1.join()
    t2.join()


def sine_tone(
        frequency: int=440,
        duration: float=1.0,
        amplitude: float=1.0,
        samplerate: int=44100,
) -> np.ndarray:
    n_samples = int(samplerate * duration)
    time_points = np.linspace(0, duration, n_samples,False)
    sine = np.sin(2 * np.pi * frequency * time_points)
    sine *= amplitude
    return sine

def am_synthesis(
        carrier_frequency: float,
        carrier_amplitude: float,
        modulator_wave: np.array,
        modulation_index: float=0.5,
        amplitude: float=0.5,
        sample_rate: int=44100,
) -> np.ndarray:
    total_samples = len(modulator_wave)
    time_points = np.arange(total_samples) / sample_rate
    carrier_wave = np.sin(2 * np.pi * carrier_frequency * time_points) * carrier_amplitude
    am_wave = (1+modulation_index * modulator_wave) * carrier_wave
    max_amplitude = np.max(np.abs(am_wave))
    am_wave = amplitude * (am_wave / max_amplitude)
    return am_wave

from scipy.signal import butter,filtfilt
def am_demodulate(sig_am, carrier_frequency, carrier_amp, duration, sample_rate=44100):
    b, a = butter(len(sig_am), 2 / (sample_rate * 0.5), btype='low', analog=False)
    demodulated_signal = filtfilt(b, a, sig_am)
    return demodulated_signal


def fm_synthesis(
        carrier_frequency: float,
        modulator_wave: np.array,
        modulation_index: float=3,
        amplitude: float=0.5,
        sample_rate: int=44100,
) -> np.ndarray:
    total_samples = len(modulator_wave)
    time_points = np.arange(total_samples) / sample_rate
    fm_wave = np.sin(2 * np.pi * carrier_frequency * time_points + modulation_index * modulator_wave)
    max_amplitude = np.max(np.abs(fm_wave))
    fm_wave = amplitude * (fm_wave / max_amplitude)
    return fm_wave

def plot_sound(sound, duration, samplerate=44100,title=" "):
    n_samples = int(samplerate * duration)
    time_points = np.linspace(0, duration, n_samples,False)
    plt.plot(time_points, sound)
    plt.title(title)
    plt.show()





def fm_demodulate(sig_fm, sample_rate=44100):
    total_samples = len(sig_fm)
    time = np.arange(total_samples) / sample_rate
    y_d = np.gradient(sig_fm, time)
    y_envelop = np.abs(hilbert(y_d))
    plt.plot(y_envelop,y_d)
    plt.show()
    print(np.shape(y_envelop), np.shape(y_d))
    return y_envelop

def transfer(freq_amp_by_time_segment):
    duration = 5

    to_play = []
    for t in freq_amp_by_time_segment:
        for k, v in t.items():
            sine = sine_tone(k,duration,v)
            to_play.append(_playsound(sine))
        for th in to_play:
            th.join()
        to_play = []






if __name__ == "__main__":
    main()
    freq_amp_by_time_segment = [{
        100: 1,
        110: 1,
        120: 1,
        130: 1,
        140: 1,
        150: 1,
        160: 1,
        170: 1,
        180: 1,
        190: 1,
        200: 1,
    },
        {
            100: 1,
            110: 0,
            120: 1,
            130: 1,
            140: 1,
            150: 0,
            160: 1,
            170: 1,
            180: 0,
            190: 1,
            200: 0,
        },
        {
            100: 0,
            110: 0,
            120: 0,
            130: 0,
            140: 0,
            150: 1,
            160: 1,
            170: 1,
            180: 1,
            190: 1,
            200: 1,
        },
        {
            100: 1,
            110: 1,
            120: 1,
            130: 1,
            140: 1,
            150: 1,
            160: 0,
            170: 0,
            180: 0,
            190: 0,
            200: 0,
        },
    ]
    # transfer(freq_amp_by_time_segment)
