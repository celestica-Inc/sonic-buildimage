# fwmgrutil.py
#
# Platform-specific firmware management interface for SONiC
#

try:
    from sonic_fwmgr.fwgmr_base import FwMgrUtilBase
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))


class FwMgrUtil(FwMgrUtilBase):

    """Platform-specific FwMgrUtil class"""

    def __init__(self):
        """TODO: to be defined1. """
        self.onie_config_file = "/host/machine.conf"

    def get_bmc_version(self):
        """Get BMC version from SONiC
        :returns: version string

        """
        return '0.0.0'

    def get_cpld_version(self):
        """Get CPLD version from SONiC
        :returns: version string

        """
        return '0.0.0'

    def get_bios_version(self):
        """Get BIOS version from SONiC
        :returns: version string

        """
        return '0.0.0'

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
