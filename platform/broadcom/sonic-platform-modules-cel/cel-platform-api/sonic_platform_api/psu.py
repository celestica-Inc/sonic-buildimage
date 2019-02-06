#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the PSUs status which are available in the platform
#
#############################################################################

import os.path
import sonic_platform

try:
    from sonic_platform_base.psu_base import PsuBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

psu_list = []


class Psu(PsuBase):
    """Platform-specific Psu class"""

    def __init__(self, psu_index):
        global psu_list
        PsuBase.__init__(self)
        self.index = psu_index
        psu_list.append(psu_index)
        self.platform = self.get_platform()
        self.dx010_psu_gpio = [
            {'base': self.get_gpio_base()},
            {'abs': 27, 'power': 22},
            {'abs': 28, 'power': 25}
        ]
        self.psu_e1031_path = "/sys/devices/platform/e1031.smc/"
        self.psu_e1031_presence = "psu{}_prs"
        self.psu_e1031_oper_status = "psu{}_status"

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

    def read_psu_statuses(self, pinnum):
        sys_gpio_dir = "/sys/class/gpio"
        gpio_base = self.dx010_psu_gpio[0]['base']

        gpio_dir = sys_gpio_dir + '/gpio' + str(gpio_base+pinnum)
        gpio_file = gpio_dir + "/value"

        try:
            with open(gpio_file, 'r') as fd:
                retval = fd.read()
        except IOError:
            raise IOError("Unable to open " + gpio_file + "file !")

        retval = retval.rstrip('\r\n')
        return retval

    def get_status(self):
        """
        Retrieves the operational status of power supply unit (PSU) defined

        Returns:
            bool: True if PSU is operating properly, False if not
        """
        psu_status = 0

        if self.platform == "x86_64-cel_seastone-r0":
            psu_status = self.read_psu_statuses(
                self.dx010_psu_gpio[self.index]['power'])
            psu_status = int(psu_status, 10)

        elif self.platform == "x86_64-cel_e1031-r0":
            psu_location = ["R", "L"]
            try:
                with open(self.psu_e1031_path + self.psu_e1031_oper_status.format(psu_location[self.index - 1]), 'r') as power_status:
                    psu_status = int(power_status.read())
            except IOError:
                return False

        return psu_status == 1

    def get_presence(self):
        """
        Retrieves the presence status of power supply unit (PSU) defined

        Returns:
            bool: True if PSU is present, False if not
        """
        psu_presence = 1

        if self.platform == "x86_64-cel_seastone-r0":

            psu_presence = self.read_psu_statuses(
                self.dx010_psu_gpio[self.index]['abs'])
            psu_presence = (int(psu_presence, 10))

        elif self.platform == "x86_64-cel_e1031-r0":
            psu_location = ["R", "L"]
            try:
                with open(self.psu_e1031_path + self.psu_e1031_presence.format(psu_location[self.index - 1]), 'r') as psu_prs:
                    psu_presence = int(psu_prs.read())
            except IOError:
                return False

        return psu_presence == 0
