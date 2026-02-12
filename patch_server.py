#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binary patch frida-server to replace detection strings.
Uses SAME-LENGTH replacements for binary compatibility.
"""
import sys

def patch_binary(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    original_size = len(data)
    print(f"File size: {original_size}")
    
    # SAME-LENGTH replacements (critical for binary patching!)
    replacements = [
        # Agent main (16 chars each)
        (b'frida_agent_main', b'bkWNs_agent_main'),
        # Agent lib (11 chars each)  
        (b'frida-agent', b'bkWNs-agent'),
        # RPC (9 chars each)
        (b'frida:rpc', b'AdWBfWIcq'),
        # Server/Helper (12 chars each)
        (b'frida-server', b'bkWNs-server'),
        (b'frida-helper', b'bkWNs-helper'),
        # Package identifiers (15 chars each)
        (b're.frida.server', b'xx.xxxxx.xxxxxx'),
        (b're.frida.Helper', b'xx.xxxxx.Xxxxxx'),
        # Socket name (7 chars each)
        (b'/frida-', b'/bkWNs-'),
        # Thread names
        (b'gum-js-loop', b'xxx-xx-loop'),
        (b'pool-spawner', b'pool-xxxxxxx'),
        (b'gmain', b'xmain'),
        (b'gdbus', b'xdbus'),
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
