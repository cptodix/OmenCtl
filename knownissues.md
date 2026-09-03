# Known Issues & Bug Reports

Aşağıdaki sorunlar Omen Space 2.0 mimari güncellemeleri ve yamaları ile çözülmüş ve test edilmiştir.

### [8A43] Bug Report — OMEN by HP Gaming Laptop 16-n0xxx #173
- **Description:** Power profiles return to balanced on auto seconds after changing. `hp-rgb-lighting` DKMS module fails to build on kernel 6.12.104 with Clang (`make LLVM=1`).
- **Status:** ✅ **Tamamlandı.** `hp-rgb-lighting` yerine `hp-omen-extra` modülüne geçildi ve Clang derleme hataları giderildi. Güç profili sıfırlanma sorunu `is_victus_s_thermal_profile` ayrıştırması ile çözüldü.

### [8912] Bug Report — OMEN by HP Laptop 16-c0xxx #171
- **Description:** Power profile, fan readout, fan mode and rgb lighting not working. Capabilities DB reports board 8912 not in database.
- **Status:** ✅ **Tamamlandı.** `8912` Board ID'si OMEN 16-c0xxx için `capabilities.rs` veritabanına eklendi.

### [8D41] Bug Report — OMEN MAX Gaming Laptop 16-ah0xxx #169
- **Description:** Changing RGB settings affects only RGB Bar. Zones are inverted horizontally (Zone 1 is on the right). Keyboard is breathing yellow/red, no per-key function active.
- **Status:** ✅ **Tamamlandı.** Yeni Omen Space 2.0 HID backend'i ile Per-Key desteği aktive edildi ve ters bölgeler `capabilities.rs` içerisinde `has_per_key_rgb: true` notuyla çözüldü.

### [88F7] Bug Report — OMEN by HP Laptop 17-ck0xxx #168
- **Description:** Keyboard lighting stays enabled after reboot even if the last action was to turn it off.
- **Status:** ✅ **Tamamlandı.** Linux çekirdeğinin boot sırasında LED durumunu sıfırlamasını engellemek için `rgb.rs` içerisine 5 saniyelik gecikmeli yeniden uygulama (deferred apply) mekanizması eklendi.

### [8D2F] Bug Report — OMEN Gaming Laptop 16-am0018nt #167
- **Description:** Only Auto and Max fan modes are available. Can't use performance/custom mode. Auto mode is too aggressive (starts at 40°C at 2000 RPM). `thermal_profile` node is missing.
- **Status:** ✅ **Tamamlandı.** Cihaz hwmon ve `pwm1` yetkilerine zorunlu fallback sağlayacak şekilde `force_fan_control_support` özelliği aktif edilerek daemon seviyesinde özel fan eğrilerinin kullanılabilmesinin önü açıldı.

### [8C77] Bug Report — OMEN by HP Gaming Laptop 16-wf1xxx #157 / #162
- **Description:** Fan doesn't follow the custom curve and goes up to maximum RPM when CPU goes above 90°C.
- **Status:** ✅ **Tamamlandı.** Termal koruma mekanizmasının (95°C Max Fan) istenildiğinde kapatılabilmesi için Omen Space 2.0 arayüzüne (config) kapatma/açma opsiyonu bağlandı.

### Add board 8D87 (OMEN MAX 16-ak0xxx, RTX 5080) #152
- **Description:** Needs patched hp-wmi for gpu_tgp/gpu_ppab since stock in-tree hp-wmi on kernel 7.0+ doesn't expose them. Missing from capabilities DB and exception list.
- **Status:** ✅ **Tamamlandı.** `8D87` Board ID'si `capabilities.rs`'ye eklendi ve `driver/setup.sh` içerisindeki Kernel 7.0+ yaması exception listesine dâhil edilerek sürücünün doğru kurulması sağlandı.

### [8BAA] Bug Report — OMEN by HP Gaming Laptop 16-wf0xxx #151
- **Description:** Fan RPM reading is always 0 even at max. No custom curve option available. Board not in database.
- **Status:** ✅ **Tamamlandı.** Cihaz `capabilities.rs` veritabanına eklendi. EC erişiminin 0 döndürmesi sorunu hwmon üzerinden zorunlu fan kontrol yaması ile kalıcı olarak aşıldı.
