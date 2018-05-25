import os
import time
import subprocess
from threading import Timer
import datetime
import calendar
import sys
import pytz


class StreamRecorder(object):

    def __init__(self, start_time='19:58:00', end_time='21:02:00'):
        self.valid_days = ['Monday',
                           'Tuesday',
                           'Wednesday',
                           'Thursday',
                           'Friday']

        self.time_format = '%H:%M:%S'
        self.start_time = start_time
        self.end_time = end_time
        self.duration = 3600
        self.today = datetime.date.today()
        self.day_name = calendar.day_name[self.today.weekday()]

        self.url = 'http://provisioning.streamtheworld.com/pls/FUTURO.pls'
        self.stream_source = "-playlist {:s}".format(self.url)

        self.output_base = "rock_and_ruedas_{:s}_{:s}.mp3"
        self.output_file = ""

        self.command_base = "mplayer -dumpstream -dumpfile {:s} {:s}"
        self.command = ""

        self.rock_and_ruedas = None
        self.timer = None
        self.stdout = None
        self.stderr = None

    def __call__(self, *args, **kwargs):
        time_start = datetime.datetime.strptime(self.start_time,
                                                self.time_format)
        time_end = datetime.datetime.strptime(self.end_time,
                                              self.time_format)
        duration = time_end - time_start
        self.duration = int(duration.total_seconds())

        while True:
            if not self.__check_weekday():
                # self.__wait_until_monday()
                sys.exit('No hay Rock & Ruedas hoy {:s}.'.format(self.day_name))
            if self.__get_time_to_start() < 0:
                print('A esperar hasta manana')
                time.sleep(3600)

            elif self.__get_time_to_start() > 3600:
                print("Waiting 1 Hour")
                print("Next Check: {:s}".format(str(datetime.datetime.now() +
                                                datetime.timedelta(hours=1))))
                time.sleep(3600)

            elif self.__get_time_to_start() > 600:
                print("Waiting 10 Minutes")
                print("Next Check: {:s}".format(str(datetime.datetime.now() +
                                                    datetime.timedelta(
                                                        minutes=10))))
                time.sleep(600)
            else:
                while self.__get_time_to_start() > 1:
                    print("\rTime to start {:s}".format(
                        str(datetime.timedelta(
                            seconds=self.__get_time_to_start()))),
                        sep=' ',
                        end='',
                        flush=True)
                    time.sleep(1)

                print("Start recording")
                self.output_file = self.output_base.format(str(self.today),
                                                           self.day_name)

                if os.path.isfile(self.output_file):
                    print("Removing existing file {:s}"
                          "".format(self.output_file))
                    os.remove(self.output_file)
                else:
                    print("Recording to {:s}".format(self.output_file))

                self.command = self.command_base.format(self.output_file,
                                                        self.stream_source)
                self.__record()


            break

    def __record(self):
        try:
            self.rock_and_ruedas = subprocess.Popen(self.command.split())
        except OSError as error:
            print(error)

        self.timer = Timer(self.duration,
                           self.__stop_recording,
                           [self.rock_and_ruedas])
        try:
            self.timer.start()
            self.stdout, self.stderr = self.rock_and_ruedas.communicate()
        finally:
            self.timer.cancel()


    def __check_weekday(self):
        """Checks that today is a week day"""
        if self.day_name in self.valid_days:
            return True
        else:
            return False

    @staticmethod
    def __get_chile_local_time():
        return datetime.datetime.now(pytz.timezone('America/Santiago'))

    def __get_time_to_start(self):
        """Gets time in seconds to start recording

        """
        now = self.__get_chile_local_time()
        time_obj = datetime.datetime.strptime(str(self.today) + self.start_time,
                                              '%Y-%m-%d' + self.time_format)

        start_time = pytz.timezone('America/Santiago').localize(time_obj)
        time_to_start = start_time - now
        print(time_to_start.total_seconds())
        return time_to_start.total_seconds()

    def __stop_recording(self, process):
        print("End recording")
        process.kill()

if __name__ == '__main__':
    record = StreamRecorder()
    try:
        record()
    except KeyboardInterrupt:
        sys.exit("Program Exit")

#
# for line in stdout.split(b'\n'):
#     print(line.decode("utf-8"))
#
# if stderr != b'':
#     for error_line in stderr.split(b'\n'):
#         print("error: ", error_line.decode("utf-8"))