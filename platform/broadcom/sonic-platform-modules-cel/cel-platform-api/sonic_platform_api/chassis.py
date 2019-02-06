#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the Chassis information which are available in the platform
#
#############################################################################

import sys

try:
    from sonic_platform_base.chassis_base import ChassisBase
    from sonic_platform_api.psu import Psu
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

NUM_PSU = 2

class Chassis(ChassisBase):
    """Platform-specific Chassis class"""
    def __init__(self):
        ChassisBase.__init__(self)
        self._psu_list.append(None)
        for index in range(1, NUM_PSU + 1):
            psu = Psu(index)
            self._psu_list.append(psu)

    def get_num_psus(self):
        """
        Retrieves the number of power supply units available on this chassis

        Returns:
            An integer, the number of power supply units available on this
            chassis
        """
        return NUM_PSU

    def get_psu(self, index):
        """
        Retrieves power supply unit represented by (0-based) index <index>

        Args:
            index: An integer, the index (0-based) of the power supply unit to
            retrieve

        Returns:
            An object derived from PsuBase representing the specified power
            supply unit
        """
        psu = None
        try:
            psu = self._psu_list[index]
        except IndexError:
            sys.stderr.write("PSU index {} out of range (1-{})\n".format(
                             index, len(self._psu_list)))
        return psu

