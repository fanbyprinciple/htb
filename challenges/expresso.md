**Flag found:** `HTB{3mul4ting_hw_is_s0_c00l!!!}`

### Analysis summary

The file is a 4 MB ESP32 firmware image (ESP-IDF based, project name “espresso”).

- Starts with `0xff` padding (typical flash image).
- Bootloader / ESP-IDF strings appear throughout (`boot.esp32`, partition table, etc.).
- Relevant strings:
  - `flag did not generate correctly.`
  - `It seems you are running the firmware on cloned hadware.`
  - `Buy the real hardware, or perhaps try to emulate it. ;)`

The firmware intentionally refuses to print the flag on “cloned” (non-original) hardware and tells you to emulate it.

### Emulation (worked)

Espressif’s QEMU fork was used:

```bash
qemu-system-xtensa -nographic -machine esp32 \
  -drive file=firmware.bin,if=mtd,format=raw \
  -serial mon:stdio
```

Boot log ends with:

```
I (1096) main_task: Calling app_main()
I (1106) main: HTB{3mul4ting_hw_is_s0_c00l!!!}
I (1106) main_task: Returned from app_main()
```

That’s the flag. The challenge is deliberately solved by running the image under ESP32 QEMU rather than static analysis alone.
