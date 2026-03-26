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
    my_modulation = sine_tone(3, 5)
    fm_sound = fm_synthesis(150, my_modulation,modulation_index=3)
    t2 = _playsound(fm_sound)

    # t1.join()
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

def fm_synthesis(
        carrier_frequency: float,
        modulator_wave: np.array,
        modulation_index: float=3,
        amplitude: float=0.5,
        sample_rate: int=44100,
) -> np.ndarray:
    total_samples = len(modulator_wave)
    time_points = np.arange(total_samples) / sample_rate
    fm_wave = np.sin(2 * np.pi * carrier_frequency * time_points + modulation_index * modulator_wave)
    max_amplitude = np.max(np.abs(fm_wave))
    fm_wave = amplitude * (fm_wave / max_amplitude)
    return fm_wave


def transfer(freq_amp_by_time_segment):
    duration = 5

    to_play = []
    for t in freq_amp_by_time_segment:
        for k, v in t.items():
            sine = sine_tone(k,duration,v)
            to_play.append(_playsound(sine))
        for th in to_play:
            th.join()
        to_play = []






if __name__ == "__main__":
    # main()
    freq_amp_by_time_segment = [{
        100: 1,
        110: 1,
        120: 1,
        130: 1,
        140: 1,
        150: 1,
        160: 1,
        170: 1,
        180: 1,
        190: 1,
        200: 1,
    },
        {
            100: 1,
            110: 0,
            120: 1,
            130: 1,
            140: 1,
            150: 0,
            160: 1,
            170: 1,
            180: 0,
            190: 1,
            200: 0,
        },
        {
            100: 0,
            110: 0,
            120: 0,
            130: 0,
            140: 0,
            150: 1,
            160: 1,
            170: 1,
            180: 1,
            190: 1,
            200: 1,
        },
        {
            100: 1,
            110: 1,
            120: 1,
            130: 1,
            140: 1,
            150: 1,
            160: 0,
            170: 0,
            180: 0,
            190: 0,
            200: 0,
        },
    ]
    transfer(freq_amp_by_time_segment)
