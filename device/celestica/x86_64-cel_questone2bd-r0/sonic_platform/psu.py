#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the PSUs status which are available in the platform
#
#############################################################################

try:
    import os
    import re
    import math
    from sonic_platform_base.psu_base import PsuBase
    from sonic_platform.eeprom import Eeprom
    from sonic_platform.fan import Fan
    from helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

PSU_NUM_FAN = [1, 1]

PRESENT_BIT = '0'
POWER_OK_BIT = '1'
PSU_INFO_MAPPING = {
    0: {
        "name": "PSU-1",
        "status": 0,
        "present": 2,
        "i2c_num": 75,
        "pmbus_reg": "58",
        "eeprom_reg": "50"
    },
    1: {
        "name": "PSU-2",
        "status": 1,
        "present": 3,
        "i2c_num": 76,
        "pmbus_reg": "59",
        "eeprom_reg": "51",
    },
}
PSU_STATUS_REGISTER = "0xA160"
HWMON_PATH = "/sys/bus/i2c/devices/i2c-{0}/{0}-00{1}/hwmon"
PSU_POWER_DIVIDER = 1000000
PSU_VOLT_DIVIDER = 1000
PSU_CUR_DIVIDER = 1000

PSU_MUX_HWMON_PATH = "/sys/bus/i2c/devices/i2c-68/i2c-{0}/{0}-00{1}/"


