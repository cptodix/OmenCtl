# Hardware Offsets & Registers

HP Omen laptops primarily expose hardware controls through ACPI WMI interfaces. However, some legacy or non-standard models require direct interaction with the Embedded Controller (EC) memory space. This document details both the direct EC register offsets and the ACPI WMI commands used by OmenCtl.

## 1. Embedded Controller (EC) Registers

On supported or legacy models, OmenCtl interacts with the Linux EC module (`ec_sys`) mounted at `/sys/kernel/debug/ec/ec0/io`. Writing bytes to specific offsets controls hardware behavior by bypassing ACPI.

*Warning: Directly writing to EC registers on unsupported models can cause hardware panics and sudden system shutdowns.*

### Fan Control Offsets
- **`0x2E`** (Fan 1 Speed %): Writes an integer `0-100` representing percentage speed.
- **`0x2F`** (Fan 2 Speed %): Writes an integer `0-100` representing percentage speed.
- **`0x34`** (Fan 1 RPM Target): Sets target speed in units of 100 RPM (e.g., writing `40` = 4000 RPM).
- **`0x35`** (Fan 2 RPM Target): Sets target speed in units of 100 RPM.
- **`0xEC`** (Fan Boost Toggle): Writes `0x00` (Off) or `0x0C` (Max Boost/ON).
- **`0xF4`** (Fan State): `0x00` (Enabled/Auto), `0x02` (Disabled).

### Thermal & Power Offsets
- **`0x57`** (CPU Temp): Real-time EC CPU temperature readout in Celsius.
- **`0xB7`** (GPU Temp): Real-time EC GPU temperature readout in Celsius.
- **`0x95`** (Performance Mode): The primary thermal profile register on legacy Omen laptops.
  - `0x30`: Default / Balanced
  - `0x31`: Performance
  - `0x50`: Cool / Power Saver
- **`0x59`** (Fallback Thermal Register): Used on specific newer boards (e.g., 8E35, 8A43) where standard WMI routing is broken by the BIOS. Same `0x30`/`0x31`/`0x50` payloads as above.

---

## 2. ACPI WMI (Windows Management Instrumentation)

Most modern Omen laptops (2021+) use the `hp-wmi` Linux driver, which safely wraps ACPI WMI calls into `sysfs` nodes.

- **Thermal Profiles (`/sys/devices/platform/hp-wmi/thermal_profile`)**:
  - `0`: Balanced
  - `1`: Performance
  - `2`: Cool
  This node directly invokes the BIOS WMI method for CommandType `0x11` (ThermalControl).

- **GPU TGP & Power Limits**:
  Certain kernel sysfs nodes like `gpu_tgp` and `gpu_ppab` are mapped to undocumented WMI commands that increase the Total Graphics Power (cTGP) limit for NVIDIA GPUs dynamically when switching to Performance mode.

---

## 3. MUX Switch (GPU Mode)

The MUX switch controls whether the internal laptop display is electrically routed through the iGPU (Hybrid) or dGPU (Discrete).

OmenCtl includes a custom driver extension (`hp-rgb-lighting.c`) that hooks the undocumented HP WMI MUX interface and exposes it to `/sys/devices/platform/hp-rgb-lighting/omen_mux`.

- **WMI Method Payload**: CommandType `0x52`, Command `0x00002`
- **Writes:**
  - `0`: Hybrid (Optimus) Mode
  - `1`: Discrete (dGPU only) Mode

*Note: Any write to the MUX WMI register triggers a BIOS flag. The hardware will not switch modes until a full system reboot is performed.*
