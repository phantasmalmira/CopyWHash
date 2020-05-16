# CopyWHash
Python to copy files that are actually changed with MD5.

Currently, it supports
- Added files in source (PLUS)
- Removed files in source (MINUS)
- Modified files in source (MODIFIED)

# Requirements
Python >= 3.5

# How to use (This is a two step process)

### Send
1. Generate a MD5 hash snapshot of the source
```
py CopyWithHash.py --mode SEND --src SRCPATH
```
2. MD5 hash snapshot `hashdump.json` is created at `SRCPATH`

### Receive
1. Compare the MD5 hash snapshot of the source with destination
```
py CopyWithHash.py --mode RECEIVE --src SRCPATH --dst DSTPATH
```
2. Review changes to be applied
3. Confirm changes


# Bugs
There are probably many, since no thorough test are done.
