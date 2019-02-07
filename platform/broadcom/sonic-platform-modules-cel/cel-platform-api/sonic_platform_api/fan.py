#!/usr/bin/env python

try:
    from sonic_platform_base.fan_base import FanBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_index):
        FanBase.__init__(self)
        self.index = fan_index
        self.fan_speed = 0

    def get_speed(self):
        """
        Retrieves the speed of fan as a percentage of full speed
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)
        """
        if self.fan_speed != 0:
            return self.fan_speed
        else:
            # TODO
            
            return 0
