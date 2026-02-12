#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binary patch frida-server to replace detection strings
"""
import sys

def patch_binary(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    original_size = len(data)
    print(f"File size: {original_size}")
    
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
    
    if len(data) != original_size:
        print(f"ERROR: Size changed from {original_size} to {len(data)}")
        sys.exit(1)
    
    with open(file_path, 'wb') as f:
        f.write(data)
    
    print("Binary patching complete!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: patch_server.py <server_path>")
        sys.exit(1)
    patch_binary(sys.argv[1])
