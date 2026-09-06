import os
from Registry import Registry

path = os.path.expanduser("./C/Users/admin/NTUSER.DAT")

reg = Registry.Registry(path)

paths = [
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32",
]

for path in paths:
    print(f"\n========== {path} ==========")

    try:
        key = reg.open(path)

        for value in key.values():
            print(f"{value.name()}: {value.value()}")

        for subkey in key.subkeys():
            print(f"\n[{subkey.name()}]")

            for value in subkey.values():
                print(f"{value.name()}: {value.value()}")

    except Exception as e:
        print(f"Not found: {e}")