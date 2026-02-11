#!/usr/bin/env python3
import sys

files = {
    "backend": "frida/subprojects/frida-core/src/linux/frida-helper-backend.vala",
    "process": "frida/subprojects/frida-core/src/linux/frida-helper-process.vala",
    "system": "frida/subprojects/frida-core/src/system.vala"
}

# Patch backend
print("Patching backend...")
with open(files["backend"], "r") as f:
    c = f.read()
old = 'return "/frida-" + Uuid.string_random ();'
new = 'var _b = new StringBuilder (); var _c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; for (var _i = 0; _i != 32; _i++) _b.append_c (_c[Random.int_range (0, _c.length)]); return "/" + _b.str;'
if old in c:
    c = c.replace(old, new)
    with open(files["backend"], "w") as f:
        f.write(c)
    print("  OK")
else:
    print("  FAILED - pattern not found")
    sys.exit(1)

# Patch process
print("Patching process...")
with open(files["process"], "r") as f:
    c = f.read()
old = 'string socket_path = "/frida-" + Uuid.string_random ();'
new = 'var _b = new StringBuilder (); var _c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; for (var _i = 0; _i != 32; _i++) _b.append_c (_c[Random.int_range (0, _c.length)]); string socket_path = "/" + _b.str;'
if old in c:
    c = c.replace(old, new)
    with open(files["process"], "w") as f:
        f.write(c)
    print("  OK")
else:
    print("  FAILED - pattern not found")
    sys.exit(1)

# Patch system
print("Patching system...")
with open(files["system"], "r") as f:
    c = f.read()
c = c.replace('new StringBuilder ("frida-")', 'new StringBuilder ()')
c = c.replace('for (var i = 0; i != 16; i++)', 'for (var i = 0; i != 32; i++)')
c = c.replace('builder.append_printf ("%02x", Random.int_range (0, 256))', 'builder.append_c ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[Random.int_range (0, 62)])')
with open(files["system"], "w") as f:
    f.write(c)
print("  OK")

print("All patches applied!")
