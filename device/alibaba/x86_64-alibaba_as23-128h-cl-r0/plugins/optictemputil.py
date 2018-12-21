#!/usr/bin/env python

#
#  optictemputil.py
#
#  Platform-specific Optic module temperature Interface for SONiC
#

__author__ = 'Pradchaya P.<pphuchar@celestica.com>'
__author__ = 'Wirut G.<wgetbumr@celestica.com>'
__license__ = "GPL"
__version__ = "0.2.0"
__status__  = "Development"

import os
import sys
import binascii
import subprocess

class OpticTempUtil():
    """Platform-specific OpticTempUtil class"""

    def __init__(self):
        pass

    def read_eeprom_specific_bytes(self, bus_num, dev_addr, offset, num_bytes):
        eeprom_raw = []
        for i in range(0, num_bytes):
            eeprom_raw.append(0x00)

        try:
            for i in range(0, num_bytes):
                p = subprocess.Popen(['i2cget', '-f', '-y', str(bus_num), str(dev_addr), str(offset+i)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                raw, err = p.communicate()
                if p.returncode != 0 or err != '':
                    raise IOError
                eeprom_raw[i] = raw.strip()
        except IOError:
            return None

        return eeprom_raw


    def twos_comp(self, num, bits):
        try:
            if ((num & (1 << (bits - 1))) != 0):
                num = num - (1 << bits)
            return num
        except:
            return 0


    def calc_temperature(self, cal_type, tad_data, tslope_data, toff_data, offset ):

        msb = int(tad_data[offset], 16)
        lsb = int(tad_data[offset + 1], 16)

        Tad = (msb << 8) | (lsb & 0xff)
        Tad = self.twos_comp(Tad, 16)

        if cal_type == 1:
        # Internal calibration
            result = float(result / 256.0)
            retval = '%.4f' %result

        # Eexternal calibration
        # float = Tslope * two_comp(Tad) + two_comp(Toffset)
        # float = twos(Tad)*Tslope[msb] + ( twos(Tad)*Tslope[lsb] + twos(Toffset) )/256
        elif cal_type == 2:
            Toff_msb = int(toff_data[offset], 16)
            Toff_lsb = int(toff_data[offset + 1], 16)
            Toff = (msb << 8) | (lsb & 0xff)
            Toff = self.twos_comp(Toff, 16)

            Tslope_msb = int(toff_data[offset], 16)
            Tslope_lsb = int(toff_data[offset + 1], 16)

            result = Tad*Tslope_msb
            result = result + float( (Toff*Tslope_lsb + Toff)/256.0 )

            retval = '%.4f' %result
        else:
            retval = '0.0'

        return retval

    def get_optic_temp(self, bus_num, port_type):

        EEPROM_ADDR = 0x50
        DOM_ADDR = 0x51
        EEPROM_OFFSET = 0
        DOM_OFFSET = 0

        SFP_DMT_ADDR = 92
        SFP_DMT_WIDTH = 1

        SFP_Ts_DATA_ADDR = 84
        SFP_Ts_DATA_WIDTH = 2

        SFP_To_DATA_ADDR = 86
        SFP_To_DATA_WIDTH = 2

        SFP_TEMP_DATA_ADDR = 96
        SFP_TEMP_DATA_WIDTH = 2

        QSFP_TEMP_DATA_ADDR = 22
        QSFP_TEMP_DATA_WIDTH = 2       
        temperature_raw = None

        if port_type == 'QSFP':

            # QSFP only have internal calibration mode.
            cal_type = 1
            # read temperature raw value
            temperature_raw = self.read_eeprom_specific_bytes(bus_num,EEPROM_ADDR,(EEPROM_OFFSET+QSFP_TEMP_DATA_ADDR),QSFP_TEMP_DATA_WIDTH)
        else:
            # read calibration type at bit 4-6
            cal_type = self.read_eeprom_specific_bytes(bus_num,EEPROM_ADDR,EEPROM_OFFSET+SFP_DMT_ADDR,SFP_DMT_WIDTH)
            if cal_type is None:
                return 0
            else:
                cal_type = (int(cal_type[0],16) >> 4 ) & 0x7
                if cal_type == 5:
                    cal_type = 2
                    # read calibration parameter
                    slope_raw = self.read_eeprom_specific_bytes(bus_num,DOM_ADDR,(DOM_OFFSET+SFP_Ts_DATA_ADDR),SFP_TEMP_DATA_WIDTH)
                    offset_raw = self.read_eeprom_specific_bytes(bus_num,DOM_ADDR,(DOM_OFFSET+SFP_To_DATA_ADDR),SFP_TEMP_DATA_WIDTH)
                    # read temperature raw value
                    temperature_raw = self.read_eeprom_specific_bytes(bus_num,DOM_ADDR,(DOM_OFFSET+SFP_TEMP_DATA_ADDR),SFP_TEMP_DATA_WIDTH)
                elif cal_type == 6:
                    cal_type = 1
                    # read temperature raw value
                    temperature_raw = self.read_eeprom_specific_bytes(bus_num,DOM_ADDR,(DOM_OFFSET+SFP_TEMP_DATA_ADDR),SFP_TEMP_DATA_WIDTH)
                else:
                    return 0

        #calculate temperature
        if temperature_raw is not None:
            return self.calc_temperature(cal_type, temperature_raw, slope_raw, offset_raw, 0)
        else:
            return 0

