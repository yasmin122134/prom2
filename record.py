# Imports
import numpy as np
from scipy.io import wavfile
import scipy.signal as sps
import sounddevice as sd

# record new audio
duration = 2 #sec
old_rate = 44100

# record
recording = sd.rec(int(duration * old_rate), samplerate = old_rate, channels =1,
                   dtype='float64')
#waits till ur finished recording
sd.wait(duration)


# play
sd.play(recording, old_rate)
sd.wait(duration)

# save new file
wavfile.write('rec.wav', old_rate, recording.astype(np.float32))