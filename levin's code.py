import pandas as pd
from scipy.fft import rfft, rfftfreq
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import stft

# COLD_THRESH = 0.0001
jump_size = 5
potential_bits = []
for i in range(0,205,jump_size):
    potential_bits.append(i)
print("potential bits:", potential_bits)
# potential_bits = [150, 155, 160, 165, 170, 175, 180, 185, 190, 195]
THRESH = 2.5

def get_info(path, is_acce=False):
    axises = ['x', 'y', 'z']
    bits = []
    for axis in axises:
        cur_bits = extract_data(path, is_acce=is_acce, axis=axis)
        for bit in cur_bits:
            if bit not in bits:
                bits.append(bit)
    print("the bits detedted are: ", bits)
    return bits




def extract_data(path, is_acce=False, axis='x'):
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    if is_acce:
        moveX = df[f'Linear Acceleration {axis} (m/s^2)'].tolist()
    else:
        moveX = df[f'Gyroscope {axis} (rad/s)'].tolist()
    time = df['Time (s)'].tolist()
    message = f'{path}, FFT, axis={axis}'
    f, t, Zxx = calc_FFT(time, moveX,message)
    return get_bits(f, t, Zxx)

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


def find_threshold(arr):
    max_val = np.max(arr)
    min_val = np.min(arr)
    threshold = (max_val + min_val) / 2
    return threshold

def find_hot(abs_arr,cold_thresh, window=5):
    x = []
    ind = []
    for j in range(0, np.shape(abs_arr)[0]):
        a = abs_arr[j][window]
        x.append(a)
        ind.append(j)
    hot = []
    for i in range(0, np.size(x)):
        if x[i] >= cold_thresh:
            hot.append(i)
    return hot


def find_hot2(abs_avg_arr, cold_thresh):
    hot = []
    for j in range(0, np.shape(abs_avg_arr)[0]):
        a = abs_avg_arr[j]
        if a >= cold_thresh:
            hot.append(j)
    return hot


def get_bits(f, t, Zxx):
    found_bits = []
    # hot columns
    abs_arr = np.abs(Zxx)
    avg_abs_arr = np.mean(abs_arr,axis=1)
    cold_thresh = find_threshold(avg_abs_arr)
    hot_ind = find_hot2(avg_abs_arr, cold_thresh)
    print("hot frequencies:", hot_ind, "\n")
    for bit in potential_bits:
        for h in hot_ind:
            if np.abs(f[h] - bit) <= THRESH:
                found_bits.append(bit)
                break

    print(found_bits)
    return found_bits





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
# get_info("exp_data/sound_150.xls")
# get_info("exp_data/accel_98.xls", True)
# get_info("exp_data/sound_170_150.csv")
# get_info("exp_data/no_case_170_150.csv")
# get_info("exp_data/sound_150_second.xls",axis="z")
# get_info("exp_data/changing_amp.csv")
get_info("exp_data/tran5.xls")
