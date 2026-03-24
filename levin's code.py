import pandas as pd
from scipy.fft import rfft, rfftfreq
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import stft


def get_info(path, is_acce=False):
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    if is_acce:
        moveX = df['Linear Acceleration x (m/s^2)'].tolist()[500:-500]
    else:
        moveX = df['Gyroscope x (rad/s)'].tolist()[500:-500]
    time = df['Time (s)'].tolist()[500:-500]

    print("\n")
    print("Avarage:" , np.mean(moveX))
    print("Max:" , np.max(moveX))

    DURATOIN = time[-1] - time[0]
    N_SAMPLE = len(time)
    print(N_SAMPLE,DURATOIN)
    SAMPLE_RATE = N_SAMPLE / DURATOIN
    print("samples rate:", SAMPLE_RATE)

    f, t, Zxx = stft(moveX, fs=SAMPLE_RATE, nperseg=256)

    plt.plot(time, moveX)
    plt.title(f'{path}, before FFT')
    plt.show()

    plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
    plt.ylabel('Hz')
    plt.xlabel('Sec')
    plt.title(f'{path}, FFT')
    plt.show()


# get_info("exp_data/no_sound_1.csv")
# get_info("exp_data/no_sound_2.csv")
# get_info("exp_data/sound_500.csv")
# get_info("exp_data/sound_15000.csv")
# get_info("exp_data/zzz.csv")
# get_info("exp_data/zzz2.csv")
# get_info("exp_data/zzz3.xlsx")
# get_info("exp_data/aaa.xls")
# get_info("exp_data/sound_80.xls")
# get_info("exp_data/acceleration_80.xls", True)
# get_info("exp_data/sound_100.xls")
# get_info("exp_data/accel_98.xls", True)
get_info("exp_data/sound_150_120.xls")