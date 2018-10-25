#!/usr/bin/env python

import requests

try:
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    def __init__(self):
        PsuBase.__init__(self)
        self.fru_status_url = "http://[fe80::1:1%eth0.4088]:8080/api/sys/fruid/status"
        self.psu_info_url = "http://[fe80::1:1%eth0.4088]:8080/api/sys/fruid/psu"
        
        self.fru_status_list = None
        self.psu_info_list = None


    def request_data(self):
        # Reqest data from BMC if not exist.
        if self.fru_status_list is None or self.psu_info_list is None:
            fru_status_req = requests.get(self.fru_status_url)
            psu_info_req = requests.get(self.psu_info_url)
            fru_status_json = fru_status_req.json()
            psu_info_json = psu_info_req.json()
            self.fru_status_list = fru_status_json.get('Information')
            self.psu_info_list = psu_info_json.get('Information')
        return self.fru_status_list, self.psu_info_list


    def get_num_psus(self):
        """
        Retrieves the number of PSUs available on the device
        :return: An integer, the number of PSUs available on the device
        """

        num_psus = 2

        try:
            # Request and validate sensor's information
            self.fru_status_list, self.psu_info_list = self.request_data()
            num_psus = len(self.psu_info_list)
        except:
            return num_psus

        return num_psus

    def get_psu_status(self, index):
        """
        Retrieves the oprational status of power supply unit (PSU) defined
                by 1-based index <index>
        :param index: An integer, 1-based index of the PSU of which to query status
        :return: Boolean, True if PSU is operating properly, False if PSU is faulty
        """
        
        # init data
        psu_key = "PSU" + str(index)
        psu_status_key = "Power Status"
        psu_power_status = False

        try:
            # Request and validate sensor's information
            self.fru_status_list, self.psu_info_list = self.request_data()

            # Get PSU power status.
            for fru_status in self.fru_status_list:            
                is_psu = fru_status.get(psu_key)
                psu_status  = str(fru_status.get(psu_status_key)).strip()

                if is_psu is not None and psu_status == "OK":
                    psu_power_status = True

        except:
            print("Error: Unable to access PSU power status")
            return False

        return psu_power_status

    def get_psu_presence(self, index):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by 1-based index <index>
        :param index: An integer, 1-based index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """

        # Init data
        psu_key = "PSU" + str(index)
        psu_presence_key = "Present"
        psu_presence_status = False

        try:
            # Request and validate sensor's information.
            self.fru_status_list, self.psu_info_list = self.request_data()

            # Get PSU present status.
            for fru_status in self.fru_status_list:            
                is_psu = fru_status.get(psu_key)
                psu_status  = str(fru_status.get(psu_presence_key)).strip()

                if is_psu is not None and psu_status == "Present":
                    psu_presence_status = True

        except:
            print("Error: Unable to access PSU presence status")
            return False

        return psu_presence_status

    def get_psu_sn(self, index):
        """
        Get the serial number of the psu,
        
        :param index: An integer, 1-based index of the PSU.
        :return: Serial number
        """
        serial_number = "N/A"
        psu_key = "PSU" + str(index) + " FRU"
        psu_sn_key = "Serial Number"
      
        try:
            # Request and validate sensor's information.
            self.fru_status_list, self.psu_info_list = self.request_data()

            # Get PSU fru info.
            for psu_fru in self.psu_info_list:            
                psu_sn  = str(psu_fru.get(psu_sn_key)).strip()
                if psu_fru.get(psu_key) is not None:
                    serial_number = psu_sn if psu_sn.strip() != "" else "N/A"
                    break

        except:
            return "N/A"

        return serial_number

    def get_psu_pn(self, index):
        """
        Get the product name of the psu
        
        :param index: An integer, 1-based index of the PSU.
        :return: Product name
        """
        product_name = "N/A"
        psu_key = "PSU" + str(index) + " FRU"
        psu_pn_key = "Product Name"
      
        try:
            # Request and validate sensor's information
            self.fru_status_list, self.psu_info_list = self.request_data()

            # Get PSU fru info.
            for psu_fru in self.psu_info_list:         
                psu_pn  = str(psu_fru.get(psu_pn_key)).strip()
                if psu_fru.get(psu_key) is not None:
                    product_name = psu_pn if psu_pn.strip() != "" else "N/A"
                    break

        except:
            return "N/A"

        return product_name
