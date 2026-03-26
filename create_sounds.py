import numpy as np
import sounddevice as sd
import soundfile as sf
import threading

def _play_array(sound, samplerate=44100):
    sound = np.asarray(sound, dtype=np.float32)
    sd.play(sound, samplerate)
    sd.wait()


def _playsound(sound, samplerate=44100):
    new_thread = threading.Thread(target=_play_array, args=(sound, samplerate))
    new_thread.start()
    return new_thread




def main():
    tone = sine_tone(300, 2)
    t1 = _playsound(tone)

    my_modulator = sine_tone(150, 3)
    am_sound = am_synthesis(150, my_modulator)
    t2 = _playsound(am_sound)

    t1.join()
    t2.join()


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

def transfer(f_2D_list, time):
    freq_amp_by_time_segment = []
    for i in range(0, len(f_2D_list)):
        f_map = {}
        for j in range(0, len(f_2D_list[i])):
            f_map[f_2D_list[i][j]] = 1
        freq_amp_by_time_segment.append(f_map)

    to_play = []
    for t in freq_amp_by_time_segment:
        for k, v in t.items():
            sine = sine_tone(k,time,v)
            to_play.append(_playsound(sine))
        for th in to_play:
            th.join()
        to_play = []






if __name__ == "__main__":
    transfer([[100,150],[200,250]],2)
