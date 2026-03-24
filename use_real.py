import numpy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.fft import rfft, rfftfreq



file = 'exp_data/sound_15000.csv'
df = pd.read_csv(file)

time = df['Time (s)'].tolist()
moveX = df['Gyroscope x (rad/s)'].tolist()

DURATOIN = time[-1]
N_SAMPLE = len(time)
SAMPLE_RATE =  N_SAMPLE / DURATOIN



plt.plot(time, moveX)
plt.show()


def FFT(data):
    yf = rfft(data)
    xf = rfftfreq(N_SAMPLE, 1/SAMPLE_RATE)

    plt.plot(xf, np.abs(yf))
    plt.show()

FFT(moveX)
print("Avarage:", np.mean(moveX))
print("Max:", np.max(moveX))