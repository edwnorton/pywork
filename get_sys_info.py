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
        disk_free[s] = int('{}'.format(disk_info.free // 1024 // 1024 // 1024))
    sys_info['cpu'] = cpu_count()
    sys_info['mem_info'] = int(mem)
    sys_info['disk'] = disk_free
    return sys_info


def plot_sys_utilize():
    sys_info = get_sys_info()
    plot_utilize = {}
    mem_use = 3.4 # 内存占用(G) k32
    cache_use = 250 # plot缓存占用(G)
    cpu_use = 2 # cpu线程占用
    disk_plot_sum = 0
    plot_utilize['mem_p_num'] = int(sys_info['mem_info']/mem_use)
    plot_utilize['cpu_p_num'] = int(sys_info['cpu']/cpu_use)
    plot_utilize['disk'] = {}
    for i in sys_info['disk']:
        plot_utilize['disk'][i] = int(sys_info['disk'][i]/cache_use)
        disk_plot_sum = disk_plot_sum + plot_utilize['disk'][i]
    plot_utilize['disk_total'] = disk_plot_sum
    plot_max = sorted([plot_utilize['mem_p_num'], plot_utilize['cpu_p_num'], plot_utilize['disk_total']])
    plot_utilize['totalPlotNum'] = plot_max[0] # 根据plot过程中的资源瓶颈限制，计算做多可以plot几个文件
    return plot_utilize

a = plot_sys_utilize()
print (a)
