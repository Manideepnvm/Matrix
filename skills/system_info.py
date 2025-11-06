# skills/system_info.py

import psutil
import platform
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict
import cpuinfo

from core.logger import log_info, log_error, log_warning, log_debug


class SystemInfo:
    """Enhanced system information retrieval with detailed metrics"""
    
    def __init__(self):
        self.platform = platform.system()
        self.hostname = socket.gethostname()
        
        # Cache for frequent queries
        self._cache = {}
        self._cache_timeout = 5  # seconds
        self._last_update = {}
        
        log_info("System Info initialized")
    
    def _should_update_cache(self, key: str) -> bool:
        """Check if cache should be updated"""
        if key not in self._last_update:
            return True
        
        elapsed = (datetime.now() - self._last_update[key]).total_seconds()
        return elapsed > self._cache_timeout
    
    def get_battery_status(self) -> Optional[Dict]:
        """
        Get battery status information
        
        Returns:
            Dictionary with battery info or None if not available
        """
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                log_warning("Battery information not available")
                return None
            
            status = {
                'percent': int(battery.percent),
                'plugged': bool(battery.power_plugged),
                'time_left': None,
                'status_text': ''
            }
            
            # Calculate time remaining
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                time_left = timedelta(seconds=battery.secsleft)
                hours = time_left.seconds // 3600
                minutes = (time_left.seconds % 3600) // 60
                status['time_left'] = f"{hours}h {minutes}m"
            
            # Status text
            if status['plugged']:
                if status['percent'] == 100:
                    status['status_text'] = "fully charged"
                else:
                    status['status_text'] = "charging"
            else:
                status['status_text'] = "on battery"
            
            log_debug(f"Battery status: {status}")
            return status
            
        except Exception as e:
            log_error(f"Error getting battery status: {e}")
            return None
    
    def get_cpu_info(self) -> Dict:
        """Get CPU information"""
        try:
            if self._should_update_cache('cpu'):
                cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
                cpu_freq = psutil.cpu_freq()
                
                info = {
                    'usage_percent': cpu_percent,
                    'count_physical': psutil.cpu_count(logical=False),
                    'count_logical': psutil.cpu_count(logical=True),
                    'frequency_current': cpu_freq.current if cpu_freq else 0,
                    'frequency_max': cpu_freq.max if cpu_freq else 0,
                }
                
                # Try to get CPU name
                try:
                    cpu_info_dict = cpuinfo.get_cpu_info()
                    info['name'] = cpu_info_dict.get('brand_raw', 'Unknown')
                except:
                    info['name'] = platform.processor()
                
                self._cache['cpu'] = info
                self._last_update['cpu'] = datetime.now()
            
            return self._cache.get('cpu', {})
            
        except Exception as e:
            log_error(f"Error getting CPU info: {e}")
            return {}
    
    def get_memory_info(self) -> Dict:
        """Get memory (RAM) information"""
        try:
            if self._should_update_cache('memory'):
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                
                info = {
                    'total': mem.total,
                    'available': mem.available,
                    'used': mem.used,
                    'percent': mem.percent,
                    'total_gb': round(mem.total / (1024**3), 2),
                    'available_gb': round(mem.available / (1024**3), 2),
                    'used_gb': round(mem.used / (1024**3), 2),
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percent': swap.percent
                }
                
                self._cache['memory'] = info
                self._last_update['memory'] = datetime.now()
            
            return self._cache.get('memory', {})
            
        except Exception as e:
            log_error(f"Error getting memory info: {e}")
            return {}
    
    def get_disk_info(self) -> Dict:
        """Get disk usage information"""
        try:
            partitions = psutil.disk_partitions()
            disk_info = {}
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2)
                    }
                except PermissionError:
                    continue
            
            return disk_info
            
        except Exception as e:
            log_error(f"Error getting disk info: {e}")
            return {}
    
    def get_network_info(self) -> Dict:
        """Get network information"""
        try:
            # Network interfaces
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io = psutil.net_io_counters()
            
            info = {
                'hostname': self.hostname,
                'interfaces': {},
                'bytes_sent': io.bytes_sent,
                'bytes_recv': io.bytes_recv,
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv
            }
            
            # Get IP addresses
            for interface, addr_list in addrs.items():
                if interface in stats and stats[interface].isup:
                    for addr in addr_list:
                        if addr.family == socket.AF_INET:
                            info['interfaces'][interface] = {
                                'ip': addr.address,
                                'netmask': addr.netmask,
                                'is_up': stats[interface].isup
                            }
            
            return info
            
        except Exception as e:
            log_error(f"Error getting network info: {e}")
            return {}
    
    def get_system_uptime(self) -> Dict:
        """Get system uptime"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            return {
                'boot_time': boot_time.isoformat(),
                'uptime_seconds': uptime.total_seconds(),
                'uptime_text': f"{days}d {hours}h {minutes}m"
            }
            
        except Exception as e:
            log_error(f"Error getting uptime: {e}")
            return {}
    
    def get_temperature(self) -> Optional[Dict]:
        """Get system temperature (if available)"""
        try:
            temps = psutil.sensors_temperatures()
            
            if not temps:
                return None
            
            temp_info = {}
            for name, entries in temps.items():
                for entry in entries:
                    temp_info[f"{name}_{entry.label}"] = {
                        'current': entry.current,
                        'high': entry.high,
                        'critical': entry.critical
                    }
            
            return temp_info
            
        except Exception as e:
            log_error(f"Error getting temperature: {e}")
            return None
    
    def get_full_system_info(self) -> Dict:
        """Get comprehensive system information"""
        try:
            info = {
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor(),
                    'hostname': self.hostname
                },
                'battery': self.get_battery_status(),
                'cpu': self.get_cpu_info(),
                'memory': self.get_memory_info(),
                'disk': self.get_disk_info(),
                'network': self.get_network_info(),
                'uptime': self.get_system_uptime(),
                'temperature': self.get_temperature()
            }
            
            return info
            
        except Exception as e:
            log_error(f"Error getting full system info: {e}")
            return {}


# Global system info instance
_system_info: Optional[SystemInfo] = None


def get_system_info() -> SystemInfo:
    """Get or create global system info instance"""
    global _system_info
    if _system_info is None:
        _system_info = SystemInfo()
    return _system_info


def get_matrix_speech():
    """Get Matrix speech engine"""
    try:
        from core.speech import SpeechEngine
        return SpeechEngine()
    except:
        return None


# Convenience functions with voice feedback
def get_battery_status():
    """Speak battery status"""
    sysinfo = get_system_info()
    speech = get_matrix_speech()
    
    try:
        battery = sysinfo.get_battery_status()
        
        if battery is None:
            if speech:
                speech.speak("Battery information is not available on this system.")
            log_warning("Battery info not available")
            return None
        
        percent = battery['percent']
        status = battery['status_text']
        time_left = battery.get('time_left')
        
        # Generate speech text
        if time_left:
            message = f"Battery is at {percent} percent, {status}, with approximately {time_left} remaining."
        else:
            message = f"Battery is at {percent} percent and is {status}."
        
        if speech:
            speech.speak(message)
        
        log_info(f"Battery: {percent}% - {status}")
        return battery
        
    except Exception as e:
        log_error(f"Error in get_battery_status: {e}")
        if speech:
            speech.speak("Error retrieving battery status.")
        return None


def get_cpu_usage():
    """Speak CPU usage"""
    sysinfo = get_system_info()
    speech = get_matrix_speech()
    
    try:
        cpu = sysinfo.get_cpu_info()
        
        if not cpu:
            if speech:
                speech.speak("Could not get CPU information")
            return None
        
        usage = cpu.get('usage_percent', 0)
        cores = cpu.get('count_logical', 0)
        
        message = f"CPU usage is at {int(usage)} percent across {cores} cores."
        
        if speech:
            speech.speak(message)
        
        log_info(f"CPU: {usage}% usage")
        return cpu
        
    except Exception as e:
        log_error(f"Error in get_cpu_usage: {e}")
        if speech:
            speech.speak("Error getting CPU information")
        return None


def get_memory_usage():
    """Speak memory usage"""
    sysinfo = get_system_info()
    speech = get_matrix_speech()
    
    try:
        memory = sysinfo.get_memory_info()
        
        if not memory:
            if speech:
                speech.speak("Could not get memory information")
            return None
        
        used_gb = memory.get('used_gb', 0)
        total_gb = memory.get('total_gb', 0)
        percent = memory.get('percent', 0)
        
        message = f"Using {used_gb:.1f} gigabytes out of {total_gb:.1f} gigabytes. That's {int(percent)} percent."
        
        if speech:
            speech.speak(message)
        
        log_info(f"Memory: {percent}% used ({used_gb:.1f}GB / {total_gb:.1f}GB)")
        return memory
        
    except Exception as e:
        log_error(f"Error in get_memory_usage: {e}")
        if speech:
            speech.speak("Error getting memory information")
        return None


def get_disk_usage():
    """Speak disk usage"""
    sysinfo = get_system_info()
    speech = get_matrix_speech()
    
    try:
        disks = sysinfo.get_disk_info()
        
        if not disks:
            if speech:
                speech.speak("Could not get disk information")
            return None
        
        # Report primary disk (usually C: or /)
        primary_disk = None
        for device, info in disks.items():
            mountpoint = info.get('mountpoint', '')
            if mountpoint in ['/', 'C:\\']:
                primary_disk = info
                break
        
        if not primary_disk and disks:
            primary_disk = list(disks.values())[0]
        
        if primary_disk:
            free_gb = primary_disk.get('free_gb', 0)
            total_gb = primary_disk.get('total_gb', 0)
            percent = primary_disk.get('percent', 0)
            
            message = f"Disk is {int(percent)} percent full. {free_gb:.1f} gigabytes free out of {total_gb:.1f} gigabytes total."
            
            if speech:
                speech.speak(message)
            
            log_info(f"Disk: {percent}% used ({free_gb:.1f}GB free)")
        
        return disks
        
    except Exception as e:
        log_error(f"Error in get_disk_usage: {e}")
        if speech:
            speech.speak("Error getting disk information")
        return None


def get_system_uptime():
    """Speak system uptime"""
    sysinfo = get_system_info()
    speech = get_matrix_speech()
    
    try:
        uptime = sysinfo.get_system_uptime()
        
        if not uptime:
            if speech:
                speech.speak("Could not get uptime information")
            return None
        
        uptime_text = uptime.get('uptime_text', 'unknown')
        
        message = f"System has been running for {uptime_text}."
        
        if speech:
            speech.speak(message)
        
        log_info(f"Uptime: {uptime_text}")
        return uptime
        
    except Exception as e:
        log_error(f"Error in get_system_uptime: {e}")
        if speech:
            speech.speak("Error getting uptime")
        return None


def get_full_status():
    """Speak comprehensive system status"""
    speech = get_matrix_speech()
    
    try:
        if speech:
            speech.speak("Gathering system information.")
        
        # Get all info
        battery = get_battery_status()
        cpu = get_cpu_usage()
        memory = get_memory_usage()
        
        log_info("Full system status reported")
        
    except Exception as e:
        log_error(f"Error in get_full_status: {e}")
        if speech:
            speech.speak("Error getting system status")