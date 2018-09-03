# Celestica Platform modules

CEL_DX010_PLATFORM_MODULE_VERSION = 1.1
CEL_QUESTONE2_PLATFORM_MODULE_VERSION = 1.1
CEL_SILVERSTONE_PLATFORM_MODULE_VERSION = 1.1
CEL_FISHBONE48_PLATFORM_MODULE_VERSION = 1.1
CEL_FISHBONE32_PLATFORM_MODULE_VERSION = 1.1

export CEL_DX010_PLATFORM_MODULE_VERSION
export CEL_QUESTONE2_PLATFORM_MODULE_VERSION
export CEL_SILVERSTONE_PLATFORM_MODULE_VERSION
export CEL_FISHBONE48_PLATFORM_MODULE_VERSION
export CEL_FISHBONE32_PLATFORM_MODULE_VERSION

CEL_DX010_PLATFORM_MODULE = platform-modules-dx010_$(CEL_DX010_PLATFORM_MODULE_VERSION)_amd64.deb
$(CEL_DX010_PLATFORM_MODULE)_SRC_PATH = $(PLATFORM_PATH)/sonic-platform-modules-cel
$(CEL_DX010_PLATFORM_MODULE)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
$(CEL_DX010_PLATFORM_MODULE)_PLATFORM = x86_64-cel_seastone-r0
SONIC_DPKG_DEBS += $(CEL_DX010_PLATFORM_MODULE)

CEL_QUESTONE2_PLATFORM_MODULE = platform-modules-questone2_$(CEL_QUESTONE2_PLATFORM_MODULE_VERSION)_amd64.deb
$(CEL_QUESTONE2_PLATFORM_MODULE)_PLATFORM = x86_64-cel_questone_2-r0
$(eval $(call add_extra_package,$(CEL_DX010_PLATFORM_MODULE),$(CEL_QUESTONE2_PLATFORM_MODULE)))

CEL_SILVERSTONE_PLATFORM_MODULE = platform-modules-silverstone_$(CEL_SILVERSTONE_PLATFORM_MODULE_VERSION)_amd64.deb
$(CEL_SILVERSTONE_PLATFORM_MODULE)_PLATFORM = x86_64-cel_silverstone-r0
$(eval $(call add_extra_package,$(CEL_DX010_PLATFORM_MODULE),$(CEL_SILVERSTONE_PLATFORM_MODULE)))

CEL_FISHBONE48_PLATFORM_MODULE = platform-modules-fishbone48_$(CEL_FISHBONE48_PLATFORM_MODULE_VERSION)_amd64.deb
$(CEL_FISHBONE48_PLATFORM_MODULE)_PLATFORM = x86_64-alibaba_as13-48f8h-cl-r0
$(eval $(call add_extra_package,$(CEL_DX010_PLATFORM_MODULE),$(CEL_FISHBONE48_PLATFORM_MODULE)))

CEL_FISHBONE32_PLATFORM_MODULE = platform-modules-fishbone32_$(CEL_FISHBONE32_PLATFORM_MODULE_VERSION)_amd64.deb
$(CEL_FISHBONE32_PLATFORM_MODULE)_PLATFORM = x86_64-alibaba_as13-32h-cl-r0
$(eval $(call add_extra_package,$(CEL_DX010_PLATFORM_MODULE),$(CEL_FISHBONE32_PLATFORM_MODULE)))
