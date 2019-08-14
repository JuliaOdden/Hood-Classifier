from TESTclass import TEST
from DATAFILEclass import DATAFILE
import os

def test():
    print("Running tests... ")
    print
    d = DATAFILE('/home/pi/Desktop/hood_flex_motor/uart_log.txt', has_ranking=False)
    t = TEST(d)
    score, failures = t.classify()
    if score <= 1:
        print 'PASS'
    else:
        print 'FAIL'
        print
        for fail in failures:
            print(fail)
    print
    names_file_read = open('/home/pi/Desktop/hood_flex_motor/file_ints.txt', 'r+')
    taken = []
    for m in names_file_read.readlines():
        if m != '\n':
            taken.append(m+'\n')
    names_file_read.close()
    names_file_write = open('/home/pi/Desktop/hood_flex_motor/file_ints.txt', 'a')
    last = int(taken[-1].strip('\n'))
    new = last+1
    os.rename('/home/pi/Desktop/hood_flex_motor/uart_log.txt', '/home/pi/Desktop/hood_flex_motor/testcase'+str(new)+'.txt')
    names_file_write.write(str(new)+'\n')
    print('Data written to testcase'+str(new)+'.txt')
    print
    names_file_write.close()


test()
