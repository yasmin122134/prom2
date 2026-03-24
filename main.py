# Source - https://stackoverflow.com/q/54683525
# Posted by a kig, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-23, License - CC BY-SA 4.0

import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt

duration = 1 #sec
fs = 44100
sr = 44100

# record
recording = sd.rec(int(duration * fs), samplerate = fs, channels =1,
dtype='float64')
#waits till ur finished recording
sd.wait(duration)

# play
sd.play(recording, fs)
sd.wait(duration)


print(recording.shape)

fft_mag = np.abs(np.fft.rfft(recording))
freqs = np.fft.rfftfreq(len(recording), 1 / sr)

plt.plot(freqs, fft_mag)
plt.show()

sp = np.fft.fft(recording)
freq = np.fft.fftfreq(recording.shape[0])
_ = plt.plot(freq, sp.real, freq, sp.imag)
plt.show()

def plot_signal_freq(ys):
   N = ys.size
   print(N)
   L = N/fs
   yk = np.fft.fft(ys)
   k = np.arange(N)
   freqs = k/L
   fig, ax = plt.subplots()
   ax.plot(freqs, np.abs(yk))


# while True:
#    recording = record()
#    print(type(recording.dtype))
#    print(recording)
#    play(recording)
#    plot_signal_freq(recording)


# Source - https://stackoverflow.com/a/25735274
# Posted by Paul H, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-23, License - CC BY-SA 4.0

import scipy.fftpack
# Source - https://stackoverflow.com/q/25735153
# Posted by user3123955, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-23, License - CC BY-SA 4.0
#
# from scipy.fftpack import fft
#
# # Number of samplepoints
# N = 600
#
#
#
# # Sample spacing
# T = 1.0 / 800.0
# x = np.linspace(0.0, N*T, N)
# y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
# yf = fft(y)
# xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
#
# plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))
# plt.grid()
# plt.show()
