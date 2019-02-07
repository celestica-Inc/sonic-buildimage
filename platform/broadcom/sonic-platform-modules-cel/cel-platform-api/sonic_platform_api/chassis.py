#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Chassis information which are available in the platform
#
#############################################################################

import sys
import re
import os
import subprocess

try:
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform_api.psu import Psu
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NUM_PSU = 2


class Chassis(ChassisBase):
    """Platform-specific Chassis class"""

    def __init__(self):
        ChassisBase.__init__(self)
        self._psu_list.append(None)
        for index in range(0, NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)

    # def reboot_cause_selector(self, cause):
    
    #     return {
    #         "power_loss": "REBOOT_CAUSE_POWER_LOSS,
    #         "thermal_overload_cpu": "REBOOT_CAUSE_THERMAL_OVERLOAD_CPU",
    #         "thermal_overload_asic": "REBOOT_CAUSE_THERMAL_OVERLOAD_ASIC",
    #         "thermal_overload_other": "REBOOT_CAUSE_THERMAL_OVERLOAD_OTHER",
    #         "insufficient_fan": "REBOOT_CAUSE_INSUFFICIENT_FAN",
    #         "watchdog", "REBOOT_CAUSE_WATCHDOG",
    #         "hardware_other", "REBOOT_CAUSE_HARDWARE_OTHER",
    #         "non_hardware", "REBOOT_CAUSE_NON_HARDWARE"
    #     }.get(cause, "REBOOT_CAUSE_NON_HARDWARE")

    def get_base_mac(self):
        """
        Retrieves the base MAC address for the chassis
        Returns:
            A string containing the MAC address in the format
            'XX:XX:XX:XX:XX:XX'
        """
        command = 'show platform syseeprom | grep "Base MAC Address"'
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data, err = p.communicate()
        if err != "":
            return None
        p = re.compile(ur'(?:[0-9a-fA-F]:?){12}')
        find_mac = re.findall(p, raw_data)
        base_mac = find_mac[0] if len(find_mac) > 0 else None

        return str(base_mac)

    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot
        Returns:
            A tuple (string, string) where the first element is a string
            containing the cause of the previous reboot. This string must be
            one of the predefined strings in this class. If the first string
            is "REBOOT_CAUSE_HARDWARE_OTHER", the second string can be used
            to pass a description of the reboot cause.
        """
        PREVIOUS_REBOOT_CAUSE_FILE = "/var/cache/sonic/previous-reboot-cause.txt"

        if not os.path.isfile(PREVIOUS_REBOOT_CAUSE_FILE):
            prev_reboot_cause = "Unable to determine cause of previous reboot\n"
        else:
            with open(PREVIOUS_REBOOT_CAUSE_FILE, 'r') as prev_reboot_file:
                prev_reboot_cause = prev_reboot_file.read()

        return (prev_reboot_cause , None)

    def get_num_psus(self):
        """
        Retrieves the number of power supply units available on this chassis

        Returns:
            An integer, the number of power supply units available on this
            chassis
        """
        return NUM_PSU
