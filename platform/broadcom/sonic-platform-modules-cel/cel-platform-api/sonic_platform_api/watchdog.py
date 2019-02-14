
#!/usr/bin/env python

#############################################################################
# Celestica
# 
# Watchdog contains an implementation of SONiC Platform Base API 
#
#############################################################################
import ctypes
import fcntl
import os
from ioctl_opt import IOC, IOC_READ, IOR, IOWR
import sonic_platform

try:
	from sonic_platform_base.watchdog_base import WatchdogBase
except ImportError as e:
	raise ImportError(str(e) + "- required module not found")

WATCHDOG_IOCTL_BASE = ord('W')
int_size = ctypes.c_int

# WDIOC_GETSUPPORT = IOR(WATCHDOG_IOCTL_BASE, 0, struct_watchdog_info_size)
WDIOC_GETSTATUS = IOR(WATCHDOG_IOCTL_BASE, 1, int_size)
WDIOC_GETBOOTSTATUS = IOR(WATCHDOG_IOCTL_BASE, 2, int_size)
WDIOC_GETTEMP = IOR(WATCHDOG_IOCTL_BASE, 3, int_size)
WDIOC_SETOPTIONS = IOR(WATCHDOG_IOCTL_BASE, 4, int_size)
WDIOC_KEEPALIVE = IOR(WATCHDOG_IOCTL_BASE, 5, int_size)
WDIOC_SETTIMEOUT = IOWR(WATCHDOG_IOCTL_BASE, 6, int_size)
WDIOC_GETTIMEOUT = IOR(WATCHDOG_IOCTL_BASE, 7, int_size)
WDIOC_SETPRETIMEOUT = IOWR(WATCHDOG_IOCTL_BASE, 8, int_size)
WDIOC_GETPRETIMEOUT = IOR(WATCHDOG_IOCTL_BASE, 9, int_size)
WDIOC_GETTIMELEFT = IOR(WATCHDOG_IOCTL_BASE, 10, int_size)

WDIOS = {
	"DISABLECARD": "1",    # Turn off the watchdog timer
	"ENABLECARD": "2",     # Turn on the watchdog timer
	"TEMPPANIC": "4",      # Kernel panic on temperature trip
}

class Watchdog(WatchdogBase):

	def __init__(self):
		self.device_path = "/dev/watchdog1"
		self.watchdog_status_path = "/sys/class/watchdog/watchdog1/status"
		self.watchdog_state_path = "/sys/class/watchdog/watchdog1/state"

	@property
	def is_running(self):
		return self._fd is not None

	def open(self):
		try:
			self._fd = os.open(self.device_path, os.O_WRONLY)
		except OSError as e:
			raise OSError("Watchdog error({0}): {1}".format(e.errno, e.strerror))

	def close(self):
		if self.is_running:
			try:
				os.write(self._fd, b'V')
				os.close(self._fd)
				self._fd = None
			except OSError as e:
				raise OSError("Watchdog error({0}): {1}".format(e.errno, e.strerror))

	def _ioctl(self, func, arg):
		"""Runs the specified ioctl on the underlying fd.

		Raises WatchdogError if the device is closed.
		Raises OSError or IOError (Python 2) when the ioctl fails."""
		if self._fd is None:
			raise IOError("Watchdog error({0}): {1}".format(e.errno, e.strerror))
		fcntl.ioctl(self._fd, func, arg)

	def keepalive(self):
		if self._fd is None:
			raise IOError("Watchdog device is closed")
		try:
			os.write(self._fd, b'1')
		except OSError as e:
			raise OSError("Watchdog error({0}): {1}".format(e.errno, e.strerror))

	#################################################################

	def arm(self, seconds):
		## TODO : Not implement timeout setting.
		self.seconds = seconds
		try:
			self.open()
			self.keepalive()
			self.close()
		except (OSError, IOError) as e:
		    raise IOError("Watchdog error({0}): {1}".format(e.errno, e.strerror))
		
		return True

	def disarm(self):
		print "WDIOC_SETOPTIONS ",WDIOC_SETOPTIONS
		try:
			self.open()
			self._ioctl(WDIOC_SETOPTIONS, WDIOS['DISABLECARD'])
			self.close()
		except (OSError, IOError) as e:
		    raise IOError("Watchdog error({0}): {1}".format(e.errno, e.strerror))
		return True;

	def is_arm(self):
		try:
			with open(self.watchdog_state_path, "r") as fd:
				if fd.read() == 'active\n':
					return True
				else:g
					return False
		except (OSError, IOError) as e:
			raise IOError("Watchdog error({0}): {1}".format(e.errno, e.strerror))


	def get_remaining_time(self):

		raise NotImplementedError


