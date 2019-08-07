# DATAFILE and TEST Classes, test() Function
`DATAFILE` reads and interprets data taken from force tests on case hoods. `TEST` sorts cases into pass/fail based on information gathered from each case's `DATAFILE`. `test(path)` is a helper function designed to black-box the whole process.
## Overview
Notes on the test: each test is divided into different trials or cycles consisting of one raise of the hood and one lower, with pauses at the extremes of each. Pushing the case closed results in positive data; pulling it open reads as negative force. Hereafter, "peak" will be used to describe the maximum value obtained during the closing of the case and "trough" will describe **absolute value** of the minimum value obtained while opening the case.

If you're looking for an outline of the tests used to sort the cases, jump here: **[TEST.classify()](https://github.com/JuliaOdden/Hood-Classifier/blob/master/README.md#testclassify---liststring)** .

### Dependencies
#### DATAFILE
```python
import os
from random import randint 
```

#### TEST
```python 
from DATAFILEclass import DATAFILE
import os
from random import randint
```

#### test() function
If you're running the `test()` function in a different file from where you have `DATAFILE` and `TEST`, you'll need to import those two as well as a couple other dependencies:
```python
from TESTclass import TEST
from DATAFILEclass import DATAFILE
import os
```
Otherwise, if you have `test()` defined under the `TEST` class, you don't have to import anything.

`DATAFILE` is responsible for the interpretation of the data read from the mechanical test; it splices the data into trials and then into sections of trials by index and time. `DATAFILE` is designed to be closely compatible with the `matplotlib` library: it often returns x- and y-axes along with colors in tuples for ease of use.

