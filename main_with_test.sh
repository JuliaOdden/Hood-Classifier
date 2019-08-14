#!/bin/bash

for i in $(seq 1)
do
	python hood_flex_motor.py &
	python hood_flex_uart.py
	sleep 4s
	python testforUI.py
done
read -p "Press <enter> key to exit" x