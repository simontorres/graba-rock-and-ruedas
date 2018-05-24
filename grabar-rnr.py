import os
import time
import subprocess
from threading import Timer

today = time.strftime('%Y_%m_%d')

url = 'http://provisioning.streamtheworld.com/pls/FUTURO.pls'


file_name = "rock_and_ruedas_{:s}.mp3".format(today)

stream_source = "-playlist {:s}".format(url)

command = "mplayer -dumpstream -dumpfile {:s} {:s}".format(file_name,
                                                           stream_source)
try:
    radio_futuro = subprocess.Popen(command.split(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
except OSError as error:
    print(error)

def stop_recording(process):
    print("End recording")
    process.kill()

radio_timer = Timer(10, stop_recording, [radio_futuro])
try:
    radio_timer.start()
    stdout, stderr = radio_futuro.communicate()
finally:
    radio_timer.cancel()

for line in stdout.split(b'\n'):
    print(line.decode("utf-8"))

if stderr != b'':
    for error_line in stderr.split(b'\n'):
        print("error: ", error_line.decode("utf-8"))