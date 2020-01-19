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

import math

def render(state):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0,0))

    current_led = state["current_led"]
    new_region = state.get("new_region")

    regions = state.get("regions")
    for r in regions:
        extent = sorted((r[0], r[1]))
        for p in range(*extent):
            strip.setPixelColorRGB(p, *wheel(r[2]))

    brightness = math.floor( (math.sin(state["tick"] * 0.375) + 1) * 32)

    if new_region:
        new_region_color = state.get("new_region_color", 0)
        for p in range(*sorted(new_region)):
            strip.setPixelColorRGB(p, *wheel(new_region_color), brightness)
    
    pixel = strip.getPixelColorRGB(current_led)
    strip.setPixelColorRGB(current_led, pixel.r, pixel.g, pixel.b, brightness)

    strip.show()

###
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def input_update(message, state):
    if "new_region_color" in state:
        delta = message.get("delta", 0)
        pressed = message.get("pressed", False)
        if delta != 0:
            state["new_region_color"] = (state["new_region_color"] + message["delta"]) % 255
        elif pressed:
            state["regions"].append( (*state["new_region"], state["new_region_color"]) )
            del state["new_region_color"]
            del state["new_region"]
    else:
        if "delta" in message:
            state["current_led"] = (state["current_led"] + message["delta"]) % 300

        pressed = message.get("pressed", None)
        if pressed == True and not "new_region" in state:
            state["new_region"] = (state["current_led"], state["current_led"])
        elif "new_region" in state:
            if pressed == False: 
                if state["new_region"][0] == state["new_region"][1]:
                    del state["new_region"]
                else:
                    state["new_region_color"] = 0
            else:
                state["new_region"] = ( state["new_region"][0], state["current_led"] )

    return state

def update():
    state = { "current_led": 0, "tick": 0, "regions": [] }
    while True:
        message = yield
        
        print(message)

        switcher = {
            "DialInput": input_update,
            "Tick": (lambda message, state: state.update({"tick": message["tick"]}) or state)
        }
        transition = switcher.get(message["type"], lambda message, state: state)
        state = transition(message, state)

        print(state)
        render(state)
###

async def tick(update):
    tick = 0
    while True:
        update.send({ "type": "Tick", "tick": tick })
        tick = tick + 1
        await asyncio.sleep(0.05)

###

import asyncio
from evdev import InputDevice, categorize, ecodes

async def listen_to_dial(updater):
    dev = InputDevice('/dev/input/event0')
    async for ev in dev.async_read_loop():
        if ev.type == ecodes.EV_REL and ev.code == ecodes.REL_DIAL:
            delta = ev.value
            print('turned', delta)
            updater.send({"type": "DialInput", "delta": delta})
        elif ev.type == ecodes.EV_KEY and ev.code == ecodes.BTN_0:
            pressed = (ev.value == 1)
            print('button', pressed)
            updater.send({"type": "DialInput", "pressed": pressed})

###
        
async def main():
    updater = update()
    next(updater)
    updater.send({"type": "Init"})

    ticker = asyncio.create_task(tick(updater))
    listener = asyncio.create_task(listen_to_dial(updater))
    await listener

asyncio.run(main())

