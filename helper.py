import subprocess
import time
import numpy as np
from scipy.signal import stft
from matplotlib import pyplot as plt

# ==========================================
# CONFIGURATION
# ==========================================
TARGET_AXIS = 'x'  # Options: 'x', 'y', or 'z'
PYTHON_BATCH_SIZE = 4000  # Number of samples to accumulate before updating UI

AXIS_MAP = {'x': 1, 'y': 2, 'z': 3}
TARGET_IDX = AXIS_MAP[TARGET_AXIS.lower()]


# ==========================================
# LEVIN'S ALGORITHM CONFIGURATION
# ==========================================
jump_size = 2
potential_bits = []
for i in range(0, 205, jump_size):
    potential_bits.append(i)
print("Potential bits:", potential_bits)

THRESH = 0.01


# ==========================================
# LEVIN'S LOGIC
# ==========================================
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

    print("Hot frequencies:", hot)

    for bit in potential_bits:
        for h in hot:
            if np.abs(f[h] - bit) <= THRESH:
                found_bits.append(bit)
                break

    print("Found bits:", found_bits)
    return found_bits


# ==========================================
# REAL-TIME PROCESSING & UI
# ==========================================
def process_window(time_arr, move_arr, ax, fig):
    print(f"\n--- Analyzing Window ({len(time_arr)} samples) ---")
    print("Average:", np.mean(move_arr))
    print("Max:", np.max(move_arr))

    # Convert Java timestamps (nanoseconds) to seconds for duration
    duration_sec = (time_arr[-1] - time_arr[0]) / 1e9
    if duration_sec <= 0:
        return

    n_samples = len(time_arr)
    sample_rate = n_samples / duration_sec
    print(f"Sample rate: {sample_rate:.2f} Hz")

    sample_rate = round(sample_rate)
    if sample_rate < 2:
        return

    # Calculate Spectrogram
    f, t, Zxx = stft(move_arr, fs=sample_rate, nperseg=sample_rate)

    # Update Spectrogram UI
    ax.clear()
    ax.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
    ax.set_ylabel('Hz')
    ax.set_xlabel('Sec')
    ax.set_title(f'Live Spectrogram (Axis {TARGET_AXIS.upper()})')

    # Force UI refresh
    fig.canvas.draw()
    fig.canvas.flush_events()

    # Extract Bits using Levin's logic
    get_bits(f, t, Zxx)


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

    # Setup interactive matplotlib
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 5))
    plt.show()

    time_buffer = []
    move_buffer = []

    try:
        for line in process.stdout:
            if "GyroDataLog" in line:
                data_part = line.split(":")[-1].strip()

                # Split by \n in case Logcat batches multiple lines together
                for chunk in data_part.split('\n'):
                    values = chunk.strip().split(",")

                    if len(values) == 4:
                        try:
                            timestamp = float(values[0])
                            target_val = float(values[TARGET_IDX])

                            time_buffer.append(timestamp)
                            move_buffer.append(target_val)

                            # If we reached the target batch size, process and reset
                            if len(time_buffer) >= PYTHON_BATCH_SIZE:
                                process_window(time_buffer, move_buffer, ax, fig)

                                # Clear buffers for the next window
                                time_buffer.clear()
                                move_buffer.clear()

                        except ValueError:
                            continue

    except KeyboardInterrupt:
        print("\nProcess terminated by user.")
        process.terminate()
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()