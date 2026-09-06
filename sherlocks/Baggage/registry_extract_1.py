
from Registry import Registry

reg = Registry.Registry("./C/Users/admin/NTUSER.DAT")

keys = [
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
]

for path in keys:
    print(f"\n========== {path} ==========")

    try:
        key = reg.open(path)

        for value in key.values():
            print(f"{value.name()}: {value.value()}")

    except Exception as e:
        print(f"Not found: {e}")