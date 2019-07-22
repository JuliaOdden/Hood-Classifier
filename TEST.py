from various_get_datas import DATAFILE
import os
from pathlib import Path
from typing import List
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import figure
import numpy as np
from scipy.interpolate import UnivariateSpline

class TEST:

    def __init__(self, d: DATAFILE, peak_threshold=1.2, trough_threshold=1.0, min_threshold=1.6, max_threshold=2.2,
        s_jag_thresh=1.75, sim_thresh=0.25, hard_fail_peak=1.55, hard_fail_trough=2.25, 
        hard_fail_trilinear=3.0, click_threshold=0.07, click_lower_threshold=0.04, hard_min=0.52, spline_thresh=1.74):
        self.pthresh = peak_threshold
        self.tthresh = trough_threshold
        self.mthresh = min_threshold
        self.data = d.cut_peak()[1][3:-4]
        self.st = s_jag_thresh
        self.simt = sim_thresh
        self.hfp = hard_fail_peak
        self.hft = hard_fail_trough
        self.hftl = hard_fail_trilinear
        self.maxthresh = max_threshold
        self.clthresh = click_threshold
        self.chthresh = click_lower_threshold
        self.hmin = hard_min
        self.datafile = d
        self.sthresh = spline_thresh
    
    def gettransition(self):
        data = self.data
        slopes = []
        absslopes = []
        prev = 0
        for i in range(1, len(data)):
            absslope = abs(data[i] - data[prev])
            slope = data[i] - data[prev]
            absslopes.append(absslope)
            slopes.append(slope)
            prev+=1
        transition = absslopes.index(max(absslopes))
        lowerslopes = slopes[1:transition-1]
        upperslopes = slopes[transition+1:-1]

        return(transition, lowerslopes, upperslopes)

    # 1

    def trilinear_jaggedness(self):
        transition = self.gettransition()[0]
        data = self.data

        # lower
        lowersection = data[0:transition+1]

        upperlimit = max(lowersection)
        mind = lowersection.index(upperlimit)

        section1 = lowersection[0:mind+1]

        lowerlimit = min(lowersection[mind:])
        lind = lowersection[mind:].index(lowerlimit)+mind

        section2 = lowersection[mind:lind+1]

        if (lind == transition and not mind == transition):
            slope_line_1 = (max(section1) - section1[0]) / len(section1)
            init = section1[0]
            line1 = []
            for x in range(len(section1)):
                y = slope_line_1 * x + init
                line1.append(y)
            slope_line_2 = (min(section2) - section2[0]) / len(section2)
            init = section2[0]
            line2 = []
            for x in range(len(section2)):
                y = slope_line_2 * x + init
                line2.append(y)
            downjag = 0
            index = 0
            for point in section1:
                diff = abs(point - line1[index])
                downjag+=diff
                index+=1
            upjag = 0
            index = 0
            for point in section2:
                diff = abs(point - line2[index])
                upjag+=diff
                index+=1
            slopediff = abs(slope_line_1 - slope_line_2)
            return(round(downjag+upjag, 3), round(slopediff, 3))

        elif (mind == transition):
            return(0, 0)

        else:
            section3 = data[lind:transition+1]
            slope_line_1 = (max(section1) - section1[0]) / len(section1)
            init = section1[0]
            line1 = []
            for x in range(len(section1)):
                y = slope_line_1 * x + init
                line1.append(y)
            slope_line_2 = (min(section2) - section2[0]) / len(section2)
            init = section2[0]
            line2 = []
            for x in range(len(section2)):
                y = slope_line_2 * x + init
                line2.append(y)
            slope_line_3 = (max(section3) - section3[0]) / len(section3)
            line3 = []
            init = section3[0]
            for x in range(len(section3)):
                y = slope_line_3 * x + init
                line3.append(y)
            downjag = 0
            index = 0
            for point in section1:
                diff = abs(point - line1[index])
                downjag+=diff
                index+=1
            upjag = 0
            index = 0
            for point in section2:
                diff = abs(point - line2[index])
                upjag+=diff
                index+=1
            remainingjag = 0
            index = 0
            for point in section3:
                diff = abs(point - line3[index])
                remainingjag+=diff
                index+=1
            slopediff = abs(slope_line_1 - slope_line_2)
            return(round(upjag+downjag+remainingjag, 5), round(slopediff, 4))

    def slope_jaggedness(self):
        transition, lower, rise = self.gettransition()

        # lower

        lmag = 0
        prev = 0
        for point in range(1, len(lower)):
            diff = abs(lower[point] - lower[prev])
            lmag+=diff
            prev+=1

        # raise

        rmag = 0
        prev = 0
        for point in range(1, len(rise)):
            diff = abs(rise[point] - rise[prev])
            rmag+=diff
            prev+=1

        return(round(lmag+rmag, 3))


    def spline_jaggedness(self):

        def spline(d: DATAFILE):
            y = d.cut_peak()[1][0:38]
            time = []
            for x in range(len(y)):
                time.append(x)
            spline = UnivariateSpline(time, y)
            xs = np.linspace(0, len(time), len(time))
            spline.set_smoothing_factor(0.1)
            return(spline(xs))

        d = self.datafile
        s = spline(d)
        difference = 0
        for x in range(len(d.cut_peak()[1][0:38])):
            diff = abs(s[x] - d.cut_peak()[1][x])
            difference+=diff
        return difference

    # 2

    def pt(self):
        data = self.data
        peak = abs(max(data))
        trough = abs(min(data))
        return(peak, trough)

    # 3
    
    def sim(self):
        peak, trough = self.pt()
        return(round(abs(peak - trough), 3))
    
    # 4

    def compmag(self):
        peak, trough = self.pt()
        if(peak > trough):
            return "peak"
        else:
            return "trough"
    
    
    # TESTING

    def print_battery(self):
        print()
        print("spline jaggedness: ", self.spline_jaggedness())
        print("trilinear: ", self.trilinear_jaggedness()[0])
        print("slope jaggedness: ", self.slope_jaggedness())
        print("peak/trough: ", self.pt())
        print("p/t similarity: ",self.sim())
        print("p/t compare: ", self.compmag())
        print("combined magnitude: ", self.pt()[0]+self.pt()[1])
        print("clickiness: ", self.trilinear_jaggedness()[1])
        print("-----------------------------")
        print()
        

    
    def classify(self):
        fails = []
        fail = False
        if (self.trilinear_jaggedness()[0] == 0): 
            fails.append("fail by trilinear test")
            fail = True
        if (self.trilinear_jaggedness()[0] > self.hftl):
            fails.append("fail by trilinear threshold")
            fail = True
        if (self.pt()[0] > self.hfp):
            fails.append("fail by peak")
            fail = True
        if (self.pt()[0] < self.hmin):
            fails.append("fail by peak minimum")
            fail = True
        if (self.pt()[1] < self.hmin):
            fails.append("fail by trough minimum")
            fail = True
        if (self.pt()[1] > self.hft):
            fails.append("fail by trough")
            fail = True
        if (self.spline_jaggedness() > self.sthresh):
            if (self.pt()[1] > 1.4):
                fails.append("fail by spline/trough")
                fail = True
        if (self.slope_jaggedness() > self.st):
            if (not self.trilinear_jaggedness()[1] > self.clthresh):
                fails.append("fail by second derivative test")
                fail = True
        if (self.slope_jaggedness() < 0.7):
            if (self.trilinear_jaggedness()[1] < self.chthresh):
                fails.append("fail by flatness test")
                fail = True
        if (self.pt()[0] + self.pt()[1] > self.maxthresh):
            if(self.trilinear_jaggedness()[1] < self.clthresh):
                if(self.spline_jaggedness() > 1.5):
                    fails.append("fail by maximum/click comparison")
                    fail = True
        if (self.pt()[1]+self.pt()[0] < self.mthresh):
            if(self.trilinear_jaggedness()[1] < self.chthresh):
                fails.append("fail by minimum/click comparison")
                fail = True
        if (self.pt()[0] > self.pthresh):
            if(self.sim() > self.simt):
                fails.append("fail by peak/similarity comparison")
                fail = True
        if fail:
            return(fails)
        else:
            return(["pass!"])
