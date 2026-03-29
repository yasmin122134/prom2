import subprocess
import time
import numpy as np
from scipy.signal import stft
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from scipy.signal import find_peaks

# ==========================================
# CONFIGURATION
# ==========================================
TARGET_AXIS = 'x'
MAX_BUFFER_SIZE = 4000  # Memory: Keep the last ~10 seconds of data for the UI
UPDATE_BATCH_SIZE = 417  # Analysis & UI Refresh: Process newest ~1 second of data

AXIS_MAP = {'x': 1, 'y': 2, 'z': 3}
TARGET_IDX = AXIS_MAP[TARGET_AXIS.lower()]

# ==========================================
# LEVIN'S ALGORITHM CONFIGURATION
# ==========================================
jump_size = 10
potential_bits = list(range(0, 205, jump_size))

THRESH = 1.5


def find_threshold(arr, percentile = 90):
    return np.percentile(arr, percentile)
    # max_val = np.max(arr)
    # min_val = np.min(arr)
    # return (max_val + min_val) / 2


def find_hot2(abs_arr, cold_thresh):
    peaks_indices,_ = find_peaks(abs_arr, height=cold_thresh, prominence=cold_thresh * 1.5)
    return peaks_indices.tolist()

prev_phase = 0

def get_bits(f, t, Zxx):
    global prev_phase
    found_bits = []
    abs_arr = np.abs(Zxx)
    avg_abs_arr = np.mean(abs_arr, axis=1)

    # max_index = 0
    # for i in range(len(avg_abs_arr)):
    #     if avg_abs_arr[i] > avg_abs_arr[max_index]:
    #         max_index = i
    #
    # print("Max:", f[max_index] , "value: ", avg_abs_arr[max_index])

    cold_thresh = find_threshold(avg_abs_arr)
    hot = find_hot2(avg_abs_arr, cold_thresh)

    for item in hot:
        amplitude = avg_abs_arr[item]
        curr_phase = np.angle(Zxx[item][1])
        freq = f[item]

        rad_delta_phase = (curr_phase - prev_phase) % (2 * np.pi)
        print("\nfrequency:", freq, "amplitude:", amplitude, "phase:", curr_phase, "diff_phase",
              rad_delta_phase)

        prev_phase = curr_phase

    # print("hottest: \n" , hot, "\n")
    # for bit in potential_bits:
    #     # if bit == 150:
    #     #     print("\n Average:", np.mean(Zxx[bit]), "values: ", Zxx[bit])
    #     for h in hot:
    #         if np.abs(f[h] - bit) <= THRESH:
    #             found_bits.append(bit)
    #             break
    # return found_bits


# ==========================================
# REAL-TIME PROCESSING & UI
# ==========================================
def process_window(full_time, full_move, new_time, new_move, img_item):
    # --- 1. Update UI (Using the full 10s buffer) ---
    duration_sec = (full_time[-1] - full_time[0]) / 1e9
    if duration_sec > 0:
        sample_rate = round(len(full_time) / duration_sec)

        if sample_rate >= 2:
            overlap = int(sample_rate * 0.9)
            f_full, t_full, Zxx_full = stft(full_move, fs=sample_rate, nperseg=sample_rate, noverlap=overlap)

            magnitude = np.abs(Zxx_full)
            img_item.setImage(magnitude.T, autoLevels=True)
            img_item.setRect(QtCore.QRectF(t_full[0], f_full[0], t_full[-1] - t_full[0], f_full[-1] - f_full[0]))

    # --- 2. Bit Detection (Using ONLY the newest data chunk) ---
    chunk_duration = (new_time[-1] - new_time[0]) / 1e9
    if chunk_duration > 0:
        chunk_sr = round(len(new_time) / chunk_duration)

        if chunk_sr >= 2:
            # Ensure nperseg is not larger than the new chunk size
            nperseg_val = min(chunk_sr, len(new_time))
            f_new, t_new, Zxx_new = stft(new_move, fs=chunk_sr, nperseg=nperseg_val)

            bits = get_bits(f_new, t_new, Zxx_new)

            # Print the result for the current ~1s window
            # print(f"[{time.strftime('%H:%M:%S')}] Bits in new {chunk_duration:.2f}s chunk: {bits}")


def main():
    print("Clearing logcat cache...")
    subprocess.run([r'C:\Users\TLP\AppData\Local\Android\Sdk\platform-tools\adb.exe', 'logcat', '-c'])
    time.sleep(1)

    adb_command = [r'C:\Users\TLP\AppData\Local\Android\Sdk\platform-tools\adb.exe', 'logcat', '-s', 'GyroDataLog']
    print(f"Connecting to Logcat... Listening to axis '{TARGET_AXIS.upper()}'")

    process = subprocess.Popen(
        adb_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding='utf-8'
    )

    # Setup PyQtGraph UI
    app = pg.mkQApp("Spectrogram App")
    win = pg.GraphicsLayoutWidget(show=True, title="Real-Time Spectrogram")
    win.resize(900, 600)

    plot = win.addPlot(title=f"Live Spectrogram (Axis {TARGET_AXIS.upper()})")
    plot.setLabel('bottom', 'Time', units='s')
    plot.setLabel('left', 'Frequency', units='Hz')

    img_item = pg.ImageItem()
    plot.addItem(img_item)
    colormap = pg.colormap.get('viridis')
    img_item.setColorMap(colormap)

    time_buffer = []
    move_buffer = []
    new_samples_count = 0

    try:
        for line in process.stdout:
            if "GyroDataLog" in line:
                data_part = line.split(":")[-1].strip()

                for chunk in data_part.split('\n'):
                    values = chunk.strip().split(",")

                    if len(values) == 4:
                        try:
                            timestamp = float(values[0])
                            target_val = float(values[TARGET_IDX])

                            time_buffer.append(timestamp)
                            move_buffer.append(target_val)
                            new_samples_count += 1

                            # Once we have enough NEW samples, update the plot and analyze
                            if new_samples_count >= UPDATE_BATCH_SIZE:

                                # Extract the newest samples for bit detection
                                new_time = time_buffer[-new_samples_count:]
                                new_move = move_buffer[-new_samples_count:]

                                # Keep only the last MAX_BUFFER_SIZE samples for the UI
                                if len(time_buffer) > MAX_BUFFER_SIZE:
                                    time_buffer = time_buffer[-MAX_BUFFER_SIZE:]
                                    move_buffer = move_buffer[-MAX_BUFFER_SIZE:]

                                # Only update UI if we have a full 10s window
                                if len(time_buffer) == MAX_BUFFER_SIZE:
                                    process_window(time_buffer, move_buffer, new_time, new_move, img_item)

                                new_samples_count = 0  # Reset new samples counter

                        except ValueError:
                            continue

            # Keep GUI responsive
            app.processEvents()

    except KeyboardInterrupt:
        print("\nProcess terminated by user.")
        process.terminate()


if __name__ == "__main__":
    main()