import psutil

class SystemMonitor:
    def __init__(self):
        pass

    @staticmethod
    def collect_data():

        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        hdd = psutil.disk_usage('/').percent
        return cpu, ram, hdd

