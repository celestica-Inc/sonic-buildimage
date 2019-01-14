# fwmgrutil.py
#
# Platform-specific firmware management interface for SONiC
#

import subprocess
import requests

try:
    from sonic_fwmgr.fwgmr_base import FwMgrUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


class FwMgrUtil(FwMgrUtilBase):

    """Platform-specific FwMgrUtil class"""

    def __init__(self):
        """TODO: to be defined1. """
        self.onie_config_file = "/host/machine.conf"
        self.bmc_info_url = "http://240.1.1.1:8080/api/sys/bmc"

    def get_bmc_version(self):
        """Get BMC version from SONiC
        :returns: version string

        """
        bmc_version = "None"

        bmc_version_key = "OpenBMC Version"
        bmc_info_req = requests.get(self.bmc_info_url)
        bmc_info_json = bmc_info_req.json()
        bmc_info = bmc_info_json.get('Information')
        bmc_version = bmc_info.get(bmc_version_key)

        return bmc_version

    def get_cpld_version(self):
        """Get CPLD version from SONiC
        :returns: version string

        """
        return '0.0.0'

    def get_bios_version(self):
        """Get BIOS version from SONiC
        :returns: version string

        """
        bios_version = 'None'

        p = subprocess.Popen(
            ["sudo", "dmidecode", "-s", "bios-version"], stdout=subprocess.PIPE)
        raw_data = str(p.communicate()[0])
        raw_data_list = raw_data.split("\n")
        bios_version = raw_data_list[0] if len(
            raw_data_list) == 1 else raw_data_list[-2]

        return bios_version

    def get_onie_version(self):
        """Get ONiE version from SONiC
        :returns: version string

        """
        onie_verison = 'None'

        onie_version_keys = "onie_version"
        onie_config_file = open(self.onie_config_file, "r")
        for line in onie_config_file.readlines():
            if onie_version_keys in line:
                onie_version_raw = line.split('=')
                onie_verison = onie_version_raw[1].strip()
                break
        return onie_verison

    def get_pcie_version(self):
        """Get PCiE version from SONiC
        :returns: version string

        """
        return '0.0.0'

    def get_fpga_version(self):
        """Get FPGA version from SONiC
        :returns: TODO

        """
        return '0.0.0'
