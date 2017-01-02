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

class CheckedRunFailed(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class ExpectationFailed(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

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


def run_encoder(inpf, outf, bf, gop, bitrate, bin_ary):
    binary     = '/home/tester/aplakh/' + bin_ary
    
    #ffargs = [binary, '-psnr', '-v', 'verbose', '-i', inpf, '-c:v', 'h264_qsv', '-q', '24', '-look_ahead', '0', '-vcm', '0', '-custom_rc_window', '50', '-custom_rc_hss_rate', '20000000', '-custom_rc_bitrate', bitrate, '-g', gop, '-bf', bf, '-y', '-vstats_file', outf + '_vstats.txt', outf]
    ffargs = [binary, '-v', 'verbose', '-i', inpf, '-c:v', 'h264_qsv', '-q', '24', '-look_ahead', '0', '-vcm', '0', '-custom_rc_window', '50', '-custom_rc_hss_rate', '20000000', '-custom_rc_bitrate', bitrate, '-g', gop, '-bf', bf, '-y', outf]
    #print (ffargs)

    start_time = datetime.datetime.now()
    checked_run(ffargs, redirect_output = outf + '.ffmpeg.stdo.log', redirect_error=outf + '.ffmpeg.stde.log')
    end_time = datetime.datetime.now()
    elapsed_time = int((end_time-start_time).total_seconds()* 1000)
    
    shutil.copyfile('rc.stat', outf + '.rc.stat')	if os.path.exists('rc.stat') else None
    os.remove      ('rc.stat') 				if os.path.exists('rc.stat') else None
    
    # Store encoding time somewhere
    f = open(outf + '.ELAPSED.time','w')
    f.write(str(elapsed_time))
    #print 'FFMPEG took -> ' + str(elapsed_time) + ' milisec'
    
def run_ldecode(inpf):
    binary = '/home/tester/aplakh/ldecode'
    #args = [binary, '-i', inpf, '-o', 'RAW_' + inpf]
    args = [binary, '-i', inpf, '-o', '/dev/null']
    
    start_time = datetime.datetime.now()
    checked_run(args, redirect_output=inpf+'.ldecode.stdo.log')
    end_time = datetime.datetime.now()
    elapsed_time = int((end_time-start_time).total_seconds()* 1000)
    #print 'ldecode took -> ' + str(elapsed_time) + ' milisec'

def run_ffprobe(inpf):
    binary = '/home/tester/aplakh/ffprobe'
    args = [binary, '-show_frames', '-print_format', 'json', inpf]
    
    #show_frames -print_format json D:\New_folder123\out_5var\test_gop5_bframe0_bitrate20000000.H264
    
    start_time = datetime.datetime.now()
    checked_run(args, redirect_output = inpf + '.ffprobe.stdo.log', redirect_error = inpf + '.ffprobe.stde.log')
    end_time = datetime.datetime.now()
    elapsed_time = int((end_time-start_time).total_seconds()* 1000)
    #print 'FFPROBE took -> ' + str(elapsed_time) + ' milisec'
    
def get_psnr(ref, inpf):
    binary = '/home/tester/aplakh/ffmpeg'
    args = [binary, '-i', ref, '-i', inpf, '-lavfi', 'psnr=' + inpf + '.psnr.log', '-f', 'null', '-']
    
    start_time = datetime.datetime.now()
    checked_run(args, redirect_output = inpf + '.psnr.stdo.log', redirect_error = inpf + '.psnr.stde.log')
    end_time = datetime.datetime.now()
    elapsed_time = int((end_time-start_time).total_seconds()* 1000)
    #print 'PSNR took -> ' + str(elapsed_time) + ' milisec'
    
    #./ffmpeg -i crowd_run.mp4  -i test_gop5_bframe0_bitrate20000000.H264  -lavfi psnr="stats_file=psnr.txt" -f null -

def run_parse_quant(input_file):
    #print 'OLOLO'
    rg = r"(\d+)\(\s*(\w+)\s*\)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d\:\d\:\d)\s+(\d+)"
    
    frames_dict = dict()
    
    with open(input_file + '.ldecode.stdo.log') as f:
        for line in f:
	    result = re.match(rg, line)
	    if result:
		key = result.group(2)
		value = result.group(5)
		#print result.group(2), result.group(5)
		if key not in frames_dict:
		    frames_dict[key] = list()
		frames_dict[key].append(int(value))
    
    #print '\nQuantiser info'
    
    f_rez = input_file + '.REZULT.log'
    f = open(f_rez,'w')
    
    for key in frames_dict:
	#print   'Quantiser', key, '\t', 'max', max(frames_dict[key]), 'min', min(frames_dict[key]), 'average', sum(frames_dict[key])/len(frames_dict[key])
	f.write('QFrame ' + key + ' max ' + str( max(frames_dict[key])) + ' min ' + str(min(frames_dict[key])) + ' average ' + str(sum(frames_dict[key])/len(frames_dict[key])) + '\n')
    
    f.close()

def run_parse_probe(inpf):
    #print 'OLOLO'
    
    frames_dict = dict()

    import json
    from pprint import pprint

    with open(inpf + '.ffprobe.stdo.log') as data_file:
	data = json.load(data_file)
    
    #pprint(data)
    
    for i in data['frames']:
	key = i['pict_type']
	value = i['pkt_size']
	if key not in frames_dict:
	    frames_dict[key] = list()
	frames_dict[key].append(int(value))
	
    #print '\nFrame size info'
    
    f_rez = inpf + '.REZULT.log'
    f = open(f_rez,'a')
    
    for key in frames_dict:
	#print   'Framesize', key, '\t', 'max', max(frames_dict[key]), 'min', min(frames_dict[key]), 'average', sum(frames_dict[key])/len(frames_dict[key])
	f.write('Framesize ' + key + ' max ' + str(max(frames_dict[key])) + ' min ' + str(min(frames_dict[key])) + ' average ' + str(sum(frames_dict[key])/len(frames_dict[key])) + '\n')

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

def run_parse_window(inpf, gopsize, bitrate, fps=25.0):
    
    #print '\nBitrate info'
    
    gop_size = int(gopsize)
    
    frames_dict = dict()

    import json
    from pprint import pprint

    with open(inpf + '.ffprobe.stdo.log') as data_file:
	data = json.load(data_file)
    
    #pprint(data)
    
    frames = []
    gop_number = 0
    target_bitrate = gop_size/fps*int(bitrate)
    
    yy = 0
    
    f_rez = inpf + '.REZULT.log'
    f = open(f_rez,'a')
    
    for gop in chunker(data['frames'], gop_size):
	x = 0
	for frame in gop:
	    x = x + int(frame['pkt_size'])
	#print   'Gop#', gop_number, 8*x, target_bitrate, 'Diff', (8.0*x-target_bitrate)/target_bitrate*100.0
	#f.write('Gop# ' + str(gop_number) + ' ' + str(8*x) + ' ' + str(target_bitrate) + ' Diff ' + str((8.0*x-target_bitrate)/target_bitrate*100.0))
	# add logik to measure error!!!
	
	frame_diff = (8.0*x-target_bitrate)/target_bitrate*100.0
	
	E = 'OK'
	
	#if not (-10 <= frame_diff <= 0):
	#    E = 'ERROR'
	
	if frame_diff > 0:
	    E = 'ERROR'
	
	f.write('Gop# ' + str(gop_number) + ' Cur ' + str(8*x) + ' Exp ' + str(int(target_bitrate))  + ' Diff ' + str(frame_diff) + ' ' + E + '\n')
	gop_number = gop_number + 1
	yy = yy + x
	
    #print yy/1024, 'K'
    
def run_parse_psnr(input_file):
    #print 'OLOLO'
    rg = r"n:(\d+)\s+mse_avg:(\d+.\d+)\s+mse_y:(\d+.\d+)\s+mse_u:(\d+.\d+)\s+mse_v:(\d+.\d+)\s+psnr_avg:(\d+.\d+)\s+psnr_y:(\d+.\d+)\s+psnr_u:(\d+.\d+)\s+psnr_v:(\d+.\d+)\s+"
    
    psnr = []
    
    with open(input_file + '.psnr.log') as f:
        for line in f:
	    result = re.match(rg, line)
	    if result:
		key = result.group(6)
		psnr.append(float(key))
    
    #print '\nPSNR info'
    
    f_rez = input_file + '.REZULT.log'
    f = open(f_rez,'a')
    
    #for key in psnr:
    #print   'AvgPSNR', '\t', 'max', max(psnr), 'min', min(psnr), 'average', sum(psnr)/len(psnr)
    f.write('AvgPSNR ' + 'max ' + str(max(psnr)) + ' min ' + str(min(psnr)) + ' average ' + str(sum(psnr)/len(psnr)) + '\n')

def compare(curr, old):
    rg = r"Gop#\s+(\d+)\s+Cur\s+(\d+)\s+Exp\s+(\d+)\s+Diff\s+(-?\d+.\d+)\s+((?:ERROR|OK))"

    regPSNR = r"AvgPSNR\s+max\s+\d+.\d+\s+min\s+\d+.\d+\s+average\s+(\d+.\d+)"

    frames_dict = dict()
    
    from itertools import izip, izip_longest
    
    file1name = curr + '.REZULT.log'
    file2name = old  + '.REZULT.log'
    
    gop_ok1 = 0
    gop_ok2 = 0
    
    with open(file1name) as file1, open(file2name) as file2:
        for line1, line2 in izip(file1, file2):
            #print line1, line2
            res_p1 = re.match(regPSNR, line1)
            res_p2 = re.match(regPSNR, line2)
	    if res_p1:
		p1 = float(res_p1.group(1))
		if res_p2:
		    p2 = float(res_p2.group(1))
		    if p1 > p2:
			print 'PSNR test:: GOOD ::', 'CurrentBin', str(p1), 'OldBin', str(p2)
		    else:
			print 'PSNR test:: BAD  ::', 'CurrentBin', str(p1), 'OldBin', str(p2)
	    res_f1 = re.match(rg, line1)
            res_f2 = re.match(rg, line2)
            if res_f1:
        	if res_f1.group(5) == 'OK':
        	    gop_ok1 = gop_ok1 + 1
    	    if res_f2:
        	if res_f2.group(5) == 'OK':
        	    gop_ok2 = gop_ok2 + 1
    
    if gop_ok1 > gop_ok2:
	print 'GOP  test:: GOOD ::', 'CurrentBin', gop_ok1, 'OldBin', gop_ok2
    else:
	print 'GOP  test:: BAD  ::', 'CurrentBin', gop_ok1, 'OldBin', gop_ok2
    
    
    
    with open(curr + '.ELAPSED.time', 'r') as curftime:
        curtime=curftime.read().replace('\n', '')
        with open(old + '.ELAPSED.time', 'r') as oldftime:
    	    oldtime=oldftime.read().replace('\n', '')
    	    print 'Current bin time -> ', curtime, 'Old bin time -> ', oldtime
        	

def main(argv):
    inputfile = ''
    outputfile = ''
    bframes = ''
    gopsize = ''
    bitrate = ''
    #binary = ''
    
    try:
	opts, args = getopt.getopt(argv,"hi:f:g:b:")
    except getopt.GetoptError:
        print 'encode.py -i <inputfile> -f <bframes> -g <gopsize> -b <bitrate> -e <binary>'
	sys.exit(2)
    for opt, arg in opts:
	if opt == '-h':
    	    print 'encode.py -i <inputfile> -f <bframes> -g <gopsize> -b <bitrate> -e <ninary>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-f"):
    	    bframes = arg
    	elif opt in ("-g"):
    	    gopsize = arg
    	elif opt in ("-b"):
    	    bitrate = arg
    	#elif opt in ("-e"):
    	#    binary = arg
    	
    	
    working_dir = 'test/' + inputfile
    
    if not os.path.exists(working_dir):
	os.makedirs(working_dir)
    
    outputfile     = working_dir + '/'  + 'test_gop'     + gopsize + '_bframe' + bframes + '_bitrate' + bitrate + '.H264'
    outputfile_old = working_dir + '/'  + 'old_test_gop' + gopsize + '_bframe' + bframes + '_bitrate' + bitrate + '.H264'
    
    print '\nInput  file ->', inputfile
    print   'Output file ->', outputfile
    print   'GOP size    ->', gopsize
    print   'Bframes     ->', bframes
    print   'Bitrate     ->', bitrate
    #print   'Binary      ->', binary
    
    
    
    # Run encoder
    run_encoder(inputfile, outputfile,     bframes, gopsize, bitrate, 'ffmpeg')
    run_encoder(inputfile, outputfile_old, bframes, gopsize, bitrate, 'ffmpeg_31.10')
    
    #run_encoder(inputfile, outputfile,     bframes, gopsize, bitrate, 'ffmpeg_31.10')
    #run_encoder(inputfile, outputfile_old, bframes, gopsize, bitrate, 'ffmpeg_26.10')
    
    # Gather stats
    run_ldecode(outputfile)
    run_ffprobe(outputfile)
    get_psnr(inputfile, outputfile)
    
    run_ldecode(outputfile_old)
    run_ffprobe(outputfile_old)
    get_psnr(inputfile, outputfile_old)
        
    # Parse stats
    run_parse_quant (outputfile)
    run_parse_probe (outputfile)
    run_parse_psnr  (outputfile)
    run_parse_window(outputfile, gopsize, bitrate)

    run_parse_quant (outputfile_old)
    run_parse_probe (outputfile_old)
    run_parse_psnr  (outputfile_old)
    run_parse_window(outputfile_old, gopsize, bitrate)
    
    compare(outputfile, outputfile_old)
    
    os.remove      ('dataDec.txt') 				if os.path.exists('dataDec.txt') else None
    os.remove      ('log.dec')	 				if os.path.exists('log.dec')	 else None
    
if __name__ == "__main__":
    main(sys.argv[1:])

