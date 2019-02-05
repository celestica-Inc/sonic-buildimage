# Celestica DX010 and Haliburton Platform modules

CEL_DX010_PLATFORM_MODULE_VERSION = 0.9
CEL_HALIBURTON_PLATFORM_MODULE_VERSION = 0.9

export CEL_DX010_PLATFORM_MODULE_VERSION
export CEL_HALIBURTON_PLATFORM_MODULE_VERSION

CEL_DX010_PLATFORM_MODULE = platform-modules-dx010_$(CEL_DX010_PLATFORM_MODULE_VERSION)_amd64.deb
$(CEL_DX010_PLATFORM_MODULE)_SRC_PATH = $(PLATFORM_PATH)/sonic-platform-modules-cel
$(CEL_DX010_PLATFORM_MODULE)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
$(CEL_DX010_PLATFORM_MODULE)_PLATFORM = x86_64-cel_seastone-r0
SONIC_DPKG_DEBS += $(CEL_DX010_PLATFORM_MODULE)

CEL_HALIBURTON_PLATFORM_MODULE = platform-modules-haliburton_$(CEL_HALIBURTON_PLATFORM_MODULE_VERSION)_amd64.deb
$(CEL_HALIBURTON_PLATFORM_MODULE)_PLATFORM = x86_64-cel_e1031-r0
$(eval $(call add_extra_package,$(CEL_DX010_PLATFORM_MODULE),$(CEL_HALIBURTON_PLATFORM_MODULE)))

SONIC_STRETCH_DEBS += $(CEL_DX010_PLATFORM_MODULE)

# SONIC_PLATFORM_API_PY2 package

SONIC_PLATFORM_API_PY2 = cel_platform_api-1.0-py2-none-any.whl
$(SONIC_PLATFORM_API_PY2)_SRC_PATH = $(PLATFORM_PATH)/sonic-platform-modules-cel/cel-platform-api
$(SONIC_PLATFORM_API_PY2)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_PLATFORM_API_PY2)
