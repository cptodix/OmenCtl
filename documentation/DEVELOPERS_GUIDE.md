# Developer's Guide: Where to Modify Code

This document explains step-by-step **which files you need to modify** when you want to change or add features to OmenCtl. The project is strictly separated into a Frontend (GUI) and a Backend (Daemon). 

---

## 1. Modifying the User Interface (GUI)
If you want to add a new button, change a layout, or modify how a feature looks to the user, you must edit the files in the `src/gui/` directory.

- **`src/gui/pages/fan_page.py`**: Modify this file if you want to change the custom fan curve editor, add new fan modes, or change the layout of the Performance/Fan page.
- **`src/gui/pages/power_page.py`**: Modify this if you want to add new CPU Undervolting sliders, TCC offsets, or PL1/PL2 power limits.
- **`src/gui/pages/lighting_page.py`**: Edit this to add new RGB animation modes or change the color picker.
- **`src/gui/pages/mux_page.py`**: Edit this to change how the Hybrid/Discrete GPU switch looks.
- **`src/omen-tray.py`**: Modify this if you want to add or remove right-click menu items in the system tray icon.

*Note: Whenever you make the GUI send a new command, you MUST also add the corresponding handler in the backend daemon!*

---

## 2. Modifying Hardware Logic (The Daemon)
When a button is clicked in the GUI, it sends a D-Bus signal to the Daemon. If you want to change **how** the laptop hardware actually behaves (e.g., how the fan speed is applied, or how the power profile is set), you must edit the files in `src/daemon/services/`.

- **`src/daemon/services/fan_service.py`**: Modify this file to change the background thermal protection logic, how the fan curve percentages are calculated, or how often the fan speeds are polled.
- **`src/daemon/services/power_service.py`**: Modify this if you want to change how RyzenAdj or Undervolt commands are executed in the shell, or how performance modes are applied.
- **`src/daemon/services/rgb_service.py`**: Modify this if you need to add support for a new keyboard lighting zone or change how animation frames are written to the kernel driver.
- **`src/daemon/services/mux_service.py`**: Edit this if you are adding support for a new MUX switch backend (e.g., `envycontrol` or `supergfxctl`).

---

## 3. Adding Support for a New Laptop Model
If your laptop has missing features (like the Fan Control isn't working, or Power Tuning is greyed out), it means the capabilities database doesn't know about your Board ID.

**File to modify:** `src/daemon/common/capabilities.py`

1. Find your laptop's Board ID by running: `cat /sys/class/dmi/id/board_name` (e.g., `8A43`).
2. Open `src/daemon/common/capabilities.py`.
3. Locate the `KNOWN_MODELS` dictionary.
4. Add a new entry for your Board ID. For example:
   ```python
   "8A43": ModelCapabilities("8A43", "OMEN 16-n0xxx", has_mux_switch=True, supports_fan_control_ec=False)
   ```
5. If your laptop panics when writing to the EC, make sure `supports_fan_control_ec=False`.

---

## 4. Modifying Deep Hardware / EC Access
If you are reverse-engineering a new ACPI method or finding a new EC offset for a broken laptop model, you will modify the core hardware controllers.

- **`src/daemon/common/ec_controller.py`**: Modify this to add new Embedded Controller (EC) memory offsets (e.g., adding a fallback for `0x59` or reading a new temperature sensor).
- **`src/daemon/common/acpi_mapper.py`**: Modify this if you want the daemon to extract and decompile the DSDT to look for new WMI GUIDs or undocumented ACPI methods.
- **`driver/hp-rgb-lighting.c`**: If you are adding native kernel-level support for a new OMEN feature (like the `omen_mux` sysfs node), you must write C code here and recompile the kernel module using `sudo ./setup.sh install`.
