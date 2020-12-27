# See what voltage the battery is at when the MagTag
# dies count network errors. Store the number of
# conneciton errors in alarm.sleep_memory[5] and
# send that number to adafruit_io the next time a
# conneciton is made. Also send battery voltage.

import alarm
import time
import board
import displayio
import adafruit_requests
import socketpool
import wifi
import ssl
from secrets import secrets
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
display = board.DISPLAY

# sleep a bit so there's time to open the REPL
# before the print first statement
time.sleep(10)

medium_font = bitmap_font.load_font("Arial-18.bdf")
main_group = displayio.Group(max_size=7)
margin = 10

connection_errors_text = label.Label(
    medium_font,
    max_glyphs=60,
    text="...",
    color=0xFFFFFF,
    anchor_point=(0.0, 0.0),
    anchored_position=(margin, margin),
)
main_group.append(connection_errors_text)

voltage_text = label.Label(
    medium_font,
    max_glyphs=30,
    text="...",
    color=0xFFFFFF,
    anchor_point=(0.0, 0.0),
    anchored_position=(margin, (display.height/2))
)
main_group.append(voltage_text)

magtag = MagTag()

# Reset the count if we haven't slept yet.
if not (alarm.wake_alarm):
    # Use byte 5 in sleep memory. This is just an example.
    alarm.sleep_memory[5] = 0
    print("WAKEY WAKEY")

connection_errors_text.text = f'failed connections: {alarm.sleep_memory[5]}'
voltage = magtag.peripherals.battery
voltage_text.text = f'battery: {voltage} V'
print(f'battery: {voltage} V')

def tellAdafruitIO(feed_name, value):
    try:
        aio_username = secrets["aio_username"]
        aio_key = secrets["aio_key"]
        # Initialize an Adafruit IO HTTP API object
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())
        io = IO_HTTP(aio_username, aio_key, requests)
        try:
            feed = io.get_feed(feed_name)
        except AdafruitIO_RequestError:
            # If feed doesn't exist, create it
            feed = io.create_new_feed(feed_name)
        io.send_data(feed["key"], value)
    except (ConnectionError, OSError, RuntimeError, ValueError) as e:
        print(f'Error in tellAdafruitIO - {e}')
        al = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 30)
        alarm.exit_and_deep_sleep_until_alarms(al)
    return

try:
    magtag.network.connect()
except (RuntimeError, ValueError) as e:
    print(f'RuntimeError in magtag.network.connect - {e}')
    al = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 30)
    alarm.exit_and_deep_sleep_until_alarms(al)
except (ConnectionError) as e:
    print(f'ConnectionError in magtag.network.connect - {e}')
    # count number of conneciton errors
    alarm.sleep_memory[5] = (alarm.sleep_memory[5] + 1) % 256
    al = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 30)
    alarm.exit_and_deep_sleep_until_alarms(al)
except (OSError) as e:
    print(f'An OSError occured in magtag.network.connect - {e}')
    al = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 30)
    alarm.exit_and_deep_sleep_until_alarms(al)

tellAdafruitIO("battery", voltage)
tellAdafruitIO("failures", alarm.sleep_memory[5])
# zero out number of unsucsessful connection tries
alarm.sleep_memory[5] = 0
display.show(main_group)
display.refresh()

# wait for the screen to finish refreshing then deep sleep
while display.busy:
    pass
print("nighty nite")
al = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 600)
alarm.exit_and_deep_sleep_until_alarms(al)