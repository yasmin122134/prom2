import numpy as np

fs = 44100       # Sampling rate (Hz)
duration = 2.0   # Duration in seconds
frequency = 440.0  # Frequency of the note (A4)

# Generate the time axis and the sine wave
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # 0.5 is the volume/amplitude
