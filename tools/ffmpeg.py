#
#   нужно попарсить строку достать дименшены входа
#   нагенерить скейл фактор
#   чтобы от исхного на рандом скелилось
#   сгенерить кроп фактор так же рандомом
#   и сгенерить выходное имя
#   по аналогии со входом
#   ffmpeg -pix_fmt yuv420p -s 3240x2160 -i input__3240xx2160.yuv -vf \"scale=1920:1080,crop=1280:720:512:512\" -pix_fmt yuv420p out__1920xx1080.yuv"

import re
import random
import os
import sys

class CheckedRunFailed(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

def checked_run(*popenargs, **kwargs):
    import sys
    if sys.platform.startswith("win"):
        import ctypes
        # From MSDN
        SEM_NOGPFAULTERRORBOX = 0x0002
        ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);
        #win32con.CREATE_NO_WINDOW?
        subprocess_flags = 0x8000000
        # this exit code (STATUS_ACCESS_VIOLATION) indicates crash on Windows
        EXIT_CODES_CRASH = [ ctypes.c_int32(0xC0000005).value ]
    else:
        subprocess_flags = 0
        # these signals (SIGQUIT, SIGILL, SIGTRAP, SIGABRT, SIGFPE, SIGBUS, SIGSEGV, SIGSYS) indicate crash on Linux
        EXIT_CODES_CRASH = [ -3, -4, -5, -6, -7, -8, -11, -13 ]
    
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

# generate out command line for ffmpeg
def generate_cmd(cmd, input_file_name):
    regex = r"(__)(\d+)xx(\d+)"
    
    result = re.search(regex, input_file_name)
    
    if result:
    
        file_name, file_ext = os.path.splitext(input_file_name)
        
        cmd = cmd.replace("<input_file_name>", input_file_name)        
        
        w = int(result.group(2))
        h = int(result.group(3))
        
        cmd = cmd.replace("<input_file_resolution>", str(w) + "x" + str(h))
        
        neww = random.randint(int(w/2), w)
        newh = random.randint(int(h/2), h)
        
        cmd = cmd.replace("<output_file_name>", "output__" + str(neww) + "xx" + str(newh) + ".yuv")
        cmd = cmd.replace("<random_scale>", str(neww) + ":" + str(newh))
        
        crop_out_w = random.randint(0, int(w))
        crop_out_h = random.randint(0, int(h))
        crop_x     = random.randint(0, crop_out_w)
        crop_y     = random.randint(0, crop_out_h)
    
        cmd = cmd.replace("<random_crop>", str(crop_out_w) + ":" + str(crop_out_h) + ":" + str(crop_x) + ":" + str(crop_y))
    return cmd

def run_ffmpeg(ffargs):
    print(ffargs)
    cmd = ffargs.split(" ")
    print("\n\n\n",cmd,"\n\n\n")
    checked_run(cmd)

# main
def main(argv):
    cmd = "ffmpeg -pix_fmt yuv420p -s <input_file_resolution> -i <input_file_name> -vf scale=<random_scale>,crop=<random_crop> -pix_fmt yuv420p <output_file_name> -y"
    
    try:
        #print(generate_cmd(cmd, argv[0]))
        run_ffmpeg(generate_cmd(cmd, argv[0]))
    except IndexError:
        print('Usage:\nffmpeg.py <filename>')
    except FileNotFoundError:
        print('ffmpeg not found')

if __name__ == "__main__":
    main(sys.argv[1:])
