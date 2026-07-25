# Architecture & Execution Flow

OmenCtl adopts a modern client-server architecture to ensure security, performance, and stability. Because controlling hardware (like WMI, ACPI, and EC) requires `root` privileges, the GUI runs unprivileged in the user space, while all hardware logic is handled by a background daemon.

## Core Layers

### 1. The GUI & Tray App (User Space)
Written in Python using GTK4 and Libadwaita for a native, responsive Linux experience. 
The GUI **never** touches hardware directly. Instead, it relies on D-Bus proxies. When you open the dashboard or change a setting, the GUI makes asynchronous or non-blocking D-Bus calls to fetch data or push commands.

### 2. The D-Bus IPC (Inter-Process Communication)
D-Bus is the bridge between the GUI and the Daemon. OmenCtl uses the `pydbus` library.
Services are separated logically:
- `com.yyl.hpmanager.fan`
- `com.yyl.hpmanager.power`
- `com.yyl.hpmanager.rgb`
- `com.yyl.hpmanager.mux`

### 3. The Daemon (`omenctld`)
Running as `root`, the daemon listens to D-Bus and manages background tasks like the custom fan curve loop, app-based power profiles, and thermal protection.

---

## Execution Flow: How a Command is Processed

Here is a step-by-step breakdown of how a command flows from the highest GUI layer to the deepest hardware ACPI/WMI layer.

### Example: Setting the Fan Mode to "Max"

1. **User Interaction (GUI):**
   The user clicks the "Max" toggle button in the Fan control page (`src/gui/pages/fan_page.py`).

2. **D-Bus Call (IPC):**
   The GUI fires a D-Bus method: `self.services["fan"].SetFanMode("max")`.

3. **Daemon Reception (`fan_service.py`):**
   The daemon process receives the request. It checks if Thermal Protection is active. If safe, it forwards the command to the hardware abstraction layer: `self._fan.set_mode("max")`.

4. **Hardware Driver / Sysfs Write:**
   Depending on the laptop's board ID, the controller translates "max" into a low-level command. Usually, it writes `0` (or `1` depending on PWM support) to the kernel `sysfs` node provided by the `hp-wmi` module: `/sys/devices/platform/hp-wmi/pwm1_enable`.

5. **Kernel WMI Driver (`hp-wmi.c`):**
   The Linux kernel intercepts this write. The `hp-wmi` driver converts the fan speed request into an ACPI WMI command block containing the specific CommandType and data buffers required by HP.

6. **ACPI BIOS Method Execution:**
   The kernel evaluates the ACPI object `_SB.WMID.WQBZ` (or similar WMI GUID method). The motherboard's BIOS firmware handles this ACPI call.

7. **Embedded Controller (EC):**
   The ACPI method finally translates the WMI payload into direct I/O port writes to the Embedded Controller (EC). The EC updates its fan control register (e.g., writing the corresponding speed byte to offset `0x34`), which increases the physical fan motor voltage to 100%.
