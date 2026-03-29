import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import sounddevice as sd
import soundfile as sf
import threading
from scipy.signal import butter,filtfilt
from scipy.signal import hilbert, chirp


def _play_array(sound, samplerate=44100):
    sound = np.asarray(sound, dtype=np.float32)
    sd.play(sound, samplerate)
    sd.wait()


def _playsound(sound, samplerate=44100):
    new_thread = threading.Thread(target=_play_array, args=(sound, samplerate))
    new_thread.start()
    return new_thread


data_freq = 100
data_amp = 1.0

base_freq = 150
base_amp = 1.0

duration = 10
def main():
    original_sound = sine_tone(data_freq, duration)
    am_sound = am_synthesis(base_freq, original_sound,modulation_index=1)
    demodulate = am_demodulate(am_sound,modulation_index=1)

    plot_sound(original_sound, duration, title="original sound")
    plot_sound(am_sound, duration, title="am sound")
    plot_sound(demodulate, duration, title="demodulation")

    t1 = _playsound(am_sound)
    t2 = _playsound(demodulate)


    t1.join()
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
        modulator_wave: np.array,
        modulation_index: float=1,
        sample_rate: int=44100,
) -> np.ndarray:
    total_samples = len(modulator_wave)
    time_points = np.arange(total_samples) / sample_rate
    carrier_wave = np.sin(2 * np.pi * carrier_frequency * time_points)
    am_wave = (1+modulation_index * modulator_wave) * carrier_wave
    return am_wave


def am_demodulate(sig_am, modulation_index):
    wave_without_carrier = np.abs(hilbert(sig_am))
    result = (wave_without_carrier-1)/modulation_index
    return result


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
    # main()
    N, T = 100000, 0.01  # number of samples and sampling interval for 10 s signal
    t = np.arange(N) * T  # timestamps

    x_lin = chirp(t, f0=6, f1=1, t1=10, method='linear')
    print(x_lin)
    sd.play(x_lin)
    sd.wait()

    fg0, ax0 = plt.subplots()
    ax0.set_title(r"Linear Chirp from $f(0)=6\,$Hz to $f(10)=1\,$Hz")
    ax0.set(xlabel="Time $t$ in Seconds", ylabel=r"Amplitude $x_\text{lin}(t)$")
    ax0.plot(t, x_lin)
    plt.show()

    # freq_amp_by_time_segment = [{
    #     150: 0.5,
    # },
    #     {
    #         150: 0,
    #     },
    #     {
    #         150: 1,
    #     },
    #     {
    #         150: 0,
    #     },
    # ]
    # transfer(freq_amp_by_time_segment)
