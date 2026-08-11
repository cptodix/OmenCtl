import os
import sys
import tempfile
import threading
import types
import unittest
from unittest import mock


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "daemon"))

gi = types.ModuleType("gi")
gi.repository = types.ModuleType("gi.repository")
gi.repository.GLib = types.SimpleNamespace(MainLoop=lambda: None)
sys.modules.setdefault("gi", gi)
sys.modules.setdefault("gi.repository", gi.repository)
sys.modules.setdefault("pydbus", types.SimpleNamespace(SystemBus=lambda: None))

from services import fan_service


class FanControllerSysfsTest(unittest.TestCase):
    def make_controller(self, hwmon_path, fans=(1, 2), max_speed=6000):
        controller = fan_service.FanController.__new__(fan_service.FanController)
        controller.hwmon_path = hwmon_path
        controller.found_fans = list(fans)
        controller.fan_count = len(fans)
        controller.max_speeds = {fan: max_speed for fan in fans}
        controller.mode = "custom"
        controller._fallback_paths = {}
        return controller

    def write_file(self, directory, name, value="0"):
        path = os.path.join(directory, name)
        with open(path, "w") as handle:
            handle.write(str(value))
        return path

    def read_file(self, directory, name):
        with open(os.path.join(directory, name)) as handle:
            return handle.read()

    def test_existing_fan_target_file_wins_over_pwm_fallback(self):
        with tempfile.TemporaryDirectory() as hwmon:
            self.write_file(hwmon, "pwm1", "0")
            self.write_file(hwmon, "fan1_target", "0")
            controller = self.make_controller(hwmon, fans=(1,))

            self.assertTrue(controller.set_fan_target(1, 3000))

            self.assertEqual(self.read_file(hwmon, "fan1_target"), "3000")
            self.assertEqual(self.read_file(hwmon, "pwm1"), "0")

    def test_pwm_fallback_maps_rpm_to_pwm_when_target_file_missing(self):
        with tempfile.TemporaryDirectory() as hwmon:
            self.write_file(hwmon, "pwm1", "0")
            self.write_file(hwmon, "pwm1_enable", "1")
            controller = self.make_controller(hwmon, fans=(1,), max_speed=6000)

            self.assertTrue(controller.set_fan_target(1, 6000))

            self.assertEqual(self.read_file(hwmon, "pwm1"), "255")

    def test_pwm_fallback_clamps_nonzero_pwm_to_safe_minimum(self):
        with tempfile.TemporaryDirectory() as hwmon:
            self.write_file(hwmon, "pwm1", "0")
            self.write_file(hwmon, "pwm1_enable", "1")
            controller = self.make_controller(hwmon, fans=(1,), max_speed=6000)

            self.assertTrue(controller.set_fan_target(1, 1000))

            self.assertEqual(self.read_file(hwmon, "pwm1"), "220")

    def test_pwm_fallback_preserves_zero_pwm(self):
        with tempfile.TemporaryDirectory() as hwmon:
            self.write_file(hwmon, "pwm1", "255")
            self.write_file(hwmon, "pwm1_enable", "1")
            controller = self.make_controller(hwmon, fans=(1,), max_speed=6000)

            self.assertTrue(controller.set_fan_target(1, 0))

            self.assertEqual(self.read_file(hwmon, "pwm1"), "0")

    def test_read_current_mode_uses_thermal_profile_fallback_for_max(self):
        controller = self.make_controller("/fake/hwmon", fans=(1,))
        def read_side_effect(path, default=0):
            if path.endswith("pwm1_enable"):
                return 2
            return 1

        def exists_side_effect(path):
            return path.endswith("thermal_profile")

        with mock.patch.object(fan_service, "sysfs_read", side_effect=read_side_effect), \
             mock.patch.object(fan_service, "sysfs_exists", side_effect=exists_side_effect), \
             mock.patch.object(fan_service, "sysfs_read_str", return_value="balanced"):
            controller._read_current_mode()
        self.assertEqual(controller.mode, "max")

    def test_read_current_mode_uses_platform_profile_fallback_for_max(self):
        controller = self.make_controller("/fake/hwmon", fans=(1,))
        def read_side_effect(path, default=0):
            if path.endswith("pwm1_enable"):
                return 2
            return 0

        def exists_side_effect(path):
            return path.endswith("platform_profile")

        with mock.patch.object(fan_service, "sysfs_read", side_effect=read_side_effect), \
             mock.patch.object(fan_service, "sysfs_exists", side_effect=exists_side_effect), \
             mock.patch.object(fan_service, "sysfs_read_str", return_value="performance"):
            controller._read_current_mode()
        self.assertEqual(controller.mode, "max")


class FanServiceThermalProtectionTest(unittest.TestCase):
    def make_service(self, enabled=True):
        service = fan_service.FanService.__new__(fan_service.FanService)
        service._cache_lock = threading.Lock()
        service._thermal_protection_active = False
        service._thermal_protection_entered_at = 0.0
        service._pre_protection_mode = None
        service._fan_cache = {}
        service._config = mock.Mock()
        service._fan = mock.Mock()
        service._fan.get_mode.return_value = "auto"
        service._fan.found_fans = []
        service._fan.is_available.return_value = True
        service._fan.get_fan_count.return_value = 0
        service._fan.supports_custom_mode.return_value = True

        state = {
            "fan_mode": "auto",
            "custom_curve": "[]",
            "thermal_protection_enabled": enabled,
        }

        def _get(key, default=None):
            return state.get(key, default)

        def _set(key, value):
            state[key] = value

        service._config.get.side_effect = _get
        service._config.set.side_effect = _set
        return service

    def test_monitor_loop_does_not_force_max_when_thermal_protection_disabled(self):
        service = self.make_service(enabled=False)
        service._get_max_temp = mock.Mock(return_value=96.0)
        with mock.patch.object(fan_service.system_sleeping, "is_set", return_value=False), \
             mock.patch.object(fan_service, "send_desktop_notification"), \
             mock.patch.object(fan_service.time, "sleep", side_effect=RuntimeError("stop-loop")):
            with self.assertRaisesRegex(RuntimeError, "stop-loop"):
                service._monitor_loop()

        self.assertFalse(service._thermal_protection_active)
        service._fan.set_mode.assert_not_called()

    def test_monitor_loop_forces_max_when_thermal_protection_enabled(self):
        service = self.make_service(enabled=True)
        service._get_max_temp = mock.Mock(return_value=96.0)
        with mock.patch.object(fan_service.system_sleeping, "is_set", return_value=False), \
             mock.patch.object(fan_service, "send_desktop_notification"), \
             mock.patch.object(fan_service.time, "sleep", side_effect=RuntimeError("stop-loop")):
            with self.assertRaisesRegex(RuntimeError, "stop-loop"):
                service._monitor_loop()

        self.assertTrue(service._thermal_protection_active)
        service._fan.set_mode.assert_called_with("max")

    def test_set_thermal_protection_enabled_persists_flag(self):
        service = self.make_service(enabled=True)
        self.assertEqual(service.SetThermalProtectionEnabled(False), "OK")
        self.assertFalse(service.GetThermalProtectionEnabled())
        service._config.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
