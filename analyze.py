import numpy as np
import scipy
from scipy.signal import hilbert
import pandas as pd
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.signal import stft
from scipy.fft import rfft, rfftfreq,irfft

def am_demodulate(sig_am, modulation_index):
    wave_without_carrier = np.abs(hilbert(sig_am))
    result = (wave_without_carrier - 1) / modulation_index
    return result


def plot_sound(sound, time_points, title=" "):
    plt.plot(time_points, sound)
    plt.title(title)
    plt.show()


def extract_data(path, is_acce=False, axis='x'):
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    if is_acce:
        moveX = df[f'Linear Acceleration {axis} (m/s^2)'].tolist()[500:-500]
    else:
        moveX = df[f'Gyroscope {axis} (rad/s)'].tolist()[500:-500]

    time = df['Time (s)'].tolist()[500:-500]
    f,t,Zxx = calc_FFT(time, moveX, "fft on the AM demodulation of " + path + " axis: " + axis)
    row150 = np.abs(np.array(Zxx[150]))
    reversed_fft = irfft(row150, len(time))
    result = am_demodulate(np.abs(reversed_fft), 1)
    plot_sound(result, time, title=f"AM demodulation of {path}")
    sd.play(result, 44100)
    sd.wait()
    result = np.abs(result)
    time = time[100:-100]
    result = result[100:-100]

    f = rfft(result, len(time))
    f = np.abs(f)
    print(f)
    plt.plot(f)
    plt.show()
    plot_sound(f, time, title=f"FFT demodulation of {path}")



def calc_FFT(time, moveX, message):
    print("\n")
    print("Avarage:" , np.mean(moveX))
    print("Max:" , np.max(moveX))

    DURATOIN = time[-1] - time[0]
    N_SAMPLE = len(time)
    print(N_SAMPLE,DURATOIN)
    SAMPLE_RATE = N_SAMPLE / DURATOIN
    print("samples rate:", SAMPLE_RATE)


    yf = rfft(moveX)
    xf = rfftfreq(N_SAMPLE, 1/SAMPLE_RATE)

    plt.plot(xf, np.abs(yf))
    plt.xlabel('Hrz')
    plt.ylabel('Amplitude')
    plt.title(message)
    plt.show()

    SAMPLE_RATE = round(SAMPLE_RATE)
    f, t, Zxx = stft(moveX, fs=SAMPLE_RATE, nperseg=SAMPLE_RATE, window='hann')
    print("Zxx size\n",np.shape(Zxx), "\n")
    abss = np.abs(Zxx[150])
    print(abss)
    sorted = np.sort(abss)
    print("max value:", np.max(abss))
    print("min value:", np.min(abss))
    a = (np.max(abss) - np.min(abss))/3
    b = a * 2
    c = a * 3
    # for i in range(np.size(abss)):
    #     if abss[i] < a:
    #         Zxx[150][i] = 0
    #     if b > abss[i] > a:
    #         Zxx[150][i] = 0.5
    #     if abss[i] > b:
    #         Zxx[150][i] = 1
    print("devided by 3: ", a)
    print("\n sorted: \n",sorted)
    print(f)
    plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
    plt.ylabel('Hz')
    plt.xlabel('Sec')
    plt.title(message)
    plt.show()
    return f, t, Zxx


extract_data("exp_data/our_sound_1.xls", axis="y")