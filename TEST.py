from DATAFILE import DATAFILE
import os
from pathlib import Path
from typing import List
import numpy as np
from scipy.interpolate import UnivariateSpline
from random import randint

class TEST:

    def __init__(self, d: DATAFILE, low_snap_threshold=0.38, high_snap_threshold=0.4, value_at_transition=0.3, low_total=25.0, mid_total=27.0, 
                    spline_total=2.15, peak=1.2, high_total=60.0, section_jaggedness=1.0, total_jaggedness=2.67, snap_vat=0.0):
        self.datafile = d
        self.lst = low_snap_threshold
        self.hst = high_snap_threshold
        self.vat = value_at_transition
        self.lt = low_total
        self.mt = mid_total
        self.st = spline_total
        self.p = peak
        self.ht = high_total
        self.sj = section_jaggedness
        self.tj = total_jaggedness
        self.sv = snap_vat
        self.data = d.cut_peak()[3:-4]

    def set_data_average(self):
        self.data = self.datafile.cut_average()[1][3:-4]

    def snappiness(self):
        self.set_data_average()
        data = self.data
        transition = 38
        tval = data[transition]
        lower = data[0:transition]
        diff = max(lower) - data[transition]
        return(tval, diff)

    def has_spring(self):
        self.set_data_average()
        transition = 38
        data = self.data
        lowersection = data[0:transition+1]
        upperlimit = max(lowersection)
        mind = lowersection.index(upperlimit)
        if (mind == transition):
            return(False)
        else:
            return(True)

    def spline_jaggedness(self):
        def spline(l: List):
            y = l
            time = []
            for x in range(len(y)):
                time.append(x)
            spline = UnivariateSpline(time, y, k=3)
            xs = np.linspace(0, len(time), len(time))
            spline.set_smoothing_factor(0.5)
            return(spline(xs))
        def cut_curve(d: DATAFILE):
            data = d.get_random_curve()
            transition = 41
            curve1 = data[0:transition]
            curve2 = data[transition+1:]
            return(curve1, curve2)
        def splinedata(d: DATAFILE):
            curve1, curve2 = cut_curve(d)
            spline1 = spline(curve1)
            spline2 = spline(curve2)
            return(spline1, spline2)
        d = self.datafile
        splines = splinedata(d)
        curves = cut_curve(d)
        differences = []
        for i in range(2):
            diff = []
            for x in range(len(splines[i])):
                diff.append(abs(splines[i][x] - curves[i][x]))
            differences.append(sum(diff[8:-8]))
        return differences

    def pt(self):
        self.set_data_average()
        data = self.data
        peak = abs(max(data))
        trough = abs(min(data))
        return(peak, trough)
    
    def total(self):
        self.set_data_average()
        total = 0
        for point in self.data:
            point=abs(point)
            total+=point
        return total

    def print_battery(self):
        print("val at transition, snappiness: ", self.snappiness())
        print("jaggedness: ", self.spline_jaggedness())
        print("combined spline: ", sum(self.spline_jaggedness()))
        print("peak/trough: ", self.pt())
        print("total: ", self.total())
        
    def classify(self):
        fails = []
        fail = False
        if (not self.has_spring()): 
            fails.append("fail: case does not have a spring")
            fail = True
        if (self.snappiness()[0] > self.vat and self.snappiness()[1] < self.lst):
            fails.append("fail by snappiness test")
            fail = True
        if (self.total() < self.lt and self.snappiness()[1] < self.hst):
            fails.append("fail by total magnitude test")
            fail = True
        if (self.total() < self.mt and sum(self.spline_jaggedness()) > self.st):
            fails.append("fail by low net/high friction test")
            fail = True
        if (self.pt()[0] > self.p):
            fails.append("fail by peak")
            fail = True
        if (self.total() > self.ht):
            fails.append("fail by total")
            fail = True
        if (self.spline_jaggedness()[0] > self.sj and self.spline_jaggedness()[1] > self.sj):
            fails.append("fail by section jaggedness")
            fail = True
        if (self.spline_jaggedness()[0] + self.spline_jaggedness()[1] > self.tj):
            fails.append("fail by total jaggedness")
            fail = True
        if (self.snappiness()[0] < self.sv):
            print("this case is very good")
            fail=False
        if fail:
            return(fails)
        else:
            return(["pass!"])
