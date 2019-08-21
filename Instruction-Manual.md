# Instruction Manual
## Putting the hood feel test onto a new Raspberry Pi

For convenience, and so you don’t have to dive into my code to edit file paths, I’m going to give exact instructions, including directories. Know that if you don’t make folders and move files the same way I do, and also don’t edit any of the directories, the test will not run. 

1)	First things first, make a new folder on the desktop. Name it *hood_flex_motor*.
2)	Into *hood_flex_motor*, place a) `main_with_test.sh`, b) `hood_flex_motor.py`, c) `hood_flex_uart.py`, d) `testRAISE.py` or `TESTclass.py`, e) `testforUI.py`, f) `datafileRAISE.py` or `DATAFILEclass.py`, g) `green.jpg`, h) a .txt file called `file_ints.txt` that contains just a 0 on the first line. For d) and f), the name of the file depends on where you took it from. The ones in this repository are `TESTclass.py` and `DATAFILEclass.py`.
3)	To make the `.sh` file executable, open a Linux terminal and run the following command: 
```
chmod +x /home/pi/Desktop/hood_flex_motor/main_with_test.sh
```

4)	Drop the `test.desktop` file onto the desktop. Try double-clicking it. If the motor starts moving and the test runs perfectly, you’re done! If not…
5)	Left click the `test.desktop` file (should be labeled *“TEST THAT CASE!”*). Go to *"Properties"*, then to *"Permissions"*.  Under *“Access Control”*, switch the *"Execute"* option to *“Anyone”*. Try it again.
6)	If a window pops up saying something like *“This file seems to be an executable. What would you like to do with it?”*, click on Files (the double-file icon in the top left) &rarr; Edit &rarr; Preferences &rarr; General &rarr; check the box next to *“Don't ask options on launch executable file”*. Try it again.
