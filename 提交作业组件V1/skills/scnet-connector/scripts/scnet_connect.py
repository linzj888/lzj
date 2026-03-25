#!/usr/bin/env python3
import argparse, json, os, sys, subprocess

C = os.path.expanduser("~/.scnet/config.json")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--user', '-u'); p.add_argument('--host', '-h')
    p.add_argument('--port', '-p', type=int, default=22)
    p.add_argument('--key', '-k'); p.add_argument('--save', '-s', action='store_true')
    a = p.parse_args()
    
    cfg = json.load(open(C)) if os.path.exists(C) else {}
    u = a.user or cfg.get('username')
    h = a.host or cfg.get('hostname')
    pt = a.port if a.port!=22 else cfg.get('port',22)
    k = a.key or cfg.get('key_file')
    
    if a.save:
        os.makedirs(os.path.dirname(C), exist_ok=True)
        json.dump({'username':u,'hostname':h,'port':pt,'key_file':k}, open(C,'w'), indent=2)
        print(f"Saved: {C}"); return
    
    if not u or not h: print("Error: --user --host required"); sys.exit(1)
    
    cmd = ['ssh']
    if pt!=22: cmd+=['-p',str(pt)]
    if k: cmd+=['-i',os.path.expanduser(k)]
    cmd.append(f'{u}@{h}')
    
    print(f"Connecting: {u}@{h}:{pt}"); subprocess.run(cmd)

if __name__ == '__main__': main()