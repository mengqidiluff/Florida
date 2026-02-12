#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binary patch frida Python wheel (_frida.pyd or _frida.so)
"""
import sys
import os
import zipfile
import shutil
import tempfile

def patch_binary(data):
    """Patch binary data and return patched data"""
    replacements = [
        (b'frida_agent_main', b'fxxxx_agent_main'),
        (b'frida_agent_container', b'fxxxx_agent_container'),
        (b'frida_agent_message', b'fxxxx_agent_message'),
        (b'frida_agent_runner', b'fxxxx_agent_runner'),
        (b're.frida.server', b'xx.xxxxx.xxxxxx'),
        (b're.frida.Helper', b'xx.xxxxx.Xxxxxx'),
        (b'FridaScriptEngine', b'XxxxxScriptEngine'),
        (b'GumScriptScheduler', b'XxxScriptScheduler'),
    ]
    
    for old, new in replacements:
        if len(old) != len(new):
            print(f"ERROR: Length mismatch for {old} -> {new}")
            continue
        count = data.count(old)
        if count > 0:
            data = data.replace(old, new)
            print(f"Replaced {old.decode()}: {count} times")
    
    return data

def patch_wheel(wheel_path):
    """Patch a wheel file in place"""
    print(f"Processing wheel: {wheel_path}")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract wheel
        with zipfile.ZipFile(wheel_path, 'r') as zf:
            zf.extractall(temp_dir)
        
        # Find and patch _frida.pyd or _frida.so
        patched = False
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f.startswith('_frida') and (f.endswith('.pyd') or f.endswith('.so')):
                    pyd_path = os.path.join(root, f)
                    print(f"Found: {f}")
                    
                    with open(pyd_path, 'rb') as fp:
                        data = fp.read()
                    
                    original_size = len(data)
                    data = patch_binary(data)
                    
                    if len(data) != original_size:
                        print(f"ERROR: Size changed!")
                        sys.exit(1)
                    
                    with open(pyd_path, 'wb') as fp:
                        fp.write(data)
                    
                    patched = True
                    print(f"Patched: {f}")
        
        if not patched:
            print("WARNING: No _frida.pyd or _frida.so found")
            return
        
        # Remove original wheel
        os.remove(wheel_path)
        
        # Repack wheel
        with zipfile.ZipFile(wheel_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    file_path = os.path.join(root, f)
                    arc_name = os.path.relpath(file_path, temp_dir)
                    zf.write(file_path, arc_name)
        
        print(f"Wheel repacked: {wheel_path}")
        
    finally:
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: patch_wheel.py <wheel_path>")
        sys.exit(1)
    patch_wheel(sys.argv[1])
