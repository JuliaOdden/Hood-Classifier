import os
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
        return (ticks[0:44], data[0:44], color)

    def split_data(self):
        sections = []
        timesecs = []
        stuff = self.get_data()
        time = stuff[0]
        data = stuff[1]
        color = stuff[2]
        seg_length = 43
        self.num_passes = int(len(data) / seg_length)
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
        return(sections[r])

    def get_average_curve(self):
        d = self.split_data()
        sections = self.subsections
        smallest = 43
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
