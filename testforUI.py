from TESTclass import TEST
from DATAFILE import DATAFILE
from pathlib import Path
import os

def test():
    d = DATAFILE('/Users/julia/Desktop/28new.txt', has_ranking=False)
    t = TEST(d)
    for failure in t.classify():
        print(failure)
    names_file_read = open('/Users/julia/Desktop/file_ints.txt', 'r')
    taken = []
    for m in names_file_read.read():
        if m != '\n':
            taken.append(m)
    names_file_read.close()
    names_file_write = open('/Users/julia/Desktop/file_ints.txt', 'a')
    last = int(taken[-1])
    new = last+1
    os.rename('/Users/julia/Desktop/28new.txt', '/Users/julia/Desktop/case'+str(new)+'.txt')
    names_file_write.write(str(new))
    names_file_write.close()


test()