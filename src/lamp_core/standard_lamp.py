import gc
from behaviours.lamp_fade_in import LampFadeIn
from behaviours.lamp_idle import LampIdle
from components.led.neopixel import NeoPixel
from components.network.bluetooth import Bluetooth
from components.touch.touch import Touch
from lamp_core.lamp import Lamp
from lamp_core.frame_buffer import FrameBuffer
from utils.hex_to_rgbw import hex_to_rgbw
from utils.config import merge_configs

default_config = {
    "base":  { "pin": 12, "pixels": 40, "bpp": 4 },
    "shade": { "pin": 27, "pixels": 40, "bpp": 4 },
    "touch": { "pin": 32 },
    "lamp":  { "default_behaviours": True, "debug": False },
}

# Use standard lamp to startup a lamp that uses the kicad connection layout
class StandardLamp(Lamp):
    def __init__(self, name, base_color, shade_color, config_opts = None, post_process_function = None):
        super().__init__(name)

        config = default_config.copy()

        merge_configs(config, config_opts)

        if post_process_function is not None:
            self.base = FrameBuffer(hex_to_rgbw(base_color), config["base"]["pixels"], NeoPixel(config["base"]["pin"], config["base"]["pixels"], config["base"]["bpp"]), post_process_function=post_process_function)
        else:
            self.base = FrameBuffer(hex_to_rgbw(base_color), config["base"]["pixels"], NeoPixel(config["base"]["pin"], config["base"]["pixels"], config["base"]["bpp"]))

        self.shade = FrameBuffer(hex_to_rgbw(shade_color), config["shade"]["pixels"], NeoPixel(config["shade"]["pin"], config["shade"]["pixels"], config["shade"]["bpp"]))
        self.bluetooth = Bluetooth(name, base_color, shade_color)
        self.network = self.bluetooth.network
        self.bluetooth.enable()
        self.touch = Touch(pin=config["touch"]["pin"])
        self.debug = config["lamp"]["debug"]

        if config["lamp"]["default_behaviours"] is True:
            self.add_behaviour(LampFadeIn(self, frames=30, chained_behaviors = [LampIdle]))
            self.add_behaviour(LampIdle(self, frames=1))

        # pylint: disable=no-member
        if self.debug is True:
            print("StandardLamp Started allocating {} bytes".format(gc.mem_alloc()))
        gc.collect()
