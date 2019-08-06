import os
from pathlib import Path
from typing import List
from random import randint 

class DATAFILE:
    def __init__(self, filename, has_ranking=False):
        self.filename = filename
        self.raw_data = []
        self.subsections = []
        self.num_passes = 0
        self.hr = has_ranking

    def get_data(self):
        fil = open(self.filename)
        data = []
        times = []
        ticks = []
        first = self.hr
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
        elif(rank < 5 and 0 < rank):
            color = "green"
        elif(rank > 6):
            color = "red"  
        else:
            color = "no ranking"
        return (ticks, data, color)

    def split_data(self):
        sections = []
        timesecs = []
        stuff = self.get_data()
        time = stuff[0]
        data = stuff[1]
        color = stuff[2]
        seg_length = 120
        self.num_passes = int(len(data) / 120)
        previous = 0
        for current in range(1, self.num_passes+1):
            seg = data[(previous*seg_length):(current*seg_length)]
            timesec = time[(previous*seg_length):(current*seg_length)]
            sections.append(seg)
            timesecs.append(timesec)
            previous+=1
        self.subsections = sections
        return(timesecs, self.subsections, color)

    def get_random_curve(self):
        d = self.split_data()
        sections = self.subsections
        le = len(sections)-1
        r = randint(0, le)
        return(sections[r][0:42]+sections[r][74:])

    def get_average_curve(self):
        d = self.split_data()
        sections = self.subsections
        smallest = 900
        for lst in sections:
            if len(lst) < smallest:
                smallest = len(lst)
        ticks = []
        for x in range(smallest):
            ticks.append(x)
        avg_curve = []
        for i in range(0, smallest):
            s = 0
            for section in sections:
                s+=section[i]
            avg_curve.append(s/len(sections))
        return(ticks, avg_curve, d[2])

    def cut_average(self):
        time, data, c = self.get_average_curve()
        newdata = data[0:42]+data[74:]
        times = []
        for x in range(len(newdata)):
            times.append(x)
        return(times, newdata, c)

    def cut_peak(self):
        data = self.get_data()[1]
        newdata = data[0:42]+data[74:]
        newtimes = []
        for x in range(len(newdata)):
            newtimes.append(x)
        return(newtimes, newdata, self.get_data()[2])

    def cut_subsections(self):
        data = self.split_data()[1]
        newsections = []
        for subsection in data:
            newsection = subsection[0:42]+subsection[74:]
            newsections.append(newsection)
        self.subsections = newsections

    def get_extreme_curve(self):
        self.cut_subsections()
        length = len(self.subsections[0])
        extreme_curve = []
        for i in range(length):
            extreme = 0
            for subsection in self.subsections:
                if(abs(subsection[i]) > extreme):
                    extreme = subsection[i]
            extreme_curve.append(extreme)
        return(extreme_curve)