`TEST` is a black-box class that takes a `DATAFILE` and a series of thresholds and spits out results in various formats (demonstrated in **[Outputs](https://github.com/JuliaOdden/Hood-Classifier/blob/master/README.md#outputs)**).

`test()` is a simple helper function that takes a path (either to a file or a folder of files) and does all the grunt work of creating instances of `DATAFILE`s and `TEST`s. I highly recommend you use it, because otherwise things get very confusing.

## Functionalities
### DATAFILE
#### Constructor
```python
d = DATAFILE(filename: str, has_ranking: bool)
```
`filename` corresponds to the specific directory of the file containing the data from a test of any length on a single case. The `DATAFILE` class can handle any type of document supported by Python's built-in reader, including .txt files and .log files.

`has_ranking` is a Boolean asking whether or not the first line of the data file is a ranking for the case.
#### Example Use
```python
folder = '~/hood_data_files'
files = os.listdir(folder)
for f in files:
    if not f.startswith(".DS"):
        d = DATAFILE(filename=folder+'/'+f, has_ranking=True)
        data = d.get_data()[1]
        time = d.get_data()[0]
        color = d.get_data()[2]
        figure(f, figsize = (10, 5))
        plt.plot(time, data, color = color, linewidth=1.0)
        plt.show()
```
#### Functions
`DATAFILE.get_data() -> Tuple(List[Float], List[Float], String)`

The most basic data-getting function returns a tuple of (0) a list of times taken from the data file given to the class; (1) a list of the data points from the given data file; and (2) the string of a  color corresponding to the rating of the particular case (red for fail, blue for margin, green for pass) to help with data graphing and visualization (if `has_ranking=True`).

`DATAFILE.split_data() -> Tuple(List[List[Float]], List[List[Float]], String)`

`split_data()` divides the data up by each individual up/down cycle within the larger test and returns a tuple containing (0) a list of sublists, each sublist containing one pass worth of time stamps; (1) a list of sublists, each sublist containing one pass worth of data points; and (2) a string of the color associated with the case's ranking to facilitate graphing.

`DATAFILE.get_random_curve() -> List[Float]`

This function calls `split_data()` and then selects a random subsection of data to return.

`DATAFILE.get_average_curve() -> Tuple(List[Float], List[Float], String)`

You may want to create an average curve from each pass in a test. This function returns a tuple of (0) a list of time values corresponding to the first trial in a test; (1) a list of data values averaged over every trial within a test; and (2) the color associated with the ranking of the case to facilitate graphing. If there's only one pass, it just returns the data from that pass.

`DATAFILE.cut_average() -> Tuple(List[Float], List[Float], String)`

`cut_average()` slices apart the average curve obtained in `get_average_curve()` to remove the upper and lower plateaus in the data. It returns a tuple of (0) a list of continuous x-coordinates (a.k.a. time stamps); (1) a list of noncontinuous data points, cut from indeces 0 to 42 and 74 onwards; and (2) the color associated with the ranking of the case to facilitate graphing.

`DATAFILE.cut_peak() -> Tuple(List[Float], List[Float], String)`

`cut_peak()`, just like `cut_average`, cuts the data list of a data file to indeces `[0:42]` and `[74:]`. For my convenience, I hard-coded those numbers. This just removes the irrelevant data in the middle of the single-cycle tests I was doing. It returns a tuple of (0) a single list of continuous time signatures; (1) a single list of non-continuous data points; and (2) the color associated with the ranking of the case to facilitate graphing.

`DATAFILE.cut_subsections() -> None`

`cut_subsections()` basically just runs `cut_peak` on each of the subsections in the test as created by `split_data()`. It returns nothing, but edits each section `self.subsections`, cutting out the worthless plateau data.

`DATAFILE.get_extreme_curve() -> List[Float]`

This function takes every subsection of a test and forms a new curve out of the most extreme value taken at each point. It returns a list of new y-coordinates the same length as a data set in `self.subsections()` after it's been edited with `cut_subsections()`.



### TEST
#### Constructor
```python
t = TEST(self, d: DATAFILE, low_snap_threshold: float, high_snap_threshold: float, value_at_transition: float, low_total: float, mid_total: float, peak: float, high_total: float, snap_vat: float)

# OR, use the default constructor:

t = Test(d: DATAFILE)
```

That's a lot of variables.

`d` corresponds to the `DATAFILE` for the case you're testing.

`low_snap_threshold` is the lower of the two minimum thresholds for snappiness as determined by `TEST.snappiness()` (detailed in **Functions**). Defaults to 0.38.

`high_snap_threshold` is the (slightly) higher minimum threshold for snappiness, used in conjunction with a test of the overall magnitude of the force of the hood (detailed in **[TEST.classify()](https://github.com/JuliaOdden/Hood-Classifier/blob/master/README.md#testclassify---liststring)**). Defaults to 0.4.

`value_at_transition` sets a maximum value for the force required to close the case at the exact moment when the closing process finishes. Defaults to 0.3.

`low_total` is one of three soft minimum thresholds for the overall magnitude of the force of the hood (i.e. the sum of the absolute value of every value in the dataset, excluding plateaus). This is a low threshold--cases falling below `low_total` are put in contention to fail. Used in conjunction with `high_snap_threshold`. Defaults to 25.0.

`med_total` is the second soft minimum threshold for the overall magnitude of the force of the hood. Used in conjunction with the jaggedness/high-friction test (see **TEST.spline_jaggedness()** for details). Defaults to 27.0. This is also a low threshold, like `low_total`.

`peak` is a hard threshold defining the maximum allowable force necessary to close the case. Defaults to 1.2.

`high_total` is the third threshold, and the high threshold, for force magnitude. This one is a hard threshold that defaults to 60.0--i.e. any case with a magnitude over 60.0 will automatically fail.

`snap_vat` defaults to 0 and should never be changed. "VAT" stands for "value at transition," or the value the graph takes at the last point of its lowering curve, right before it starts to be raised. If the VAT is less than zero, that indicates the case is pulling itself shut, exactly as it should be. This threshold can override previous fails, as detailed in `TEST.classify()`.


#### Example Use
```python
folder = '~/datafiles'
files = os.listdir(folder)

for f in files:
    d = DATAFILE(folder+'/'+f, has_ranking=True)
    c = d.get_data()[2]
    t = TEST(d)
    print(f)
    for failure in t.classify():
        print(failure)
```
NB: If you're relying on this GitHub repo, you'll never have to use the constructor for TEST. Included in the repository is a function called **[test()](https://github.com/JuliaOdden/Hood-Classifier/blob/master/README.md#test-2)**, which will automatically create instances of `TEST` and takes a path to either individual filenames or folders of data files as input.

#### Functions
`TEST.set_data_average() -> None`

This is a hidden function that sets the `self.data` of your instance of the `DATAFILE` class to the `cut_average()` of the `DATAFILE` 'd' given in the constructor of `TEST`. 

`TEST.has_spring() -> Bool`

Basically, this function asks if the first half of the curve (the lowering of the hood) takes its maximum at the point of transition, or at the very end of the lowering process. If so, it indicates that there is no snap whatsoever in the case, or that it is missing its spring. Returns `True` if there is a spring, `False` if there is not.

`TEST.slope_jaggedness() -> Float`

`slope_jaggedness` is how I measure the irregularity in the action of the case. First, the function finds the slope between every two consecutive points in the dataset. Then, it finds the slope every five data points (e.g. between points 0 and 5, points 5 and 10, etc.). Finally, it finds the difference between each of the five two-point slopes that fall in the five-point section and compares each small slope to the longer slope. It returns the sum of the magnitudes of differences between each small slope and the long slope into which it fits.

`TEST.pt() -> Tuple(Float, Float)`

Returns a tuple with (0) the peak of the graph and (1) the absolute value of the trough of the graph.

`TEST.total() -> Float`

Returns the sum of the absolute value of every point in the data set.

`TEST.print_battery() -> None`

Neatly prints the results of each function described above without performing any classifications.

#### `TEST.classify() -> List[String]`

This is where we sort the case into either passing or failing, and ideally tells you why. Each fail message is appended to a list of failures, returned at the end of the testing process. Each test also has a margin of error (a slight misnomer: it actually loosens the thresholds, causing cases that might otherwise pass to read as "margin" in some aspects, instead of allowing failing cases to pass or read as "margin"), which defaults to 0.8 but in the snappiness test is set to 0.1. Note that for each test, if a case falls within the margin of error but NOT within the tighter failing constraint, the case will read margin for that test. 

The tests are as follows:

1) Does the `has_spring` test return `False`? If so, FAIL. The case does not have a spring.

    **Fail message**: "fail: case does not have a spring"

2) Is the VAT of the case above the `value_at_transition` threshold and is the snappiness below the `low_snap_threshold`? If so, FAIL. The case is not snappy enough.

    **Fail message**: "fail by snappiness test"

3) Does the value of the total magnitude of the case fall below the `low_threshold` and does the snappiness fall below the `high_snap_threshold`? If so, FAIL. The case's action is too soft.

    **Fail message**: "fail by total magnitude test"

4) Does the value of the total magnitude of the case fall below `mid_threshold` and does the total slope jaggedness fall above 4.0? If so, FAIL. The case has disproportionately high friction and jaggedness for its soft action.

    **Fail message**: "fail by low net/high friction test"

5) Does the value of the peak of the graph exceed the hard `peak` threshold? If so, FAIL. The case is too hard to close.

    **Fail message**: "fail by peak"

