# DATAFILE and TEST Classes
`DATAFILE` reads and interprets data taken from force tests on case hoods. `TEST` sorts cases into pass/fail based on information gathered from each case's `DATAFILE`.
## Overview
Notes on the test: each test is divided into different trials or cycles consisting of one raise of the hood and one lower, with pauses at the extremes of each. Pushing the case closed results in positive data; pulling it open reads as negative force. Hereafter, "peak" will be used to describe the maximum value obtained during the closing of the case and "trough" will describe **absolute value** of the minimum value obtained while opening the case.

Scroll to the bottom under **TEST/Functions/TEST.classify()** if you're looking for an outline of the tests I use to sort cases.

### Dependencies
#### DATAFILE
```python
import os
from pathlib import Path
from typing import List
```

#### TEST
```python 
from datafile import DATAFILE
import os
from pathlib import Path
from typing import List
import numpy as np
from scipy.interpolate import UnivariateSpline
```
`DATAFILE` is responsible for the interpretation of the data read from the mechanical test; it splices the data into trials and then into sections of trials by index and time. `DATAFILE` is designed to be closely compatible with the `matplotlib` library: it often returns x- and y-axes along with colors in tuples for ease of use.

`TEST` is a black-box class that takes a `DATAFILE` and a series of thresholds and spits out results in various formats (demonstrated in **Outputs**).

## Functionalities
### DATAFILE
#### Constructor
```python
d = DATAFILE(filename: str, num_passes: int, old: bool)
```
`filename` corresponds to the specific directory of the file containing the data from a test of any length on a single case. The `DATAFILE` class can handle any type of document supported by Python's built-in reader, including .txt files and .log files.

`num_passes` describes the length of the test (i.e. how many open/close cycles the case was put through)

`old` is a Boolean describing the type of the test, since the two variations, old and new, return data in different formats. If `old` is set to `True`, the class knows to expect time data along with force data.
#### Example Use
```python
folder = '~/hood_data_files'
files = os.listdir(folder)
for f in files:
    d = DATAFILE(filename=folder+'/'+f, num_passes=3, old=True)
    data = d.get_data()[1]
    time = d.get_data()[0]
    color = d.get_data()[2]
    figure(f, figsize = (10, 5))
    plt.plot(time, data, color = color, linewidth=1.0)
    plt.show()
```
#### Functions
`DATAFILE.get_data() -> Tuple(List[Float], List[Float], String)`

The most basic data-getting function returns a tuple of (0) either a list of times taken from the data file given to the class (if `old=True`) or a list of consecutive integers the same length as the given data file; (1) a list of the data points from the given data file; and (2) the string of a  color corresponding to the rating of the particular case (red for fail, blue for margin, green for pass) to help with data graphing and visualization. For training, the `DATAFILE` class expects the first line of every case's file to be that case's rating. For testing, enter the hidden `old_get_data()` and `get_new_data()` methods and change `first` to `False`.

`DATAFILE.get_raw_data() -> List[Float]`

This function works just like `get_data()` but only returns a list of the raw datapoints from the data file.

`DATAFILE.split_data() -> Tuple(List[List[Float]], List[List[Float]], String)`

`split_data()` is why the class asks for the number of trials performed on the case durind the test. This function divides the data up by each individual up/down cycle within the larger test and returns a tuple containing (0) a list of sublists, each sublist containing one pass worth of time stamps; (1) a list of sublists, each sublist containing one pass worth of data points; and (2) a string of the color associated with the case's ranking to facilitate graphing. `split_data()` works by dividing the overall length of the data list by the provided `num_passes`.

`DATAFILE.remove_plateaus() -> Tuple(List[List[Float]], List[List[Float]], String)`

If your test happens to contain plateaus of data that you don't care about, this function will remove those plateaus from every trial within the test and return a tuple of (0) a list of sublists, each of which contains one trial's worth of time data minus those points during which the test was at a plateau; (1) a list of sublists, each of which contains one trial's worth of data points, minus the plateaus; and (2) a string of the color associated with the case's rating to facilitate graphing. `remove_plateaus()` calls `split_data()`, then grabs the indeces of the maximum and minimum values on each sublist and removes them along with the 20 proceeding data points. For my purposes, that number is hard-coded.

`DATAFILE.get_average_curve() -> Tuple(List[Float], List[Float], String)`

#### NOTE: this function only works if `old=True`. Otherwise, it returns 0.

In the event that `num_passes` is greater than zero, you may want to create an average curve from each of those passes. This function returns a tuple of (0) a list of time values corresponding to the first trial in a test; (1) a list of data values averaged over every trial within a test; and (2) the color associated with the ranking of the case to facilitate graphing.

`DATAFILE.cut_peak() -> Tuple(List[Float], List[Float], String)`

#### NOTE: this function will only work if `old=True`. It assumes `num_passes=1`.

`cut_peak()` is very similar to `remove_plateaus()`, but more computationally efficient because it does a lot less. It cuts both the time and data lists of a data file to indeces `[0:42]` and `[74:]`. For my convenience, I hard-coded those numbers. This just removes the irrelevant data in the middle of the single-cycle tests I was doing. It returns a tuple of (0) a single list of non-continuous time signatures; (1) a single list of non-continuous data points; and (2) the color associated with the ranking of the case to facilitate graphing.

