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
import sonic_platform

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
        for index in range(0, NUM_PSU):
            psu = Psu(index)
            self._psu_list.append(psu)
        self.platform = self.get_platform()
        self.bios_version_path = "/sys/class/dmi/id/bios_version"
        self.smc_cpld_e1031_path = "/sys/devices/platform/e1031.smc/version"
        self.mmc_cpld_e1031_path = "/sys/devices/platform/e1031.smc/getreg"
        self.cpld_dx010_path = "/sys/devices/platform/dx010_cpld/getreg"

    def __get_register_value(self, path, register):
        cmd = "echo {1} > {0}; cat {0}".format(path, register)
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data, err = p.communicate()
        if err is not '':
            return 'None'
        else:
            return raw_data.strip()

    def get_platform(self):
        machine_info = sonic_platform.get_machine_info()
        platform = sonic_platform.get_platform_info(machine_info)
        return platform

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

    def get_component_versions(self):
        """
        Retrieves platform-specific hardware/firmware versions for chassis
        componenets such as BIOS, CPLD, FPGA, etc.
        Returns:
            A string containing platform-specific component versions
        """

        component_versions = dict()

        # Get BIOS version
        try:
            with open(self.bios_version_path, 'r') as fd:
                bios_version = fd.read()
        except IOError:
            raise IOError("Unable to open version file !")

        # Get CPLD version
        if self.platform == "x86_64-cel_seastone-r0":

            CPLD_1 = self.__get_register_value(self.cpld_dx010_path, '0x100')
            CPLD_2 = self.__get_register_value(self.cpld_dx010_path, '0x200')
            CPLD_3 = self.__get_register_value(self.cpld_dx010_path, '0x280')
            CPLD_4 = self.__get_register_value(self.cpld_dx010_path, '0x300')
            CPLD_5 = self.__get_register_value(self.cpld_dx010_path, '0x380')

            CPLD_1 = 'None' if CPLD_1 is 'None' else "{}.{}".format(
                int(CPLD_1[2], 16), int(CPLD_1[3], 16))
            CPLD_2 = 'None' if CPLD_2 is 'None' else "{}.{}".format(
                int(CPLD_2[2], 16), int(CPLD_2[3], 16))
            CPLD_3 = 'None' if CPLD_3 is 'None' else "{}.{}".format(
                int(CPLD_3[2], 16), int(CPLD_3[3], 16))
            CPLD_4 = 'None' if CPLD_4 is 'None' else "{}.{}".format(
                int(CPLD_4[2], 16), int(CPLD_4[3], 16))
            CPLD_5 = 'None' if CPLD_5 is 'None' else "{}.{}".format(
                int(CPLD_5[2], 16), int(CPLD_5[3], 16))

            cpld_version = dict()
            cpld_version["CPLD1"] = CPLD_1
            cpld_version["CPLD2"] = CPLD_2
            cpld_version["CPLD3"] = CPLD_3
            cpld_version["CPLD4"] = CPLD_4
            cpld_version["CPLD5"] = CPLD_5
            component_versions["CPLD"] = cpld_version

        elif self.platform == "x86_64-cel_e1031-r0":
            cpld_version = dict()

            with open(self.smc_cpld_e1031_path, 'r') as fd:
                smc_cpld_version = fd.read()
            smc_cpld_version = 'None' if smc_cpld_version is 'None' else "{}.{}".format(
                int(smc_cpld_version[2], 16), int(smc_cpld_version[3], 16))

            mmc_cpld_version = self.__get_register_value(
                self.mmc_cpld_e1031_path, '0x100')
            mmc_cpld_version = 'None' if mmc_cpld_version is 'None' else "{}.{}".format(
                int(mmc_cpld_version[2], 16), int(mmc_cpld_version[3], 16))

            cpld_version["SMC"] = smc_cpld_version
            cpld_version["MMC"] = mmc_cpld_version

            component_versions["CPLD"] = cpld_version

        component_versions["BIOS"] = bios_version.strip()
        return str(component_versions)

    def get_num_psus(self):
        """
        Retrieves the number of power supply units available on this chassis

        Returns:
            An integer, the number of power supply units available on this
            chassis
        """
        return NUM_PSU
