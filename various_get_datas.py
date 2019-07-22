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
                

#####################################################################
#####################################################################

# folder = '/Users/julia/Desktop/newdata'
# files = os.listdir(folder)

# # # fil = '/Users/julia/Desktop/14long.txt'
# # # d = DATAFILE(fil, 3, old=True)
# # # data = d.get_data()[1]
# # # c = "blue"
# # # time = d.get_data()[0]
# # # figure("f", figsize = (10, 5))
# # # plt.yticks([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
# # # plt.plot(time, data, color = c, linewidth=1.0)
# # # plt.show()

# for f in files:
#     #if not f.startswith(".DS"):
#     if f.startswith("19"):
#         d = DATAFILE(folder+'/'+f, 3, old=True)
#         data = d.cut_peak()[1][3:-4]
# #         print(f, max(data), min(data))
#         c = d.cut_peak()[2]
#         time = d.cut_peak()[0][3:-4]
#         ticks = []
#         for x in range(len(time)):
#             ticks.append(x) 
#         # for dats in data:
#         # if c == "red":
#         #     if(min(data[10:48]) < 0.5):
#         #     #figure("red sections")
#         figure(f, figsize = (10, 5))
#         plt.plot(ticks, data, color = c, linewidth=1.0)
#         # elif c == "blue":
#         #     continue
#         #     # #figure("blue sections")
#         #     # plt.yticks([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
#         #     # figure("full tests", figsize = (10, 5))
#         #     # plt.plot(time, data, color = c, linewidth=1.0)
#         # else:
#         #     #figure("green sections")
#         #     if (max(data[10:48]) > 1.4):
#         #         figure(f, figsize = (10, 5))
#         #         plt.yticks([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
#         #         plt.plot(time, data, color = c, linewidth=1.0)
# plt.show()
        
        # x1: List[float] = []
        # x2: List[float] = []
        # x3: List[float] = []

        # for index in range(3):
        #     if index == 0:
        #         x1 = data[0]
        #     elif index == 1:
        #         x2 = data[1]
        #     else:
        #         x3 = data[2]
        
        # #x1 - x3
        # y13 = []
        # for index in range(0, len(x1)):
        #     y13.append(abs(x1[index]-x3[index]))
        # figure(f"{f} x1-x3")
        # print(f"{f} x1-x3")
        # print("average difference: ", sum(y13)/len(y13))
        # plt.plot(time, y13, color = c, linewidth=1.0)
        # plt.show()
        

        # #x2 - x3
        # y23 = []
        # for index in range(0, len(x1)):
        #     y23.append(abs(x2[index]-x3[index]))
        # figure(f"{f} x2-x3")
        # print(f"{f} x2-x3")
        # print("average difference: ", sum(y23)/len(y23))
        # plt.plot(time, y23, color = c, linewidth=1.0)
        # plt.show()
        
        # #x1 - x2  
        # y12 = []
        # for index in range(0, len(x1)):
        #     y12.append(abs(x1[index]-x2[index]))
        # figure(f"{f} x1-x2")
        # print(f"{f} x1-x2")
        # print("average difference: ", sum(y12)/len(y12))
        # plt.plot(time, y12, color = c, linewidth=1.0)
        # plt.show()



# PLOTTING STUFF

# for f in files:
#    if (not f.startswith(".DS")):
#        d = DATAFILE(folder+'/'+f, 3, old=True)
#        dat = d.get_data()
#        figure(f, figsize = (10,10))
#        plt.plot(dat[0][0:52], dat[1][0:52], color = dat[2], linewidth=1.0)

# plt.show()

# l14:List[list] = []
# l24:List[list] = []
# l19:List[list] = []

# master = [l14, l19, l24]

# for f in files:
#     if (not f.startswith(".DS")):
#         if(f.endswith(".log")):
#             print("LOGGING")
#             d = DATAFILE(folder+'/'+f, 3, old=False)
#             dat = d.get_data()[1]
#             if f.startswith("14"):
#                 l14.append(dat)
#             elif f.startswith("19"):
#                 l19.append(dat)
#             else:
#                 l24.append(dat)
#         elif f.endswith(".txt"):
#             print("TEXTING")
#             d = DATAFILE(folder+'/'+f, 3, old=True)
#             dat = d.get_data()[1]
#             if f.startswith("14"):
#                 l14.append(dat)
#             elif f.startswith("19"):
#                 l19.append(dat)
#             else:
#                 l24.append(dat)

# marks = []
# for x in range(len(master[0][0])):
#     marks.append(x)
        
# ind  = [14, 19, 24]
# for lst in master:
#    print(lst)
#    for sublist in lst:
#        plt.plot(marks[0:180], sublist[0:180], color = "blue", linewidth=1.0)
#    plt.show()



# #FFT STUFF

#Number of sample points
# N = 100

# # # sample spacing
# T = 1.0 / (2*N)
# x = np.linspace(0.0, N*T, N)

# X = []

# folder = '/Users/julia/Desktop/newdata'
# files = os.listdir(folder)

# print(files)

# color = ""
# figure("FFT stuff", figsize = (20,7))
# for datafile in files:
#     #if (not datafile.startswith(".DS")):
#     if (datafile.startswith("18") or datafile.startswith("24") or datafile.startswith("19") or datafile.startswith("6")):
#         print(datafile)
#         d = DATAFILE(folder+'/'+datafile, 3, old=True)
#         color = d.cut_peak()[2]
#         y = d.cut_peak()[1]
#         yf = (1.0/N)*fft(y)
#         xf = np.linspace(0.0, 1.0/(2.0*T), N)
#         log_yf = [math.log10(abs(i)) for i in yf]
#         X.append(log_yf)
#         plt.plot(xf, log_yf, color = color)

# kmeans = KMeans(n_clusters=2)  
# kmeans.fit(X) 
# print(kmeans.cluster_centers_)  
# print(kmeans.labels_) 
# plt.show()

plt.close('all')