class Psu(PsuBase):
    """Platform-specific Psu class"""

    def __init__(self, psu_index):
        PsuBase.__init__(self)
        self.index = psu_index
        for fan_index in range(0, PSU_NUM_FAN[self.index]):
            fan = Fan(fan_index, 0, is_psu_fan=True, psu_index=self.index)
            self._fan_list.append(fan)
        self.hwmon_path = HWMON_PATH.format(
            PSU_INFO_MAPPING[self.index]["i2c_num"], PSU_INFO_MAPPING[self.index]["pmbus_reg"])
        self._api_helper = APIHelper()

    def __search_file_by_contain(self, directory, search_str, file_start):
        for dirpath, dirnames, files in os.walk(directory):
            for name in files:
                file_path = os.path.join(dirpath, name)
                if name.startswith(file_start) and search_str in self._api_helper.read_txt_file(file_path):
                    return file_path
        return None

    def __get_psu_status(self):
        psu_status_raw = self._api_helper.get_register_value(
            PSU_STATUS_REGISTER)
        psu_status_bin = self._api_helper.hex_to_bin(psu_status_raw)
        return str(psu_status_bin)[2:][::-1]

    def __read_eeprom_sysfs(self,sys_path,sysfs_file):
        sysfs_path = os.path.join(sys_path, sysfs_file)
        try:
            with open(sysfs_path, 'rb') as fd:
                data = fd.read()
                return data
        except IOError:
            raise IOError("Unable to open %s file !" % sysfs_path)
        return False

    def __fru_decode_product_serial(self, data):
        if data[4] != 00:
            start_product_info = ord(data[4]) * 8
            start_format_version = start_product_info
            start_product_info = start_format_version + 1
            start_product_Lang_code = start_product_info + 1
            start_product_Manu_name = start_product_Lang_code + 1
            start_product_Manu_name_length = ord(data[start_product_Manu_name]) & 0x0F
            start_product_name =  start_product_Manu_name + start_product_Manu_name_length + 1
            start_product_name_length = ord(data[start_product_name]) & 0x0F
            start_product_module_number = start_product_name + start_product_name_length +1
            start_product_module_number_length = ord(data[start_product_module_number]) & 0x0F
            start_product_version = start_product_module_number + start_product_module_number_length +1
            start_product_version_length = ord(data[start_product_version]) & 0x0F
            start_product_serial_number = start_product_version + start_product_version_length +1
            start_product_serial_number_length = ord(data[start_product_serial_number]) & 0x1F
            return data[start_product_serial_number+1:start_product_serial_number+start_product_serial_number_length+1]
        else:
            return None

    def __fru_decode_product_model(self, data):
        if data[4] != 00:
            start_product_info = ord(data[4]) * 8
            start_format_version = start_product_info
            start_product_info = start_format_version + 1
            start_product_Lang_code = start_product_info + 1
            start_product_Manu_name = start_product_Lang_code + 1
            start_product_Manu_name_length = ord(data[start_product_Manu_name]) & 0x0F
            start_product_name =  start_product_Manu_name + start_product_Manu_name_length + 1
            start_product_name_length = ord(data[start_product_name]) & 0x0F
            start_product_module_number = start_product_name + start_product_name_length +1
            start_product_module_number_length = ord(data[start_product_module_number]) & 0x0F
            start_product_version = start_product_module_number + start_product_module_number_length +1
            start_product_version_length = ord(data[start_product_version]) & 0x0F
            start_product_serial_number = start_product_version + start_product_version_length +1
            start_product_serial_number_length = ord(data[start_product_serial_number]) & 0x1F
            return data[start_product_module_number+1:start_product_module_number+start_product_module_number_length+1]
        else:
            return None

    def get_voltage(self):
        """
        Retrieves current PSU voltage output
        Returns:
            A float number, the output voltage in volts,
            e.g. 12.1
        """
        psu_voltage = 0.0
        voltage_name = "in{}_input"
        voltage_label = "vout1"

        vout_label_path = self.__search_file_by_contain(
            self.hwmon_path, voltage_label, "in")
        if vout_label_path:
            dir_name = os.path.dirname(vout_label_path)
            basename = os.path.basename(vout_label_path)
            in_num = filter(str.isdigit, basename)
            vout_path = os.path.join(
                dir_name, voltage_name.format(in_num))
            vout_val = self._api_helper.read_txt_file(vout_path)
            psu_voltage = float(vout_val) / PSU_VOLT_DIVIDER

        return psu_voltage

    def get_current(self):
        """
        Retrieves present electric current supplied by PSU
        Returns:
            A float number, the electric current in amperes, e.g 15.4
        """
        psu_current = 0.0
        current_name = "curr{}_input"
        current_label = "iout1"

        curr_label_path = self.__search_file_by_contain(
            self.hwmon_path, current_label, "cur")
        if curr_label_path:
            dir_name = os.path.dirname(curr_label_path)
            basename = os.path.basename(curr_label_path)
            cur_num = filter(str.isdigit, basename)
            cur_path = os.path.join(
                dir_name, current_name.format(cur_num))
            cur_val = self._api_helper.read_txt_file(cur_path)
            psu_current = float(cur_val) / PSU_CUR_DIVIDER

        return psu_current

    def get_power(self):
        """
        Retrieves current energy supplied by PSU
        Returns:
            A float number, the power in watts, e.g. 302.6
        """
        psu_power = 0.0
        power_name = "power{}_input"
        power_label = "pout1"

        pw_label_path = self.__search_file_by_contain(
            self.hwmon_path, power_label, "power")
        if pw_label_path:
            dir_name = os.path.dirname(pw_label_path)
            basename = os.path.basename(pw_label_path)
            pw_num = filter(str.isdigit, basename)
            pw_path = os.path.join(
                dir_name, power_name.format(pw_num))
            pw_val = self._api_helper.read_txt_file(pw_path)
            psu_power = float(pw_val) / PSU_POWER_DIVIDER

        return psu_power

    def get_powergood_status(self):
        """
        Retrieves the powergood status of PSU
        Returns:
            A boolean, True if PSU has stablized its output voltages and passed all
            its internal self-tests, False if not.
        """
        return self.get_status()

    def set_status_led(self, color):
        """
        Sets the state of the PSU status LED
        Args:
            color: A string representing the color with which to set the PSU status LED
                   Note: Only support green and off
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        # NOT ALLOW

        return False

    def get_status_led(self):
        """
        Gets the state of the PSU status LED
        Returns:
            A string, one of the predefined STATUS_LED_COLOR_* strings above
        """
        return self.STATUS_LED_COLOR_OFF

    ##############################################
    # Device methods
    ##############################################

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        return PSU_INFO_MAPPING[self.index]["name"]

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        psu_stat_raw = self.__get_psu_status()
        psu_presence = psu_stat_raw[PSU_INFO_MAPPING[self.index]["present"]]

        return psu_presence == PRESENT_BIT

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        temp_file = PSU_MUX_HWMON_PATH.format( ((self.index) + 75), self.index+50 )
        return self.__fru_decode_product_model(self.__read_eeprom_sysfs(temp_file, "eeprom"))

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        temp_file = PSU_MUX_HWMON_PATH.format( ((self.index) + 75), self.index+50  )
        return self.__fru_decode_product_serial(self.__read_eeprom_sysfs(temp_file, "eeprom"))

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        psu_stat_raw = self.__get_psu_status()
        psu_status = psu_stat_raw[PSU_INFO_MAPPING[self.index]["status"]]

        return psu_status == POWER_OK_BIT
