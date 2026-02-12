#!/usr/bin/env python3
"""
Apply all Florida anti-detection patches to Frida 16.7.19
Run this script from frida/subprojects/frida-core directory
"""
import os
import re
import sys

def log(msg):
    print(f"[*] {msg}")

def patch_file(filepath, old, new, description):
    with open(filepath, "r") as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(filepath, "w") as f:
            f.write(content)
        log(f"{description} - OK")
        return True
    else:
        log(f"{description} - pattern not found")
        return False

def main():
    log("Starting Florida patches for Frida 16.7.19")
    
    # ===== Patch 1: string_frida_rpc (lib/base/rpc.vala) =====
    log("Patch 1: string_frida_rpc")
    filepath = "lib/base/rpc.vala"
    with open(filepath, "r") as f:
        content = f.read()
    
    # Add getRpcStr method after the constructor
    old_constructor = 'Object (peer: peer);\n\t\t}'
    new_constructor = '''Object (peer: peer);
		}

		public string getRpcStr(bool quote){
			string result = (string) GLib.Base64.decode((string) GLib.Base64.decode("Wm5KcFpHRTZjbkJq"));
			if(quote){
				return "\\"" + result + "\\"";
			}else{
				return result;
			}
		}'''
    content = content.replace(old_constructor, new_constructor)
    
    # Replace frida:rpc usages
    content = content.replace('.add_string_value ("frida:rpc")', '.add_string_value (getRpcStr(false))')
    content = content.replace('json.index_of ("\\"frida:rpc\\"")', 'json.index_of (getRpcStr(true))')
    content = content.replace('type != "frida:rpc"', 'type != getRpcStr(false)')
    
    with open(filepath, "w") as f:
        f.write(content)
    log("  Patch 1 applied")

    # ===== Patch 2: frida_agent_so (src/linux/linux-host-session.vala) =====
    log("Patch 2: frida_agent_so")
    filepath = "src/linux/linux-host-session.vala"
    with open(filepath, "r") as f:
        content = f.read()
    
    old = 'agent = new AgentDescriptor (PathTemplate ("frida-agent-<arch>.so"),'
    new = '''var random_prefix = GLib.Uuid.string_random();
			agent = new AgentDescriptor (PathTemplate (random_prefix + "-<arch>.so"),'''
    content = content.replace(old, new)
    content = content.replace('new AgentResource ("frida-agent-arm.so",', 'new AgentResource (random_prefix + "-arm.so",')
    content = content.replace('new AgentResource ("frida-agent-arm64.so",', 'new AgentResource (random_prefix + "-arm64.so",')
    
    with open(filepath, "w") as f:
        f.write(content)
    log("  Patch 2 applied")

    # ===== Patch 3: symbol_frida_agent_main =====
    log("Patch 3: symbol_frida_agent_main")
    files_to_patch = [
        "src/agent-container.vala",
        "src/linux/linux-host-session.vala",
    ]
    for fp in files_to_patch:
        if os.path.exists(fp):
            with open(fp, "r") as f:
                content = f.read()
            content = content.replace("frida_agent_main", "main")
            with open(fp, "w") as f:
                f.write(content)
    log("  Patch 3 applied")

    # ===== Patch 6: protocol_unexpected_command =====
    log("Patch 6: protocol_unexpected_command")
    filepath = "src/droidy/droidy-client.vala"
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            content = f.read()
        content = content.replace(
            'throw new Error.PROTOCOL ("Unexpected command");',
            'break; // throw new Error.PROTOCOL ("Unexpected command");'
        )
        with open(filepath, "w") as f:
            f.write(content)
        log("  Patch 6 applied")

    # ===== Patch 8: pool-frida (frida-glue.c) =====
    log("Patch 8: pool-frida in frida-glue.c")
    filepath = "src/frida-glue.c"
    with open(filepath, "r") as f:
        content = f.read()
    
    # Insert g_set_prgname after openssl register
    old = '''#endif

    if (runtime == FRIDA_RUNTIME_OTHER)'''
    new = '''#endif

    g_set_prgname ("ggbond");

    if (runtime == FRIDA_RUNTIME_OTHER)'''
    content = content.replace(old, new)
    
    with open(filepath, "w") as f:
        f.write(content)
    log("  Patch 8 applied")

    # ===== Patch 9: memfd-name-jit-cache =====
    log("Patch 9: memfd-name-jit-cache")
    filepath = "lib/base/linux.vala"
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            content = f.read()
        content = content.replace(
            'return Linux.syscall (SysCall.memfd_create, name, flags);',
            'return Linux.syscall (SysCall.memfd_create, "jit-cache", flags);'
        )
        with open(filepath, "w") as f:
            f.write(content)
        log("  Patch 9 applied")

    # ===== Custom: Hide socket names =====
    log("Custom patch: hide socket names")
    
    # Patch backend
    filepath = "src/linux/frida-helper-backend.vala"
    old = 'return "/frida-" + Uuid.string_random ();'
    new = 'var _b = new StringBuilder (); var _c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; for (var _i = 0; _i != 32; _i++) _b.append_c (_c[Random.int_range (0, _c.length)]); return "/" + _b.str;'
    patch_file(filepath, old, new, "  Socket (backend)")
    
    # Patch process
    filepath = "src/linux/frida-helper-process.vala"
    old = 'string socket_path = "/frida-" + Uuid.string_random ();'
    new = 'var _b = new StringBuilder (); var _c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; for (var _i = 0; _i != 32; _i++) _b.append_c (_c[Random.int_range (0, _c.length)]); string socket_path = "/" + _b.str;'
    patch_file(filepath, old, new, "  Socket (process)")
    
    # Patch system.vala
    filepath = "src/system.vala"
    with open(filepath, "r") as f:
        content = f.read()
    content = content.replace('new StringBuilder ("frida-")', 'new StringBuilder ()')
    content = content.replace('for (var i = 0; i != 16; i++)', 'for (var i = 0; i != 32; i++)')
    content = content.replace('builder.append_printf ("%02x", Random.int_range (0, 256))', 'builder.append_c ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[Random.int_range (0, 62)])')
    with open(filepath, "w") as f:
        f.write(content)
    log("  Socket (system) - OK")

    # ===== Create anti-anti-frida.py =====
    log("Creating anti-anti-frida.py")
    anti_script = '''import lief
import sys
import random
import os

def log_color(msg):
    print(f"\\033[1;31;40m{msg}\\033[0m")

if __name__ == "__main__":
    input_file = sys.argv[1]
    random_charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    log_color(f"[*] Patch frida-agent: {input_file}")
    binary = lief.parse(input_file)

    if not binary:
        log_color(f"[*] Not elf, exit")
        exit()
    
    random_name = "".join(random.sample(random_charset, 5))
    log_color(f"[*] Patch `frida` to `{random_name}`")

    for symbol in binary.symbols:
        if symbol.name == "frida_agent_main":
            symbol.name = "main"

        if "frida" in symbol.name:
            symbol.name = symbol.name.replace("frida", random_name)

        if "FRIDA" in symbol.name:
            symbol.name = symbol.name.replace("FRIDA", random_name)

    all_patch_string = ["FridaScriptEngine", "GLib-GIO", "GDBusProxy", "GumScript"]
    for section in binary.sections:
        if section.name != ".rodata":
            continue
        for patch_str in all_patch_string:
            addr_all = section.search_all(patch_str)
            for addr in addr_all:
                patch = [ord(n) for n in list(patch_str)[::-1]]
                log_color(f"[*] Patching section name={section.name} offset={hex(section.file_offset + addr)} orig:{patch_str} new:{''.join(list(patch_str)[::-1])}")
                binary.patch_address(section.file_offset + addr, patch)

    binary.write(input_file)

    # thread_gum_js_loop
    random_name = "".join(random.sample(random_charset, 11))
    log_color(f"[*] Patch `gum-js-loop` to `{random_name}`")
    os.system(f"sed -b -i s/gum-js-loop/{random_name}/g {input_file}")

    # thread_gmain
    random_name = "".join(random.sample(random_charset, 5))
    log_color(f"[*] Patch `gmain` to `{random_name}`")
    os.system(f"sed -b -i s/gmain/{random_name}/g {input_file}")

    # thread_gdbus
    random_name = "".join(random.sample(random_charset, 5))
    log_color(f"[*] Patch `gdbus` to `{random_name}`")
    os.system(f"sed -b -i s/gdbus/{random_name}/g {input_file}")

    log_color(f"[*] Patch Finish")
'''
    with open("src/anti-anti-frida.py", "w") as f:
        f.write(anti_script)
    log("  anti-anti-frida.py created")

    # ===== Patch 10: exec anti-anti-frida.py in embed-agent.py =====
    log("Patch 10: exec anti-anti-frida.py")
    filepath = "src/embed-agent.py"
    with open(filepath, "r") as f:
        content = f.read()
    
    old = '''else:
                embedded_agent.write_bytes(b"")
            embedded_assets += [embedded_agent]'''
    new = '''else:
                embedded_agent.write_bytes(b"")
            import os
            custom_script=str(output_dir)+"/../../../../frida/subprojects/frida-core/src/anti-anti-frida.py"
            return_code = os.system("python3 "+custom_script+" "+str(priv_dir / f"frida-agent-{flavor}.so"))
            if return_code == 0:
                print("anti-anti-frida finished")
            else:
                print("anti-anti-frida error. Code:", return_code)
            
            embedded_assets += [embedded_agent]'''
    
    content = content.replace(old, new)
    with open(filepath, "w") as f:
        f.write(content)
    log("  Patch 10 applied")

    log("All patches applied successfully!")

if __name__ == "__main__":
    main()
