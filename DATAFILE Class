import os
from pathlib import Path
from typing import List
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import wave
from scipy.fftpack import fft
from sklearn.cluster import KMeans
import math



#####################################################################
#####################################################################


class DATAFILE:
    def __init__(self, filename, num_passes, old=False):
        self.filename = filename
        self.raw_data = []
        self.subsections = []
        self.isold = old
        self.num_passes = num_passes


    #################################################################


    def get_new_data(self):
        fil = open(self.filename)
        rank = 0
        color = ""
        data = []
        newdata = []
        first = False
        marks = []

        i = 0
        for line in fil:
            if first:
                rank = float(line)
                first = False
            else:
                if (not line == '\n'):
                    line = str(line)
                    line = line.strip(' lbf\n')
                    newline: float = 0.0
                    if(line.startswith('- ')):
                        line = line[2:]
                        newline = float(line) * -1.0
                    else:
                        newline = float(line)
                    data.append(newline) 
                    marks.append(i)
                    i+=1

        for x in data:
            newdata.append(x)
        self.raw_data = newdata

        if(5<=rank and 6 >= rank):
            color = "blue"
        elif(rank < 5):
            color = "green"
        else:
            color = "red"  
        return (marks, newdata, color)


    #################################################################


    def get_old_data(self):
        fil = open(self.filename)
        data = []
        times = []
        ticks = []
        first = True
        rank = 0
        color = ""
        last = 0
        i = 0
        for line in fil:
            if first:
                rank = float(line)
                first = False
            else:
                if (not line == '\n'):
                    if (line.endswith('lbf\n')):
                        ticks.append(i)
                        i+=1
                        line = str(line)
                        line = line.strip(' lbf\n')
                        newline: float = 0.0
                        if(line.startswith('- ')):
                            line = line[2:]
                            newline = float(line) * -1.0
                        else:
                            newline = float(line)
                        data.append(newline) 
                    else:
                        if (not (float(line) > 60)):
                            times.append(float(line) + last)
                        else:
                            times.append(float(line) + last)
                            last = float(line) + last

        if(5<=rank and 6 >= rank):
            color = "blue"
        elif(rank < 5):
            color = "green"
        else:
            color = "red"  

        return (ticks, data, color)


    #################################################################


    def get_data(self):
        if self.isold:
            return self.get_old_data()
        else:
            return self.get_new_data()


    #################################################################

    
    def new_get_raw_data(self):
        data = self.get_new_data()
        self.raw_data = data[0]
        return self.raw_data


    #################################################################


    def old_get_raw_data(self):
        data = self.get_old_data()
        self.raw_data = data[0]
        return self.raw_data


    #################################################################


    def get_raw_data(self):
        if self.isold:
            data = self.get_old_data()
            self.raw_data = data[1]
        else:
            data = self.get_new_data()
            self.raw_data = data[0]
        return self.raw_data


    #################################################################


    def new_split_data(self):
        sections = []
        data = self.get_new_data()
        seg_length = int(len(data) / self.num_passes)
        previous = 0
        for current in range(1, self.num_passes):
            seg = data[0][previous*seg_length:current*seg_length]
            sections.append(seg)
        self.subsections = sections
        return ([sections], data[1])


    #################################################################


    def old_split_data(self):
        sections = []
        timesecs = []
        stuff = self.get_old_data()
        time = stuff[0]
        data = stuff[1]
        color = stuff[2]
        seg_length = int(len(data) / self.num_passes) + 1
        previous = 0
        for current in range(1, self.num_passes+1):
            seg = data[(previous*seg_length):(current*seg_length)]
            timesec = time[(previous*seg_length):(current*seg_length)]
            sections.append(seg)
            timesecs.append(timesec)
            previous+=1
        self.subsections = sections
        return (timesecs, sections, color)


    #################################################################


    def split_data(self):
        if self.isold:
            return self.old_split_data()
        else:
            return self.new_split_data()


    #################################################################


    def new_remove_plateaus(self):
        flat_split = []
        # tuple: ([[sect][ions]], color)
        split_data = self.new_split_data(self.num_passes)
        size = len(split_data[0])
        for updown in split_data[0]:
            maximum = max(updown)
            maxind = updown.index(maximum)
            minimum = min(updown)
            minind = updown.index(minimum)
            newupdown = updown[0:maxind]+updown[maxind+20:minind]+updown[minind+20:]
            flat_split.append(newupdown)
        return (flat_split, split_data[1])


    #################################################################


    def old_remove_plateaus(self):
        flat_split = []
        times = []
        # tuple: ([[time] [segments]], [[sect][ions]], color)
        split_data = self.split_data()
        size = len(split_data[0][0])
        ind = 0
        for updown in split_data[1]:
            maximum = max(updown)
            maxind = updown.index(maximum)
            newupdown = updown[0:maxind]+updown[maxind+20:]
            newtime = split_data[0][ind][0:maxind]+split_data[0][maxind+20:]
            times+=newtime
            flat_split+=newupdown
            ind+=1
        return (times, flat_split, split_data[2])

    
    #################################################################


    def remove_plateaus(self):
        if self.isold:
            return self.old_remove_plateaus()
        else:
            return self.new_remove_plateaus()


    #################################################################


    def get_average_curve(self):
        d = self.split_data()
        sections = self.subsections

        smallest = 900
        for lst in sections:
            if len(lst) < smallest:
                smallest = len(lst)
                
        avg_curve = []

        for i in range(0, smallest):
            s = 0
            for sec in sections:
                s+=sec[i]
            avg_curve.append(s/len(sections))

        if self.isold:
            return(d[0][0], avg_curve, d[2])
        else:
            return(0)


#####################################################################


    def cut_peak(self):
        data = self.get_data()[1]
        time = self.get_data()[0]
        newdata = data[0:42]+data[74:]
        newtimes = time[0:42]+time[74:]
        return(newtimes, newdata, self.get_data()[2])
                
