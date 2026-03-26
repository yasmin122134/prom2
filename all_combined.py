import subprocess
import time
import numpy as np
from scipy.signal import stft
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

# ==========================================
# CONFIGURATION
# ==========================================
TARGET_AXIS = 'x'
MAX_BUFFER_SIZE = 4000  # Memory: Keep the last 10 seconds of data (assuming ~400Hz)
UPDATE_BATCH_SIZE = 800  # UI Refresh Rate: Update the graph every ~1 second

AXIS_MAP = {'x': 1, 'y': 2, 'z': 3}
TARGET_IDX = AXIS_MAP[TARGET_AXIS.lower()]

# ==========================================
# LEVIN'S ALGORITHM CONFIGURATION
# ==========================================
jump_size = 2
potential_bits = list(range(0, 205, jump_size))

THRESH = 0.01


def find_threshold(arr):
    max_val = np.max(arr)
    min_val = np.min(arr)
    threshold = (max_val + min_val) / 2
    return threshold


def find_hot2(abs_arr, cold_thresh):
    hot = []
    for j in range(0, np.shape(abs_arr)[0]):
        a = abs_arr[j]
        if a >= cold_thresh:
            hot.append(j)
    return hot


def get_bits(f, t, Zxx):
    found_bits = []
    abs_arr = np.abs(Zxx)
    avg_abs_arr = np.mean(abs_arr, axis=1)

    cold_thresh = find_threshold(avg_abs_arr)
    hot = find_hot2(avg_abs_arr, cold_thresh)

    for bit in potential_bits:
        for h in hot:
            if np.abs(f[h] - bit) <= THRESH:
                found_bits.append(bit)
                break
    return found_bits


# ==========================================
# REAL-TIME PROCESSING & UI
# ==========================================
def process_window(time_arr, move_arr, img_item):
    duration_sec = (time_arr[-1] - time_arr[0]) / 1e9
    if duration_sec <= 0:
        return

    n_samples = len(time_arr)
    sample_rate = n_samples / duration_sec
    sample_rate = round(sample_rate)

    if sample_rate < 2:
        return

    # INCREASED RESOLUTION: Use 90% overlap for a smooth, detailed Spectrogram
    overlap = int(sample_rate * 0.9)
    f, t, Zxx = stft(move_arr, fs=sample_rate, nperseg=sample_rate, noverlap=overlap)

    magnitude = np.abs(Zxx)

    # Update Spectrogram UI
    img_item.setImage(magnitude.T, autoLevels=True)
    img_item.setRect(QtCore.QRectF(t[0], f[0], t[-1] - t[0], f[-1] - f[0]))

    # Extract Bits
    bits = get_bits(f, t, Zxx)
    print(f"Bits detected in current 10s window: {bits}")


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

                            # Once we have enough NEW samples, update the plot
                            if new_samples_count >= UPDATE_BATCH_SIZE:

                                # Keep only the last MAX_BUFFER_SIZE samples (Rolling Window)
                                if len(time_buffer) > MAX_BUFFER_SIZE:
                                    time_buffer = time_buffer[-MAX_BUFFER_SIZE:]
                                    move_buffer = move_buffer[-MAX_BUFFER_SIZE:]

                                # Only process if we have a full window
                                if len(time_buffer) == MAX_BUFFER_SIZE:
                                    process_window(time_buffer, move_buffer, img_item)

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