6) Does the value of the total magnitude of the case fall above `high_total`? If so, FAIL. The case is too stiff.

    **Fail message**: "fail by total"
   
7) Does the slope jaggedness fall above 5.0? If so, FAIL. The case is too irregular and/or choppy.

    **Fail message**: "fail by jaggedness test"

8) Does the VAT fall below the `snap_vat` threshold (or 0)? If so, the case automatically PASSES. It is clicky enough to make up for other faults.

    **Pass message**: "this case is very good"

If all of those cases are false, then the case passes, and the function will return `[pass!]`.


### test()
#### Constructor
```python
test('~/data_file.txt')
```
OR
```python
test('~/folder_of_data_files')
```
Note that `test()` takes either a path to a single file or a directory. You don't have to tell it anything; it sorts out what you want internally. 

#### How It Works

`test()` does three main things: first, it decides whether you're testing on a folder or a single file; next, it either makes a single `DATAFILE` instance or an instance for every file in the folder; and third, it either makes a single `TEST` instance or an instance for each `DATAFILE` it created. Then, it simply runs `TEST.classify()` on the relevant file(s) and neatly prints the results. The main purpose of this function is to avoid ugly list parsing and constructors.

## Outputs
Note that you don't actually have to care about the outputs from `DATAFILE` or `TEST` unless you want to edit the `test()` function to print out more or less information for you.
### DATAFILE

Prints out lists (of tuples (of lists)) of numbers.

### TEST
#### With `TEST.classify()`
```
this case is very good
['pass!']
['fail by peak', 'fail by total']
['margin by peak', 'fail by total']
```
#### With `TEST.print_battery()`
```
22new.txt
green
val at transition, snappiness:  (-0.1, 1.1360000000000001)
jaggedness:  [0.9790416090306655, 1.0640769644569734]
combined spline:  2.043118573487639
peak/trough:  (1.036, 0.844)
total:  46.09200000000001
3redone.txt
blue
val at transition, snappiness:  (0.134, 1.142)
jaggedness:  [0.7979339856927536, 1.1059015328173734]
combined spline:  1.903835518510127
peak/trough:  (1.276, 0.984)
total:  61.78800000000002
```
### test() function
```
6new.txt
red
fail by snappiness test
fail by section jaggedness
fail by total jaggedness

---------------------------------

8new.txt
blue
fail by total magnitude test

---------------------------------

27new.txt
green
this case is very good
pass!

---------------------------------
```
