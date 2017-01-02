import time
import datetime
import random
import sys
import getopt
import os
import shutil
import re
#import psutil
#import multiprocessing

# this os not for test watermark but just util functions
class CheckedRunFailed(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
# this os not for test watermark but just util functions
class ExpectationFailed(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# this os not for test watermark but just util functions
def checked_run(*popenargs, **kwargs):
    import sys
    if sys.platform.startswith("win"):
        # Don't display the Windows GPF dialog if the invoked program dies.
        # See comp.os.ms-windows.programmer.win32
        # How to suppress crash notification dialog?, Jan 14,2004 -
        # Raymond Chen's response [1]

        import ctypes

        SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
        ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);
        subprocess_flags = 0x8000000 #win32con.CREATE_NO_WINDOW?

        EXIT_CODES_CRASH = [ ctypes.c_int32(0xC0000005).value ] # this exit code (STATUS_ACCESS_VIOLATION) indicates crash on Windows
    else:
        subprocess_flags = 0

        EXIT_CODES_CRASH = [ -3, -4, -5, -6, -7, -8, -11, -13 ] # these signals (SIGQUIT, SIGILL, SIGTRAP, SIGABRT, SIGFPE, SIGBUS, SIGSEGV, SIGSYS) indicate crash on Linux

    import subprocess as sp32

    if 'redirect_output' in kwargs:
        kwargs['stdout'] = open(kwargs.pop('redirect_output', '.output'), "wb")
    if 'redirect_error' in kwargs:
        kwargs['stderr'] = open(kwargs.pop('redirect_error', '.error'), "wb")
    if 'redirect_outputa' in kwargs:
        kwargs['stdout'] = open(kwargs.pop('redirect_outputa', '.outputa'), "ab")
    if 'redirect_errora' in kwargs:
        kwargs['stderr'] = open(kwargs.pop('redirect_errora', '.errora'), "ab")
    try:
        sp32.check_call(*popenargs, **kwargs)

    except sp32.CalledProcessError as e:
        if e.returncode in EXIT_CODES_CRASH:
            raise CheckedRunFailed("CRASH")
        else:
            return e.returncode

    #except sp32.TimeoutExpired:
    #    raise CheckedRunFailed("TIMEOUT EXPIRED")

    return 0

# test func
def run_ffmpeg(input_file, frame_number):
    #binary = 'D:\\Downloads\\ffmpeg-20161210-edb4f5d-win64-static\\bin\\ffmpeg.exe'
    binary = 'ffmpeg'

    ffargs = [binary, '-i', input_file, '-vf', 'select=gte(n\,' + frame_number + ')', '-vframes', '1', input_file + '_frame' + frame_number + '.png', '-y']

    checked_run(ffargs, redirect_output = 'nul', redirect_error = 'nul')

# test func
def run_wmdetect(inpf, frame_number, wmpos, wm):
    binary = 'wm_det_app'
    bin_stdout = 'test.stdout'

    wmargs = [binary, inpf + '_frame' + frame_number + '.png', wmpos]

    # run our detector and redirect output to bin_stdout file. we dont care about stderror
    checked_run(wmargs, redirect_output = bin_stdout, redirect_error = 'nul')

    # regular expression to extract our watermark from bin_stdout
    rg = r"OK: text found\nOK:\s+(.+)"

    with open(bin_stdout, 'r') as fp:
        data = fp.read()
        result = re.match(rg, data)
        # our result file
        f_rez = inpf + '.REZULT.log'
        f = open(f_rez,'a')
        # if regular expression found
        if result:
            extracted_wm  = result.group(1)
            #print(extracted_wm)
            f.write(frame_number + '\t' + wmpos + '\t' + extracted_wm + '\n')
            #f.write(extracted_wm)
        else:
            f.write(frame_number + '\t' + wmpos + '\t' + 'NOT_FOUND' + '\n')

# test func
def compare_logs(input_log, detected_log):
    print('Input metadata file -> ', input_log)
    print('Extracted wm   file -> ', detected_log)

    num_total = 0
    num_found = 0
    sum_detected = 0

    rg = r"(\d+)\s+(\d+)\s+(.+)"
    with open(input_log) as file1, open(detected_log) as file2:
        for line1, line2 in zip(file1, file2):
            num_total = num_total + 1
            #print(line1, line2)
            #print("{0}\t{1}".format(line1.strip(),line2.strip()))
            # compare strings
            result1 = re.match(rg, line1)
            result2 = re.match(rg, line2)
            if result1:
                golden_wm = result1.group(3)
                if result2:
                    detected_wm = result2.group(3)
                    #print(golden_wm, detected_wm)
                    if detected_wm != 'NOT_FOUND':
                        num_found = num_found + 1
                    if detected_wm == golden_wm:
                        sum_detected = sum_detected + 1
    print('\nTotal   ', str(num_total))
    print('Found   ', str(num_found))
    print('Matched ', str(sum_detected))

# test func
def extract_frames(input_media, input_data):
    # lets remove old result file
    os.remove(input_media + '.REZULT.log') if os.path.exists(input_media + '.REZULT.log') else None

    # regular expression to parse input metadata file to get frame, pos and watermark string
    rg = r"(\d+)\s+(\d+)\s+(.+)"

    try:
        with open(input_data) as fp:
            for line in fp:
                #print(line)
                result = re.match(rg, line)
                if result:
                    frame_number  = result.group(1)
                    mark_position = result.group(2)
                    mark_symbols  = result.group(3)

                    # lets extract frame
                    run_ffmpeg(input_media, frame_number)

                    # and now lets try to find watermark in this frame
                    run_wmdetect(input_media, frame_number, mark_position, mark_symbols)
    except FileNotFoundError:
        print('input not found or ffmpeg missing')

# main
def main(argv):
    try:
        # lets parse input mp4 filename so we could get log metadata filename
        # argv[0] is our mp4 filename that we passed to our python script
        media_file_name = argv[0]
        filename, file_extension = os.path.splitext(media_file_name)
        media_file_metadata = filename + '.log'
        print('\nInput media    file -> ', media_file_name)

        # now we extract frames from our media file according to metadata that should be near media file
        # also we will try to find watermark for each frame of media file
        extract_frames(media_file_name, media_file_metadata)

        # now we will compare input metadata with our result file
        compare_logs(media_file_metadata, media_file_name + '.REZULT.log')
    except IndexError:
        print('Usage:\nextract_frames.py <filename>')

# required for import
if __name__ == "__main__":
    main(sys.argv[1:])
    os.remove      ('test.stdout')      if os.path.exists('test.stdout') else None
