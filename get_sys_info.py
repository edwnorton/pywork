import psutil
from multiprocessing import cpu_count
from decimal import Decimal, ROUND_HALF_UP


def get_sys_info():
    pc_mem = psutil.virtual_memory()
    div_gb_factor = (1024.0 ** 3)
    sys_info = {}
    disk_free = {}
    mem_tmp = Decimal(float(pc_mem.total / div_gb_factor))
    mem = mem_tmp.quantize(Decimal('0.0'), rounding=ROUND_HALF_UP)
    for id in psutil.disk_partitions():
        if 'cdrom' in id.opts or id.fstype == '':
            continue
        disk_name = id.device.split(':')
        s = disk_name[0]
        disk_info = psutil.disk_usage(id.device)
        disk_free[s] = '{}GB'.format(disk_info.free // 1024 // 1024 // 1024)
    sys_info['cpu'] = cpu_count()
    sys_info['mem_info'] = int(mem)
    sys_info['disk'] = disk_free
    return sys_info


sys_info = get_sys_info()
print(sys_info)
