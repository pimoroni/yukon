include("$(PORT_DIR)/boards/manifest.py")

freeze("$(BOARD_DIR)/../frozen/")

require("sdcard")

require("bundle-networking")

# Bluetooth
require("aioble")