### TEST
#### Constructor
```python
t1 = TEST(d: DATAFILE, peak_threshold: float, trough_threshold: float, min_threshold: float, max_threshold: float,

s_jag_thresh: float, sim_thresh: float, hard_fail_peak: float, hard_fail_trough: float, hard_fail_trilinear: float, 

click_threshold: float, click_lower_threshold: float, hard_min: float, spline_thresh: float)

# OR, use default constructor:

t2 = Test(d: DATAFILE)
```

That's a lot of variables.

`d` corresponds to the `DATAFILE` for the case you're testing.

`peak_threshold` is a soft threshold used in conjunction with other tests (i.e., if you're above this threshold, it's not a hard fail, but you're on the edge). Defaults to 1.2.

`trough_threshold` is a slight misnomer as it should always be a positive value, since I'm measuring magnitude and not direction. That being said, like `peak_threshold`, it is a soft threshold. Defaults to 1.0.

`min_threshold` is another soft threshold corresponding to the minimum acceptable sum of the magnitudes of the peak and the trough. Defaults to 1.6.

`max_threshold` is also a soft threshold corresponding to the maximum acceptable sum of the magnitudes of the peak and the trough. Defaults to 2.2.

`s_jag_thresh` is where things get difficult. I have one test called `slope_jaggedness()` (further described in **Functions**), which assesses the second derivative at each point of the graph of the data to make sure the slope of the grsph isn't changing too much or too rapidly (indicating jagged behavior). This is a hard threshold; i.e. cases whose `slope_jaggedness()` functions exceed the given `s_jag_thresh` automatically fail. Defaults to 1.75. 

`sim_thresh` is a soft threshold describing the difference in magnitudes of the peak and the trough of the graph. Defaults to 0.25.

`hard_fail_peak` is a hard threshold describing the maximum acceptable force for the peak of the graph. Defaults to 1.55.

`hard_fail_trough` is a hard threshold describing the maximum acceptable magnitude of the lowest point on the graph. Defaults to 2.25.

`hard_fail_trilinear` corresponds to another jaggedness test (`trilinear_jaggedness()`) that measures deviation from a "curve" made up of one to three lines approximating the graph of the lowering of the hood. A case can fail just based on the trilinear test if it is best approximated by only a single line; otherwise, it is a hard threshold for jaggedness in lowering action. Defaults to 3.0.

`click_threshold` is a soft threshold describing the minimum "clickiness" of the case, which is determined by the comparative slopes of the first 2 lines created in the `trilinear_jaggedness()` test. Defaults to 0.07.

`click_lower_threshold` is a soft "clickiness" threshold used in conjunction with other tests. It describes the absolute minimum allowed clickiness gived a curve that's already pretty flat, as determined by overall magnitude and slope jaggedness. Defaults to 0.04.

`hard_min` is a hard threshold defining the lowest acceptable magnitude on both the peak and the trough. Defaults to 0.52.

`spline_thresh` is a hard threshold for yet another measure of jaggedness. I'll detail the `spline_jaggedness()` function firther in **functions**, but the basic idea is that I use `Scipy`'s spline functionality to make a smooth curve approximating the force graph and then find the magnitude of the difference between the approximation and the actual data points. It's similar to `trilinear_jaggedness()` (also detailed below) but a little more refined. Defaults to 1.74. 

#### Example Use
```python
folder = '~/datafiles'
files = os.listdir(folder)

for f in files:
    d = DATAFILE(folder+'/'+f, 3, old=True)
    c = d.get_data()[2]
    t = TEST(d)
    print()
    print(f)
    for failure in t.classify():
        print(failure)
```
#### Functions
`TEST.gettransition() -> Tuple(Int, List[Float], List[Float])` 

This is a hidden function that is very tightly applicable to my particular test; it takes the `cut_peak()` of the input `DATAFILE` and finds the index at which the test transitions from pushing the case shut to pulling it open. It returns a tuple with (0) the index of that transition, (1) a list containing the datapoints from before the transition, and (2) a list containing the datapoints from after the transition.

`TEST.trilinear_jaggedness() -> Tuple(Float, Float)` OR `Tuple(0, 0)`

First, this test asks the question: is the value at the point of transition (gathered from `gettransition()`) the maximum of the graph of the closing of the hood? If so, this indicates that there's no spring in the case and automatically returns (0, 0) and fails the case (it's the hardest threshold in the code!). If that's not true, we then ask if the value at the transition point is the minimum value on the graph of the closing of the hood. If it is, then we approximate the graph of the closing of the case with two lines: one beginning at the first point of the graph and ending at its maximum, and one beginning at its maximum and ending at the transition point. If the transition point is neither the maximum nor the minimum of the first half of the cycle, then we approximate the curve with three lines: one from the start to the maximum, one from the maximum to the following minimum, and one from that minimum to the transition point. Finally, the function takes each point in the dataset and calculates the magnitude of its distance from the line approximating that point on the curve and sums those distances to measure how irregular the curve is as a whole. As an extra, the function also calculates the magnitude of the difference between the slopes of lines 1 and 2 as a measure of clickiness. The function returns a tuple of (0) the sum of the distances between the graoh and the approximation, and (1) the "clickiness" measure.

