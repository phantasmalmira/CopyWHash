import hashlib
import os
import json
import time
import argparse
import shutil
from pathlib import Path

def md5sum(filename, blocksize=65536):
    print('Hashing: {}'.format(filename))
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

def hashrecursively(pathname, oripath=None):
    ls = os.listdir(pathname)
    if not oripath:
        oripath = pathname
    files = []
    dirs = []
    for item in ls:
        if os.path.isfile("{}/{}".format(pathname, item)):
            if not (item.endswith(".png") or item.endswith(".dmp") or item.endswith(".LOG")):
                files.append("{}/{}".format(pathname, item))
        else:
            dirs.append("{}/{}".format(pathname, item))

    hashmap = {}
    # recursive call myself
    for _dir in dirs:
        r_hashmap = hashrecursively(_dir, oripath)
        hashmap.update(r_hashmap)
    
    for _file in files:
        _t_file = _file.replace(oripath, '.')
        hashmap[_t_file] = md5sum(_file)

    return hashmap

def sendmode(path):
    start = time.time()
    hashmap = hashrecursively(path)
    end = time.time()
    print('Completed hashing in {}s'.format('%.2f'%(end-start)))
    with open('{}/{}'.format(path, 'hashdump.json'), 'w') as f:
        f.write(json.dumps(hashmap))

def receivemode(src, dst):
    if os.path.isfile('{}/{}'.format(src, 'hashdump.json')):
        hashmap = {}
        plus = []
        minus = []
        modified = []
        unmodified = []
        with open('{}/{}'.format(src, 'hashdump.json'), 'r') as f:
            hashmap = json.load(f)

        if not os.path.isfile('{}/{}'.format(dst, 'hashdump.json')):
            print('HASHING DEST...')
            dst_hashmap = hashrecursively(dst)
            with open('{}/{}'.format(dst, 'hashdump.json'), 'w') as f:
                f.write(json.dumps(dst_hashmap))
        else:
            with open('{}/{}'.format(dst, 'hashdump.json'), 'r') as f: 
                dst_hashmap = json.load(f)



        for s_key, s_value in hashmap.items():
            if not s_key in dst_hashmap: # Destination has no file
                plus.append(s_key)
            elif s_key in dst_hashmap and (dst_hashmap[s_key] != s_value): # Destination has file, but hash is different
                modified.append(s_key)
            else:
                unmodified.append(s_key)
        
        # Minuses
        for d_key, d_value in dst_hashmap.items():
            if not d_key in hashmap:
                minus.append(d_key)

        # Print Unmodified
        print('\n\nUNMODIFIED==============<')
        for _u in unmodified:
            print(_u)

        # Print Pluses
        print('\n\nPLUS====================<')
        for _p in plus:
            print(_p)

        # Print Minuses
        print('\n\nMINUS===================<')
        for _m in minus:
            print(_m)

        # Print Modified
        print('\n\nMODIFIED================<')
        for _m in modified:
            print('{}\t\t\t({})=>({})'.format(_m, dst_hashmap[_m], hashmap[_m]))
        print('\n\n')
        apply_changes(src, dst, plus, minus, modified)

def apply_changes(src, dest, plus, minus, modified):
    prompt = input('Apply changes? (Y/N)')
    if(prompt.upper().startswith('Y')):
        dprompt = input('Are you really sure to apply changes? (Y/N)')
        if(dprompt.upper().startswith('Y')):
            apply_plus(src, dest, plus) #Apply the plusses
            apply_minus(dest, minus)
            apply_modified(src, dest, modified)
        
def apply_plus(src, dest, plus):
    for _i in plus:
        _dir = '{}/{}'.format(dest, _i)
        _dir = _dir[:_dir.rindex('/')]
        Path(_dir).mkdir(parents=True, exist_ok=True)
        print('Adding {}/{} to {}/{}'.format(src, _i, dest, _i))
        shutil.copyfile('{}/{}'.format(src, _i), '{}/{}'.format(dest, _i))

def apply_minus(dest, minus):
    for _i in minus:
        print('Removing {}/{}'.format(dest, _i))
        os.remove('{}/{}'.format(dest, _i))

def apply_modified(src, dest, modified):
    for _i in modified:
        print('Overwriting {}/{} to {}/{}'.format(src, _i, dest, _i))
        shutil.copyfile('{}/{}'.format(src, _i), '{}/{}'.format(dest, _i))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode',
                        metavar=('SEND/RECEIVE'),
                        help='*Specify run mode, generate delta hash snapshot in send, compare delta hash snapshot in receive')
    parser.add_argument('-s', '--src',
                        metavar=('PATH'),
                        help='*Specify path to hash recursively in send mode, specify path to delta hash snapshot in receive')
    parser.add_argument('-d', '--dst',
                        metavar=('PATH'),
                        help='Specify path to destination, only required in receiving mode')
    args = parser.parse_args()


    if not args.mode or not args.src:
        print('Run the script with -h for help info.')
        exit(1)

    if not os.path.exists(args.src):
        print('SRC is invalid')
        exit(1)

    if args.mode.upper() == 'SEND' or args.mode.upper().startswith('S'):
        print('Sending mode')
        sendmode(args.src)

    elif args.mode.upper() == 'RECEIVE' or args.mode.upper().startswith('R'):
        if not args.dst or (args.dst and not os.path.exists(args.dst)):
            print('DST is invalid')
        print("Receiving mode")
        receivemode(args.src, args.dst)

