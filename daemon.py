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
def input_update(message, state):
    state["current_led"] = (state["current_led"] + message["delta"]) % 300
    return state

def update():
    state = { "current_led": 0 }
    while True:
        message = yield
        
        print(message)

        switcher = {
            "DialInput": input_update
        }
        transition = switcher.get(message["type"], lambda message, state: state)
        state = transition(message, state)

        print(state)
        render(state["current_led"])
###

async def tick(update):
    while True:
        update.send({ "type": "Tick" })
        await asyncio.sleep(0.1)

###

import asyncio
from evdev import InputDevice, categorize, ecodes

async def listen_to_dial(updater):
    dev = InputDevice('/dev/input/event0')
    pressed = False
    async for ev in dev.async_read_loop():
        if ev.type == ecodes.EV_REL and ev.code == ecodes.REL_DIAL:
            delta = ev.value
            print('turned', delta)
            print(updater)
            updater.send({"type": "DialInput", "delta": delta, "pressed": pressed})
        elif ev.type == ecodes.EV_KEY and ev.code == ecodes.BTN_0:
            pressed = (ev.value == 1)
            print('button', pressed)
            updater.send({"type": "DialInput", "delta": 0, "pressed": pressed})

###
        
async def main():
    updater = update()
    next(updater)
    updater.send({"type": "Init"})

    ticker = asyncio.create_task(tick(updater))
    listener = asyncio.create_task(listen_to_dial(updater))
    await listener

asyncio.run(main())

