import subprocess

subprocess.run([r'C:\Users\TLP\AppData\Local\Android\Sdk\platform-tools\adb.exe', 'logcat', '-c'])

adb_command = [r'C:\Users\TLP\AppData\Local\Android\Sdk\platform-tools\adb.exe', 'logcat', '-s', 'GyroDataLog']

print("Connecting to device...")

process = subprocess.Popen(adb_command, stdout=subprocess.PIPE, text=True)

data_list = []


for line in process.stdout:
    if "GyroDataLog" in line:
        print(line)
