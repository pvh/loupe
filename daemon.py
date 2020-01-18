import asyncio
from evdev import InputDevice, categorize, ecodes

dev = InputDevice('/dev/input/event0')

counter = 0

async def helper(dev):
    counter = 0
    pressed = False
    async for ev in dev.async_read_loop():
        if ev.type == ecodes.EV_REL and ev.code == ecodes.REL_DIAL:
            counter = counter + ev.value
            print('dial', counter)
        elif ev.type == ecodes.EV_KEY and ev.code == ecodes.BTN_0:
            pressed = (ev.value == 1)
            print('button', pressed)
        
loop = asyncio.get_event_loop()
loop.run_until_complete(helper(dev))
