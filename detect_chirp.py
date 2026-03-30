
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import chirp, stft

def detect_chirp(xls_path, axis="x", duration=1.0, f0=160, f1=185):
    # extract
    df = pd.read_excel(xls_path)
    t = df['Time (s)'].to_numpy()
    x = df[f'Gyroscope {axis} (rad/s)'].to_numpy()

    # estimate sample rate
    dt = np.median(np.diff(t))
    sample_rate = 1.0 / dt
    print("fs:", sample_rate)


    # STFT of received signal
    received_freq, received_time, received_zxx = stft(x, fs=sample_rate,nperseg=256 ,noverlap=192)
    received_abs = np.abs(received_zxx)

    # build chirp template - LEVIN THIS IS THE IMPORTANT PART TO TWEEK WITH AND TRY NEW MORE COMPLEX SEQUENCES
    n = int(duration * sample_rate)
    times = np.arange(n) / sample_rate
    chirp_template = chirp(times, f0=f0, f1=f1, t1=duration, method="linear")
    chirp_template = np.array(chirp_template)
    print("chirp template shape:", np.shape(chirp_template))
    chirp_template = np.concatenate((chirp_template,chirp_template),axis=0)
    chirp_template = np.concatenate((chirp_template,chirp_template),axis=0)
    print("chirp template shape:", np.shape(chirp_template))


    # STFT of chirp template using SAME settings
    chirp_freq, chirp_time, chirp_zxx = stft(chirp_template, fs=sample_rate, nperseg=256, noverlap=192)
    chirp_abs = np.abs(chirp_zxx)

    # keep only relevant band
    band = (received_freq >= max(0, f0 - 30)) & (received_freq <= f1 + 30)
    received_abs = received_abs[band, :]
    chirp_abs = chirp_abs[band, :]
    freq_band = received_freq[band]


    print("chirp abs shape:", chirp_abs.shape)
    width = chirp_abs.shape[1]
    scores = []

    for i in range(received_abs.shape[1] - width + 1):
        chunk = received_abs[:, i:i+width]
        chunk = chunk - np.mean(chunk)
        chunk_norm = np.linalg.norm(chunk)

        if chunk_norm > 0:
            chunk = chunk / chunk_norm
            score = np.sum(chunk * chirp_abs)
        else:
            score = 0.0
            score = np.sum(chunk * chirp_abs)

        scores.append(score)

    scores = np.array(scores)
    best_i = np.argmax(scores)
    detected_time = received_time[best_i]

    print("Detected chirp at:", detected_time, "sec")
    print("Best score:", scores[best_i])

    plt.figure(figsize=(10, 4))
    plt.pcolormesh(received_time, freq_band, received_abs, shading="gouraud")
    plt.axvline(detected_time, color="r", linestyle="--")
    plt.title("Received gyro spectrogram")
    plt.xlabel("Time [sec]")
    plt.ylabel("Frequency [Hz]")
    plt.show()

    plt.figure(figsize=(10, 4))
    plt.plot(received_time[:len(scores)], scores)
    plt.axvline(detected_time, color="r", linestyle="--")
    plt.title("Spectrogram chirp match score")
    plt.xlabel("Time [sec]")
    plt.ylabel("Score")
    plt.show()

    return detected_time, scores

detect_chirp("exp_data/chirp3.xls", axis="y", duration=2.0, f0=160, f1=185)
