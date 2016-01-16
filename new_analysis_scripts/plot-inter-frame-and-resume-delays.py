from __future__ import print_function
import os
import sys
import re
import pprint
import math
from decimal import *
import matplotlib
matplotlib.use('pdf') # Must be before importing matplotlib.pyplot or pylab! Default uses x window manager and won't work cleanly in cloud installations.
from matplotlib import collections
import numpy as np
import pylab
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
 
def main():
    if len( sys.argv ) is not 2:
        raise ValueError("Usage: python plot-inter-frame-delay.py inter-frame-delay-directory")
    delay_logs_folder = sys.argv[1]

    inter_frame_delays_list = []
    resume_delays_list = []
    for dirpath,_,filenames in os.walk(delay_logs_folder):
        for f in filenames:
            filepath = os.path.abspath(os.path.join(dirpath, f))
            match_object = re.search("inter-frame-delays.dat", filepath)
            if match_object: # change this to simpler match
                print("parsing " + filepath)
                with open(filepath) as delay_logfile:
                    for line in delay_logfile:
                        inter_frame_delays_list.append(Decimal(line))

            match_object = re.search("resume-delays.dat", filepath)
            if match_object:
                print("parsing " + filepath)
                with open(filepath) as resume_delay_logfile:
                    for line in resume_delay_logfile:
                        resume_delays_list.append(float(line))

    # TODO make CDF of inter_frame_delays_list
    #plt.plot(inter_frame_delays_list, color="blue")
    #plt.xlabel('Time in video (seconds)')
    #plt.ylabel('Stall duration (seconds)')
    #plt.ylim([-2, 20])
    #plt.xlim([-30, 920])
    #plt.savefig("inter-frame-delays-cdf.pdf")

    # TODO make CDF of resume_delays_list
    #plt.plot(resume_delays_list, color="blue")
    #plt.xlabel('Time in video (seconds)')
    #plt.ylabel('Stall duration (seconds)')
    #plt.ylim([-2, 20])
    #plt.xlim([-30, 920])
    #plt.savefig("resume-delays-cdf.pdf")

if __name__ == '__main__':
  main()
