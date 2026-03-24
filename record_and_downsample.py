# Imports
import numpy as np
from scipy.io import wavfile
import scipy.signal as sps
import sounddevice as sd

# Your new sampling rate
# new_rate = 170
#
# # Read file
# sampling_rate, data = wavfile.read("rec.wav")
#
# # Resample data
# number_of_samples = round(len(data) * float(new_rate) / sampling_rate)
# data = sps.resample(data, number_of_samples)
#

# save new file
# name = "downsampled_recording.wav"
# wavfile.write(name, new_rate, data.astype(np.float32))

name = "rec.wav"

sampling_rate, data = wavfile.read(name)
while True:
    sd.play(data, sampling_rate)
    sd.wait()
print(data.shape)
print(sampling_rate)
# play
sd.play(data, 44100)
sd.wait()


# FFT
from scipy.signal import stft
from matplotlib import pyplot as plt

f, t, Zxx = stft(data, fs=sampling_rate, nperseg=256)

plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
plt.ylabel('Hz')
plt.xlabel('Sec')
plt.title(f'{name}, FFT')
plt.show()