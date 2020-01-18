####
from rpi_ws281x import Color, PixelStrip, ws

LED_COUNT = 300         # Number of LED pixels.
LED_PIN = 18           # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000   # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10           # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 64   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False     # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_RGBW

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()


def render(current_led):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(12,34,0,0))
    strip.setPixelColor(current_led, Color(255,255,255,255))
    strip.show()

###
current_led = 0
def update(counter, pressed):
    current_led = counter % 300
    print('current', current_led)
    render(current_led)

###

import asyncio
from evdev import InputDevice, categorize, ecodes

dev = InputDevice('/dev/input/event0')

async def helper(dev):
    counter = 0
    pressed = False
    async for ev in dev.async_read_loop():
        if ev.type == ecodes.EV_REL and ev.code == ecodes.REL_DIAL:
            counter = counter + ev.value
            print('dial', counter)
            update(counter, pressed)
        elif ev.type == ecodes.EV_KEY and ev.code == ecodes.BTN_0:
            pressed = (ev.value == 1)
            print('button', pressed)
            update(counter, pressed)
        
loop = asyncio.get_event_loop()
loop.run_until_complete(helper(dev))

