
#!/usr/bin/env python

#############################################################################
# Celestica
# 
# Watchdog contains an implementation of SONiC Platform Base API 
#
#############################################################################
import ctypes
import fcntl
from ioctl_opt import IOC, IOC_READ, IOR
import sonic_platform

try:
	from sonic_platform_base.watchdog_base import WatchdogBase
except ImportError as e:
	raise ImportError(str(e) + "- required module not found")

class Watchdog(WatchdogBase):

	def __init__(self):

		self.watchdog_path = "/dev/watchdog1"
		self.watchdog_status_path = "/sys/class/watchdog/watchdog1/status"
		self.watchdog_state_path = "/sys/class/watchdog/watchdog1/state"

		self.WDIOS_DISABLECARD = "1"
		self.WDIOS_ENABLECARD = "2"

		self.WDIOC_SETOPTIONS = IOR(ord('W'), 4, ctypes.c_int)
		self.WDIOC_KEEPALIVE = IOR(ord('W'), 5, ctypes.c_int)

	def arm(self, seconds):
		## TODO : Not implement timeout setting.
		self.seconds = seconds

		try:
			with open(self.watchdog_path, "w") as fd:
				ret = fcntl.ioctl(fd, self.WDIOC_SETOPTIONS, self.WDIOS_ENABLECARD)
		except IOError as e:
		    print "I/O error({0}): {1}".format(e.errno, e.strerror)
		    raise IOError("Unable to send ioctl !")
		return True

	def disarm(self):
		try:
			with open(self.watchdog_path, "w") as fd:
				ret = fcntl.ioctl(fd, self.WDIOC_SETOPTIONS, self.WDIOS_DISABLECARD)
		except IOError as e:
		    print "I/O error({0}): {1}".format(e.errno, e.strerror)
		    raise IOError("Unable to send ioctl !")
		return True;

	def is_arm(self):
		try:
			with open(self.watchdog_state_path, "r") as fd:
				if fd.read() == 'active\n':
					return True
				else:
					return False
		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
			raise IOError("Unable to send ioctl !")


	def get_remaining_time(self):

		raise NotImplementedError


