import numpy as np
import commpy.modulation as mod
import matplotlib.pyplot as plt
import sounddevice as sd

# Define parameters
M = 16  # Modulation order (e.g., 16 for 16QAM)
SNR_dB = 20  # Signal-to-noise ratio in dB

# Generate random bit stream
bits = np.random.randint(0, 2, int(1e4))
print(bits)

# 16QAM Modulation
qam = mod.QAMModem(M)
modulated_signal = qam.modulate(bits)

def complex_to_wave(comp_sig, carrier_freq, sample_rate):
    """
    Convert complex signal to a real passable waveform:
        s[n] = I[n] cos(2πfcn/fs) - Q[n] sin(2πfcn/fs)
    """
    n = np.arange(len(comp_sig))
    i = np.real(comp_sig)
    q = np.imag(comp_sig)

    carrier_cos = np.cos(2 * np.pi * carrier_freq * n / sample_rate)
    carrier_sin = np.sin(2 * np.pi * carrier_freq * n / sample_rate)

    return i * carrier_cos - q * carrier_sin


transfer_signal = complex_to_wave(modulated_signal,150,48000)
print(transfer_signal)

sd.play(np.abs(transfer_signal))
sd.wait()
plt.plot(transfer_signal[0:100])
plt.title('Transfer signal')
plt.show()


# Compute average symbol power Es
Es = np.mean(np.abs(modulated_signal)**2)

# Add AWGN noise
noise_std = np.sqrt(Es * 0.5 * 10**(-SNR_dB / 10))
noise = noise_std * (np.random.randn(len(modulated_signal)) + 1j * np.random.randn(len(modulated_signal)))
received_signal = modulated_signal + noise
plt.plot(np.abs(received_signal[0:100]))
plt.show()

# 16QAM Demodulation
demodulated_bits = qam.demodulate(received_signal, 'hard')

# Calculate Bit Error Rate (BER)
ber = np.sum(bits != demodulated_bits) / len(bits)
print(f'Bit Error Rate (BER): {ber}')

# Plotting the constellation diagram
plt.scatter(received_signal.real, received_signal.imag, color='red', s=1)
plt.title('16QAM Constellation Diagram')
plt.xlabel('In-phase')
plt.ylabel('Quadrature')
plt.grid(True)
plt.show()

