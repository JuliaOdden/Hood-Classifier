from DATAFILE import DATAFILE
import os
from random import randint

class TEST:

    def __init__(self, d, low_snap_threshold=0.38, high_snap_threshold=0.4, value_at_transition=0.3, low_total=15.0, 
                    mid_total=25.0, peak=1.2, high_total=30.0, snap_vat=0.002):
        self.datafile = d
        self.lst = low_snap_threshold
        self.hst = high_snap_threshold
        self.vat = value_at_transition
        self.lt = low_total
        self.mt = mid_total
        self.p = peak
        self.ht = high_total
        self.sv = snap_vat
        self.data = d.get_data()

    def set_data_average(self):
        self.data = self.datafile.get_average_curve()[1]
    
    def slope_jaggedness(self):
        def getslopes(l):
            slopes = []
            prev = 0
            for obj in range(1, len(l)):
                slope = l[obj] - l[prev]
                slopes.append(slope)
                prev+=1
            return (slopes)
        data = self.datafile.get_random_curve()
        slopes = getslopes(data)
        five_slopes = []
        prev = 0
        for x in range(5, len(data), 5):
            slope = (data[x] - data[prev]) / 5
            five_slopes.append(slope)
            prev+=5
        differences = 0
        index = 0
        for big_slope in five_slopes:
            for x in range(5):
                differences+=(abs(big_slope - slopes[index]))
                index+=1
        return(differences)

    def snappiness(self):
        self.set_data_average()
        data = self.data
        transition = 40
        tval = min(data[10:])
        lower = data[0:transition]
        diff = max(lower) - data[transition]
        return(tval, diff)

    def has_spring(self):
        self.set_data_average()
        transition = 42
        data = self.data
        lowersection = data[0:transition+1]
        upperlimit = max(lowersection)
        mind = lowersection.index(upperlimit)
        if (mind == transition):
            return(False)
        else:
            return(True)
  
    def pt(self):
        self.set_data_average()
        data = self.data
        peak = abs(max(data))
        return(peak)
    
    def total(self):
        self.set_data_average()
        total = 0
        for point in self.data:
            point=abs(point)
            total+=point
        return total

    def print_battery(self):
        print("val at transition, snappiness: ", self.snappiness())
        print("peak: ", self.pt())
        print("total: ", self.total())
        print("jaggedness: ", self.slope_jaggedness())
        
    def classify(self):
        MFE = 0.8
        score = 0
        fails = []
        if (not self.has_spring()): 
            fails.append("fail: case does not have a spring")
            score += 100
        if (self.snappiness()[0] > 0.7):
            fails.append("fail vat test")
            score += 100
        if (self.snappiness()[0] > self.vat and self.snappiness()[1] < self.lst):
            fails.append("fail by snappiness test")
            score += 100
        elif (self.snappiness()[0] > self.vat - 0.1 and self.snappiness()[1] < self.lst + 0.1):
            fails.append("margin by snappiness test")
            score +=1
        if (self.total() < 0.3 and self.snappiness()[1] < self.hst):
            fails.append("fail by total magnitude test")
            score +=2
        elif (self.total() < self.lt + MFE and self.snappiness()[1] < self.hst + MFE):
            fails.append("margin by total magnitude test")
            score +=1
        if (self.total() < self.mt and self.slope_jaggedness() > 0.8):
            fails.append("fail by low net/high friction test")
            score +=2
        elif (self.total() < self.mt + MFE and self.slope_jaggedness() > 0.8 - MFE):
            fails.append("margin by low net/high friction test")
            score +=1
        if (self.pt() >= self.p + MFE):
            fails.append("fail by peak")
            score +=2
        elif (self.pt() > self.p and self.pt() < self.p + MFE):
            fails.append("margin by peak")
            score +=1
        if (self.total() >= self.ht):
            fails.append("fail by total")
            score +=2
        elif (self.total() > self.mt and self.total() < self.ht):
            fails.append("margin by total")
            score +=1
        if (self.slope_jaggedness() >= 0.5 + MFE):
            fails.append("fail by jaggedness test")
            score +=2
        elif (self.slope_jaggedness() > 0.5 and self.slope_jaggedness() < 0.5 + MFE):
            fails.append("margin by jaggedness test")
            score +=1
        if (self.snappiness()[1] < 0.2):
            fails.append("fail by raw snappiness test")
            score += 2
        if (self.snappiness()[0] <= self.sv):
            print("this case is very good")
            score = 0
        return score, fails