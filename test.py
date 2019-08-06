from TESTclass import TEST
from DATAFILE import DATAFILE
import os
from pathlib import Path

def test(path):
    if os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            if not f.startswith(".DS_Store"):
                print(f)
                d = DATAFILE(path+'/'+f, has_ranking=True)
                print(d.get_data()[2])
                t = TEST(d)
                for failure in t.classify():
                    print(failure)
                print()
                t.print_battery()
                print()
                print("---------------------------------")
                print()
    elif os.path.isfile(path):  
        print(path)
        d = DATAFILE(path+'/'+f, has_ranking=True)
        t = TEST(d)
        for failure in t.classify():
            print(failure)
        t.print_battery()

test('/Users/julia/Desktop/share')
