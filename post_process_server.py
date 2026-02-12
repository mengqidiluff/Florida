#!/usr/bin/env python3
"""
Post-process frida-server binary to patch remaining detection strings
"""
import random
import string
import sys

def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

def main():
    server_path = sys.argv[1] if len(sys.argv) > 1 else "build-android-arm64/subprojects/frida-core/server/frida-server"
    
    with open(server_path, 'rb') as f:
        data = f.read()
    
    print(f"Size: {len(data)}")
    print(f"frida:rpc before: {data.count(b'frida:rpc')}")
    
    # Patch remaining frida:rpc
    data = data.replace(b'frida:rpc', b'AdWBfWIcq')
    
    # Patch thread names
    gmain_new = random_string(5).encode()
    gdbus_new = random_string(5).encode()
    data = data.replace(b'gmain', gmain_new)
    data = data.replace(b'gdbus', gdbus_new)
    
    # Patch gum-js-loop
    gum_new = random_string(11).encode()
    data = data.replace(b'gum-js-loop', gum_new)
    
    # Patch pool-spawner
    pool_new = random_string(12).encode()
    data = data.replace(b'pool-spawner', pool_new)
    
    # Patch frida-agent
    agent_new = random_string(11).encode()
    data = data.replace(b'frida-agent', agent_new)
    
    # Patch frida-server
    server_new = random_string(12).encode()
    data = data.replace(b'frida-server', server_new)
    
    # Patch /frida- paths
    path_new = '/' + random_string(6)
    data = data.replace(b'/frida-', path_new.encode())
    
    print(f"frida:rpc after: {data.count(b'frida:rpc')}")
    print(f"AdWBfWIcq after: {data.count(b'AdWBfWIcq')}")
    print(f"gmain after: {data.count(b'gmain')}")
    print(f"gdbus after: {data.count(b'gdbus')}")
    print(f"/frida- after: {data.count(b'/frida-')}")
    
    with open(server_path, 'wb') as f:
        f.write(data)
    
    print("Post-processing complete!")

if __name__ == "__main__":
    main()
