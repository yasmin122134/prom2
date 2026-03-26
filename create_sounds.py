import numpy as np
import sounddevice as sd

def white_noise(
        duration: float=1.0,
        amplitude: float=0.5,
        sample_rate: int=44100,
) -> np.ndarray:
    n_samples = int(duration * sample_rate)
    noise = np.random.uniform(-1,1, n_samples)
    noise *= amplitude
    return noise


def main():
    mysound = white_noise()
    sd.play(mysound, 44100)
    sd.wait(1)
    my_modulator = sine_tone(400,3)
    sd.play(my_modulator)
    sd.wait()
    am_sound = am_synthesis(440, my_modulator)
    print(am_sound)
    sd.play(am_sound)
    sd.wait()

def sine_tone(
        frequency: int=440,
        duration: float=1.0,
        amplitude: float=1.0,
        samplerate: int=44100,
) -> np.ndarray:
    n_samples = int(samplerate * duration)
    time_points = np.linspace(0, duration, n_samples,False)
    sine = np.sin(2 * np.pi * frequency * time_points)
    sine *= amplitude
    return sine

def am_synthesis(
        carrier_frequency: float,
        modulator_wave: np.array,
        modulation_index: float=0.5,
        amplitude: float=0.5,
        sample_rate: int=44100,
) -> np.ndarray:
    total_samples = len(modulator_wave)
    time_points = np.arange(total_samples) / sample_rate
    carrier_wave = np.sin(2 * np.pi * carrier_frequency * time_points)
    am_wave = (1+modulation_index * modulator_wave) * carrier_wave
    max_amplitude = np.max(np.abs(am_wave))
    am_wave = amplitude * (am_wave / max_amplitude)
    return am_wave

if __name__ == "__main__":
    main()