from TESTclass import TEST
from DATAFILEclass import DATAFILE
import os

def test(path):
    if os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            if not f.startswith(".DS_Store"):
                print(f)
                d = DATAFILE(path+'/'+f, has_ranking=False)
                t = TEST(d)
                score, fails = t.classify()
                if score <= 1:
                    print("PASS")
                else:
                    print("FAIL")
                    for failure in fails:
                        print(failure)
                print()
                print("---------------------------------")
                print()
    elif os.path.isfile(path):  
        d = DATAFILE(path, has_ranking=False)
        t = TEST(d)
        score, fails = t.classify()
        if score <= 1:
            return("PASS", fails)
        else:
            return("FAIL", fails)

test('/Users/julia/Desktop/halftests')
