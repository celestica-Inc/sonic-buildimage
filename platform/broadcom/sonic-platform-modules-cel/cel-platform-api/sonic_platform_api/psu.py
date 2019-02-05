#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the PSUs status which are available in the platform
#
#############################################################################

import os.path

try:
    from sonic_platform_base.psu_base import PsuBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

psu_list = []

class Psu(PsuBase):
    """Platform-specific Psu class"""
    def __init__(self, psu_index):
        global psu_list
        PsuBase.__init__(self)
        self.index = psu_index
        psu_list.append(psu_index)
        self.psu_path = "/var/run/hw-management/thermal/"
        self.psu_oper_status = "psu{}_pwr_status".format(self.index)
        self.psu_presence = "psu{}_status".format(self.index)
        if os.path.exists(self.psu_path + self.psu_presence):
            self.presence_file_exists = True
        else:
            self.presence_file_exists = False

    def get_status(self):
        """
        Retrieves the operational status of power supply unit (PSU) defined

        Returns:
            bool: True if PSU is operating properly, False if not
        """
        status = 0
        try:
            with open(self.psu_path + self.psu_oper_status, 'r') as power_status:
                status = int(power_status.read())
        except IOError:
            return False

        return status == 1

    def get_presence(self):
        """
        Retrieves the presence status of power supply unit (PSU) defined

        Returns:
            bool: True if PSU is present, False if not
        """
        status = 0
        if self.presence_file_exists:
            try:
                with open(self.psu_path + self.psu_presence, 'r') as presence_status:
                    status = int(presence_status.read())
            except IOError:
                return False
            status = 1
        else:
            status = self.index in psu_list
        return status

