from Registry import Registry

reg = Registry.Registry("./C/Users/steve/NTUSER.DAT")

path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"

try:
    key = reg.open(path)
    print("=== Steve RunMRU ===")
    for value in key.values():
        print(f"{value.name()}: {value.value()}")
except Exception as e:
    print("Not found:", e)