`TEST.slope_jaggedness() -> Float `

As mentioned above, `slope_jaggedness()` is a sort of second derivative test that works by creating a list of the slopes at each point in the graph (unlike `trilinear_jaggedness()`, this function looks at the whole graph, not just the half corresponding to the lowering of the hood) and then finding the slope between each of those slopes and summing them. It returns that sum.

`TEST.spline_jaggedness() -> Float`

`Scipy` provides a "splining" functionality that essentially smooths a dataset to various degrees of accuracy. Here, I'm using it as an approximation of the graph of our data. Essentially, this function forms a spline approximation of the lowering of one cycle of the hood, finds the distance between the smooth version and the actual data points at each point, and then returns the net distance. The idea is that it measures point irregularities, or jaggedness/bumps/etc., in the graph.

`TEST.pt() -> Tuple(Float, Float)`

Returns a tuple with (0) the peak of the graph and (1) the absolute value of the trough of the graph.

`TEST.sim() -> Float`

Returns the difference between the magnitudes of the peak and the trough of the graph.

`TEST.compmag() -> String`

Reference function that returns "peak" or "trough," depending on which magnitude is larger.

`TEST.print_battery() -> None`

Neatly prints the results of each function described above without performing any classifications.


`TEST.classify() -> List[String]`

This is where we sort the case into either passing or failing, and ideally tells you why. The tests are as follows:

1) Does the trilinear jaggedness test return only (0, 0), indicating an approximation of only one line? If so, FAIL. The case has no spring.

    **Fail message**: "fail by trilinear test"

2) Does the value of the trilinear jaggedness test exceed the provided threshold? If so, FAIL. The case's action is too irregular.

    **Fail message**: "fail by trilinear threshold"

3) Does the value of the peak of the graph exceed the hard peak threshold? If so, FAIL. The case is too hard to close.

    **Fail message**: "fail by peak"

4) Does the value of the peak of the graph fall below the hard peak minimum threshold? If so, FAIL. The case is too soft.

    **Fail message**: "fail by peak minimum"

5) Does the value of the trough of the graph exceed the hard trough threshold? If so, FAIL. The case is too hard to open.

    **Fail message**: "fail by trough"

6) Does the value of the trough of the graph fall below the hard trough minimum threshold? If so, FAIL. The case is too soft.

    **Fail message**: "fail by trough minimum"

7) Does the value of the spline jaggedness test exceed the given hard threshold? Is the magnitude of the trough greater than 1.4 (hard-coded)? If so, FAIL. The case's action on the close is too jagged and it is too difficult to open.

    **Fail message**: "fail by spline/trough"

8) Does the value of the slope jaggedness test exceed the given hard threshold? If so, does the "clickiness" fall below the higher of the two thresholds? If so, FAIL. The case has too much overall friction to be snappy enough.

    **Fail message**: "fail by second derivative test"

9) Does the value of the slope jaggedness test fall below 0.7 (hard-coded)? If so, does the "clickiness" fall below the lower of the two thresholds? If so, FAIL. The case's action is too "flat": i.e., there are no features in the action.

    **Fail message**: "fail by flatness test"

10) Does the sum of the magnitudes of the peak and the trough exceed the provided maximum threshold? If so, does the clickiness given in the trilinear jaggedness test fall below the given clickiness threshold? If so, does the spline jaggedness exceed 1.5 (hard-coded)? If so, FAIL. The general resistance is too high.

    **Fail message**: "fail by maximum/click comparison"

11) Does the sum of the magnitudes of the peak and the trough fall below the provided minimum threshold? If so, does the clickiness given in the trilinear jaggedness test fall below the lower of the two clickiness thresholds? If so, FAIL. The general resistance is too low.

    **Fail message**: "fail by minimum/click comparison"

12) Does the peak exceed the given soft threshold? Is the difference between the magnitudes of the peak and the trough bigger than the given similarity threshold? If so, FAIL. The snap on the way down is too tough.

    **Fail message**: "fail by peak/similarity comparison"

If all of those cases are false, then the case passes.

## Outputs
### DATAFILE

Prints out lists (of tuples (of lists)) of numbers.

### TEST
#### With `TEST.print_battery()`
```
24.txt

spline jaggedness: 1.2213443786
trilinear:  0.88738
slope jaggedness:  0.938
peak/trough:  (0.846, 0.99)
p/t similarity:  0.144
p/t compare:  trough
combined magnitude:  1.8359999999999999
clickiness:  0.0301

-----------------------------
```
#### With `TEST.classify()`
```
37.txt
fail by flatness test

36.txt
pass!

32.txt
pass!

33.txt
fail by peak
fail by trough
fail by peak/similarity comparison

31.txt
fail by maximum/click comparison
fail by peak/similarity comparison
```
