import neopixel, machine
from time import sleep
import time
import uasyncio as asyncio
from easing import *

# :TODO: Unsure on naming of this mixin/class. Also once that's settled, move to another file.
class LedGestures:
    # set to a new color (tuple of rgbw color)
    async def until_color_changed(self, color):
        self.pixels.fill(color)
        self.pixels.write()

    # set to a new colors (list of individual pixel colors)
    async def until_colors_changed(self, colors):
        self.set_colors(colors)

    # Turn off the lights
    async def until_off(self): 
        self.pixels.fill((0,0,0,0))
        self.pixels.write()

    # Reset to the configured color
    async def until_reset(self):
        self.reset()

    # Shift pixels from their current state to a target state. Dest can be either a list of individual pixels or a RGBW tuple
    # :TODO: Allow easing type to be passed
    async def until_faded_to(self, dest, steps, step_delay=1):
        if not isinstance(dest, list):
            dest = [dest] * self.num_pixels
  
        colors_start = list(self.pixels)
        
        colors = dict()
        for i in range(self.num_pixels):
            colors[i] = (
                CubicEaseOut(start = colors_start[i][0], end = dest[i][0], duration = steps),
                CubicEaseOut(start = colors_start[i][1], end = dest[i][1], duration = steps),
                CubicEaseOut(start = colors_start[i][2], end = dest[i][2], duration = steps),
                CubicEaseOut(start = colors_start[i][3], end = dest[i][3], duration = steps)
            )

        for step in range(steps): 
            for p in range(self.num_pixels):
                self.pixels[p] = (
                    int(colors[p][0](step)),
                    int(colors[p][1](step)),
                    int(colors[p][2](step)),
                    int(colors[p][3](step))
                )

            self.pixels.write()  
            await asyncio.sleep_ms(step_delay)

# Abstraction for light control - this gets used for the shade and base.
class LedStrip(LedGestures): 
    def __init__(self, color, pin, num_pixels):
        self.color = LedStrip.hex_to_rgb(color) 
        self.num_pixels = num_pixels
        self.pin = pin

        self.pixels = neopixel.NeoPixel(machine.Pin(self.pin), self.num_pixels, bpp=4)
        self.default_pixels = [self.color] * self.num_pixels

    # Turn this LED Strip off
    def off(self):
        self.pixels.fill((0,0,0,0))
        self.pixels.write()

    # Set the pixels to colors specificed in a passed in list of individual pixels
    def set_colors(self, colors): 
        for i in range(self.num_pixels): 
            self.pixels[i] = colors[i]
        self.pixels.write()

    def reset(self):
        self.set_colors(self.default_pixels)

    # Convert hex colors to RGBW - Automatically flip full white to 0,0,0,255 (turn on warm white led
    # instead of each individual color)
    def hex_to_rgb(value):
        value = value.lstrip('#')
        rgb = tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
        return (0,0,0,255) if rgb == (255,255,255) else rgb + (0,)
