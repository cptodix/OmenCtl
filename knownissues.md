# Known Issues & Bug Reports

The following issues have been resolved and tested with the Omen Space 2.0 architecture updates and patches.

### [8A43] Bug Report — OMEN by HP Gaming Laptop 16-n0xxx #173
- **Description:** Power profiles return to balanced on auto seconds after changing. `hp-rgb-lighting` DKMS module fails to build on kernel 6.12.104 with Clang (`make LLVM=1`).
- **Status:** ✅ **Resolved.** Migrated from `hp-rgb-lighting` to the `hp-omen-extra` module, fixing Clang compilation errors. The power profile reset issue was resolved by decoupling `is_victus_s_thermal_profile`.

### [8912] Bug Report — OMEN by HP Laptop 16-c0xxx #171
- **Description:** Power profile, fan readout, fan mode and rgb lighting not working. Capabilities DB reports board 8912 not in database.
- **Status:** ✅ **Resolved.** Added the `8912` Board ID for OMEN 16-c0xxx to the `capabilities.rs` database.

### [8D41] Bug Report — OMEN MAX Gaming Laptop 16-ah0xxx #169
- **Description:** Changing RGB settings affects only RGB Bar. Zones are inverted horizontally (Zone 1 is on the right). Keyboard is breathing yellow/red, no per-key function active.
- **Status:** ✅ **Resolved.** Activated Per-Key support with the new Omen Space 2.0 HID backend and resolved the inverted zones via the `has_per_key_rgb: true` note in `capabilities.rs`.

### [88F7] Bug Report — OMEN by HP Laptop 17-ck0xxx #168
- **Description:** Keyboard lighting stays enabled after reboot even if the last action was to turn it off.
- **Status:** ✅ **Resolved.** Added a 5-second deferred apply mechanism in `rgb.rs` to prevent the Linux kernel from resetting the LED state during boot.

### [8D2F] Bug Report — OMEN Gaming Laptop 16-am0018nt #167
- **Description:** Only Auto and Max fan modes are available. Can't use performance/custom mode. Auto mode is too aggressive (starts at 40°C at 2000 RPM). `thermal_profile` node is missing.
- **Status:** ✅ **Resolved.** Activated the `force_fan_control_support` feature to provide a mandatory fallback to hwmon and `pwm1` privileges, enabling custom fan curves at the daemon level.

### [8C77] Bug Report — OMEN by HP Gaming Laptop 16-wf1xxx #157 / #162
- **Description:** Fan doesn't follow the custom curve and goes up to maximum RPM when CPU goes above 90°C.
- **Status:** ✅ **Resolved.** Added a toggle option (config) to the Omen Space 2.0 UI so the thermal protection mechanism (95°C Max Fan) can be disabled if desired.

### Add board 8D87 (OMEN MAX 16-ak0xxx, RTX 5080) #152
- **Description:** Needs patched hp-wmi for gpu_tgp/gpu_ppab since stock in-tree hp-wmi on kernel 7.0+ doesn't expose them. Missing from capabilities DB and exception list.
- **Status:** ✅ **Resolved.** Added the `8D87` Board ID to `capabilities.rs` and included it in the Kernel 7.0+ exception list in `driver/setup.sh` to ensure proper driver installation.

### [8BAA] Bug Report — OMEN by HP Gaming Laptop 16-wf0xxx #151
- **Description:** Fan RPM reading is always 0 even at max. No custom curve option available. Board not in database.
- **Status:** ✅ **Resolved.** Added the device to the `capabilities.rs` database. The EC access returning 0 issue was permanently fixed via the mandatory fan control patch over hwmon.

### [8C75] Bug Report — OMEN 17-db0xxx fans stuck at 0 RPM after overheat #175
- **Description:** Both fans silently stuck at 0 RPM after an overheat-induced reboot. `dmesg` showed repeated `ACPI Error: AE_AML_BUFFER_LIMIT` on `_SB.WMID.WMBX` and `_SB.WMID.WMBA`. `pwm1_enable` returned `0` (driver claims manual control), but all WMI fan-speed writes abort at the ACPI layer without error propagation. Fan recovers only at POST because the EC takes over during overheat.
- **Root Cause:** The OMEN 17-db0xxx ACPI table contains the same broken `GETB` helper as `8BAC` — a `CreateField` with zero length that causes `AE_AML_BUFFER_LIMIT` and aborts all `WMID` methods. Board `8C75` was not registered in the DMI table, so it fell through without the necessary no-EC workaround.
- **Status:** ✅ **Resolved.** Added `8C75` to `victus_s_thermal_profile_boards[]` in `driver/hp-wmi.c` with `omen_v1_no_ec_thermal_params` (matching the `8BAC` fix) to bypass EC thermal profile reads and prevent silent fan-write aborts. Also added `8C75` to `capabilities.rs` with `supports_fan_control_ec: false` and flagged it as `is_wmaa_abort_prone_board` so the daemon correctly reports degraded/ProfileOnly control instead of FullControl.

---

## Active User Feedback / Open Issues (Omen Space 2.0)

### UI: Missing Application Icon
- **Description:** The application's icon appears as a red cross on the desktop/dock.
- **Status:** ⚠️ **Open.** Needs fixing in the `.desktop` entry or asset packaging.

### UX: Keyboard Color Menu is Confusing
- **Description:** Users struggle to find where to change the entire keyboard color because the bottom section focuses heavily on per-key settings. Changing all per-key colors unexpectedly changes the global backlight as well.
- **Status:** ⚠️ **Open.** Needs UX improvements in the RGB adjustment menu to clarify global vs. per-key assignments.

### Feature Regression: System Tray Support
- **Description:** Unlike `omenctl`, the new Omen Space interface doesn't minimize to the system tray on close.
- **Status:** ⚠️ **Open.** Needs to be re-implemented or properly integrated with the existing `omen-tray` backend.
