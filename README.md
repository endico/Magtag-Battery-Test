# Magtag-Battery-Test
Send the battery voltage to Adafruit IO. Also count the number of network connection errors.

## Battery Voltage
Send the voltage of the battery to to the feed periodically so I can figure out at what point to give a warning that the battery is low. 3.3 volts looks good at the moment but maybe I can go lower after finding out how long the battery lasts with 10 minute deep sleeps.  
https://io.adafruit.com/endico/feeds/battery

## Network Connection Errors
This started with random ConnectionError crashes with either **unknown error** or **No network with that ssid**. Re-running the script right away usually worked but sometimes I had to try several times before it worked and sometimes I gave up and tried again later. The problem seemed to be worse in the evening. It turns out it was crashing because I wasn't catching the errors properly but I was still getting those errors so I decided to count them to see if there was a pattern.

When there's an error, increment a counter in alarm.sleep_memory[5] and the next time the board connects, sync the counter with Adafruit IO and zero out the counter.

At first after a failure to connect I would retry again after 3 seconds. Later I switched to 3 minutes and got very few errors after that. That might just be because I'm making less attempts but I wonder if my router was ignoring the MagTag because of its spammy behaviour. Looking at the REPL, the **No network with that ssid** errors seem to have disappeared but I'm still getting a few unknown errors.  
https://io.adafruit.com/endico/feeds/failures

This is the issue I created for the connection errors  
https://github.com/adafruit/circuitpython/issues/3772

The battery I'm using is the 3.7v 420mAh Lithium  Ion Battery
https://www.adafruit.com/product/4236
