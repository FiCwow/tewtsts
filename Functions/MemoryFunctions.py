# Functions/MemoryFunctions.py
import ctypes as c
from Addresses import process_handle, base_address, config

def read_memory(address: int, size: int):
    buffer = (c.c_byte * size)()
    bytes_read = c.c_size_t()
    if c.windll.kernel32.ReadProcessMemory(process_handle, c.c_void_p(address), buffer, size, c.byref(bytes_read)):
        return bytes(buffer)[:bytes_read.value]
    return None

def calculate_address(entry: dict) -> int:
    addr = base_address
    if "base" in entry:
        addr = int(entry["base"], 16)
    if "offset" in entry:
        for offset in (entry["offset"] if isinstance(entry["offset"], list) else [entry["offset"]]):
            data = read_memory(addr, 4)
            if not data: return 0
            addr = int.from_bytes(data, "little") + offset
    return addr

def read_int(entry: dict) -> int:
    addr = calculate_address(entry)
    data = read_memory(addr, 4)
    return int.from_bytes(data, "little") if data else 0

def read_short(entry: dict) -> int:
    addr = calculate_address(entry)
    data = read_memory(addr, 2)
    return int.from_bytes(data, "little") if data else 0

def read_byte(entry: dict) -> int:
    addr = calculate_address(entry)
    data = read_memory(addr, 1)
    return data[0] if data else 0

def read_string(entry: dict, length: int = 32) -> str:
    addr = calculate_address(entry)
    data = read_memory(addr, length)
    if not data: return ""
    try:
        return data.split(b'\x00')[0].decode('utf-8', errors='ignore')
    except:
        return ""