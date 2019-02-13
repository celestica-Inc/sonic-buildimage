#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the fan status which are available in the platform
#
#############################################################################

import os.path
import sonic_platform

try:
    from sonic_platform_base.fan_base import FanBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_index):
        FanBase.__init__(self)
        self.index = fan_index
        self.platform = self.get_platform()

        self.fan_speed = 0

        self.fan_emc2305_path = "/sys/bus/i2c/drivers/emc2305/"
        self.fan_em2305_max_rpm = 16000
        self.fan_emc2305_pwm = "pwm{}"
        self.fan_emc2305_target = "fan{}_target"
        self.fan_emc2305_input = "fan{}_input"

        # dx010 fan attributes
        # Two EMC2305s located at i2c-13-4d and i2c-13-2e
        # to control a dual-fan module.
        self.dx010_emc2305_chip = [
            {
                'device': "13-002e",
                'index_map': [2, 1, 4, 5, 3]
            },
            {
                'device': "13-004d",
                'index_map': [2, 4, 5, 3, 1]
            }
        ]

        self.dx010_fan_gpio = [
            {'base': self.get_gpio_base()},
            {'prs': 10, 'dir': 15, 'color': {'red': 31, 'green': 32}},
            {'prs': 11, 'dir': 16, 'color': {'red': 29, 'green': 30}},
            {'prs': 12, 'dir': 17, 'color': {'red': 35, 'green': 36}},
            {'prs': 13, 'dir': 18, 'color': {'red': 37, 'green': 38}},
            {'prs': 14, 'dir': 19, 'color': {'red': 33, 'green': 34}},
        ]

        # e1031 fan attributes
        # Single emc2305 chip located at i2c-23-4d
        # to control a fan module
        self.e1031_emc2305_chip = [
            {
                'device': "23-004d",
                'index_map': [1, 2, 4]
            }
        ]
        self.fan_e1031_path = "/sys/devices/platform/e1031.smc/"
        # TODO: Add fan presence status in sysfs
        self.fan_e1031_presence = "fan{}_prs"
        self.fan_e1031_direction = "fan{}_dir"
        self.fan_e1031_led = "fan{}_led"
        self.fan_e1031_led_col_map = {
            self.STATUS_LED_COLOR_GREEN: "green",
            self.STATUS_LED_COLOR_RED: "amber",
            self.STATUS_LED_COLOR_OFF: "off"
        }

    def get_platform(self):
        machine_info = sonic_platform.get_machine_info()
        platform = sonic_platform.get_platform_info(machine_info)
        return platform

    def get_gpio_base(self):
        sys_gpio_dir = "/sys/class/gpio"
        for r in os.listdir(sys_gpio_dir):
            if "gpiochip" in r:
                return int(r[8:], 10)
        return 216  # Reserve

    def get_gpio_value(self, pinnum):
        sys_gpio_dir = "/sys/class/gpio"
        gpio_base = self.dx010_fan_gpio[0]['base']

        gpio_dir = sys_gpio_dir + '/gpio' + str(gpio_base+pinnum)
        gpio_file = gpio_dir + "/value"

        try:
            with open(gpio_file, 'r') as fd:
                retval = fd.read()
        except IOError:
            raise IOError("Unable to open " + gpio_file + "file !")

        retval = retval.rstrip('\r\n')
        return retval

    def set_gpio_value(self, pinnum, value=0):
        sys_gpio_dir = "/sys/class/gpio"
        gpio_base = self.dx010_fan_gpio[0]['base']

        gpio_dir = sys_gpio_dir + '/gpio' + str(gpio_base+pinnum)
        gpio_file = gpio_dir + "/value"

        try:
            with open(gpio_file, 'w') as fd:
                retval = fd.write(str(value))
        except IOError:
            raise IOError("Unable to open " + gpio_file + "file !")

    def get_direction(self):

        direction = self.FAN_DIRECTION_INTAKE

        if self.platform == "x86_64-cel_seastone-r0":
            raw = self.get_gpio_value(self.dx010_fan_gpio[self.index+1]['dir'])
            if int(raw, 10) == 0:
                direction = self.FAN_DIRECTION_INTAKE
            else:
                direction = self.FAN_DIRECTION_EXHAUST

        elif self.platform == "x86_64-cel_e1031-r0":
            try:
                fan_direction_file = (self.fan_e1031_path + 
                    self.fan_e1031_direction.format(self.index+1))
                with open(fan_direction_file, 'r') as file:
                    raw = file.read().strip('\r\n')
                if int(raw, 10) == 0:
                    direction = self.FAN_DIRECTION_INTAKE
                else:
                    direction = self.FAN_DIRECTION_EXHAUST
            except IOError:
                return False

        return direction

    def get_speed(self):
        """
        DX010 and E1031 platform specific data:
            MAX TACH is 16000 rpm from EMC2305 chip.

            speed_pc = rpm_in/16000*100
        """
        # TODO: Seperate PSU's fan and main fan class
        if self.fan_speed != 0:
            return self.fan_speed
        else:
            speed = 0
            rpm = []
            emc2305_chips = {}

            if self.platform == "x86_64-cel_seastone-r0":
                emc2305_chips = self.dx010_emc2305_chip
            elif self.platform == "x86_64-cel_e1031-r0":
                emc2305_chips = self.e1031_emc2305_chip
            else:
                return target

            for chip in emc2305_chips:
                device = chip['device']
                fan_index = chip['index_map']
                sysfs_path = "%s%s/%s" % (
                    self.fan_emc2305_path, device, self.fan_emc2305_input)
                sysfs_path = sysfs_path.format(fan_index[self.index])
                try:
                    with open(sysfs_path, 'r') as file:
                        raw = file.read().strip('\r\n')
                        rpm.append(int(raw, 10))
                except IOError:
                    raise IOError("Unable to open " + sysfs_path)

                speed = rpm[0] * 100 / self.fan_em2305_max_rpm

            return speed

    def get_target_speed(self):
        """
        DX010 and E1031 platform specific data:
            MAX TACH is 16000 rpm from EMC2305 chip.

            speed_pc = rpm_target/16000*100

            0   : when PWM mode is use
            rpm : when pwm mode is not use

        """
        target = 0
        rpm = []
        emc2305_chips = {}

        if self.platform == "x86_64-cel_seastone-r0":
            emc2305_chips = self.dx010_emc2305_chip
        elif self.platform == "x86_64-cel_e1031-r0":
            emc2305_chips = self.e1031_emc2305_chip
        else:
            return target

        for chip in emc2305_chips:
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                self.fan_emc2305_path, device, self.fan_emc2305_target)
            sysfs_path = sysfs_path.format(fan_index[self.index])
            try:
                with open(sysfs_path, 'r') as file:
                    raw = file.read().strip('\r\n')
                    rpm.append(int(raw, 10))
            except IOError:
                raise IOError("Unable to open " + sysfs_path)

            target = rpm[0] * 100 / self.fan_em2305_max_rpm

        return target

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan
        Returns:
            An integer, the percentage of variance from target speed which is
                 considered tolerable
        """
        raise NotImplementedError

    def set_speed(self, speed):
        """
        Depends on pwm or target mode is selected:
            1) pwm = speed_pc * 255             <-- Currently use this mode.
            2) target_rpm = speed_pc * 100 / 16000
             2.1) set pwm{}_enable to 3

        """
        pwm = speed * 255 / 100
        emc2305_chips = {}

        if self.platform == "x86_64-cel_seastone-r0":
            emc2305_chips = self.dx010_emc2305_chip
        elif self.platform == "x86_64-cel_e1031-r0":
            emc2305_chips = self.e1031_emc2305_chip
        else:
            return False

        for chip in emc2305_chips:
            device = chip['device']
            fan_index = chip['index_map']
            sysfs_path = "%s%s/%s" % (
                self.fan_emc2305_path, device, self.fan_emc2305_pwm)
            sysfs_path = sysfs_path.format(fan_index[self.index])
            try:
                with open(sysfs_path, 'w') as file:
                    file.write(str(round(pwm)))
            except IOError:
                return False

        return True

    def set_status_led(self, color):

        if self.platform == "x86_64-cel_seastone-r0":
            try:
                if color == self.STATUS_LED_COLOR_GREEN:
                    self.set_gpio_value(
                        self.dx010_fan_gpio[self.index+1]['color']['red'], 1)
                    self.set_gpio_value(
                        self.dx010_fan_gpio[self.index+1]['color']['green'], 0)

                elif color == self.STATUS_LED_COLOR_RED:
                    self.set_gpio_value(
                        self.dx010_fan_gpio[self.index+1]['color']['red'], 0)
                    self.set_gpio_value(
                        self.dx010_fan_gpio[self.index+1]['color']['green'], 1)

                elif color == self.STATUS_LED_COLOR_OFF:
                    self.set_gpio_value(
                        self.dx010_fan_gpio[self.index+1]['color']['red'], 1)
                    self.set_gpio_value(
                        self.dx010_fan_gpio[self.index+1]['color']['green'], 1)
                else:
                    return False

            except IOError:
                return False

        elif self.platform == "x86_64-cel_e1031-r0":
            try:
                fan_led_file = (self.fan_e1031_path +
                    self.fan_e1031_led.format(self.index+1))
                with open(fan_led_file, 'r') as file:
                    file.write(self.fan_e1031_led_col_map[color])
            except IOError:
                return False

        return True
