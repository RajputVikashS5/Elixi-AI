"""
System Monitoring Module
Tracks CPU, RAM, disk usage, network, and temperature
"""

import psutil
import platform
import time
from typing import Dict, List, Optional


class SystemMonitor:
    """Monitors system resources and performance"""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"

    # ========== CPU MONITORING ==========

    def get_cpu_usage(self, interval: float = 1.0, per_cpu: bool = False) -> Dict:
        """
        Get CPU usage percentage
        
        Args:
            interval: Measurement interval in seconds
            per_cpu: Return usage for each CPU core separately
            
        Returns:
            Dict with CPU usage information
        """
        try:
            if per_cpu:
                cpu_percent = psutil.cpu_percent(interval=interval, percpu=True)
                return {
                    "success": True,
                    "cpu_count": len(cpu_percent),
                    "cpu_usage": cpu_percent,
                    "average": sum(cpu_percent) / len(cpu_percent)
                }
            else:
                cpu_percent = psutil.cpu_percent(interval=interval)
                return {
                    "success": True,
                    "cpu_usage": cpu_percent
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_cpu_info(self) -> Dict:
        """
        Get detailed CPU information
        
        Returns:
            Dict with CPU specifications and current state
        """
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_stats = psutil.cpu_stats()
            
            return {
                "success": True,
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None
                },
                "stats": {
                    "ctx_switches": cpu_stats.ctx_switches,
                    "interrupts": cpu_stats.interrupts,
                    "soft_interrupts": cpu_stats.soft_interrupts if hasattr(cpu_stats, 'soft_interrupts') else None,
                    "syscalls": cpu_stats.syscalls if hasattr(cpu_stats, 'syscalls') else None
                },
                "processor": platform.processor()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_cpu_times(self) -> Dict:
        """Get CPU time statistics"""
        try:
            cpu_times = psutil.cpu_times()
            return {
                "success": True,
                "user": cpu_times.user,
                "system": cpu_times.system,
                "idle": cpu_times.idle,
                "interrupt": cpu_times.interrupt if hasattr(cpu_times, 'interrupt') else None,
                "dpc": cpu_times.dpc if hasattr(cpu_times, 'dpc') else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========== MEMORY MONITORING ==========

    def get_memory_usage(self) -> Dict:
        """
        Get RAM usage information
        
        Returns:
            Dict with memory statistics
        """
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "success": True,
                "ram": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "free": memory.free,
                    "percent": memory.percent,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2)
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_gb": round(swap.used / (1024**3), 2)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_top_memory_processes(self, count: int = 10) -> Dict:
        """
        Get processes using the most memory
        
        Args:
            count: Number of top processes to return
            
        Returns:
            Dict with list of top memory-consuming processes
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "memory_mb": proc.info['memory_info'].rss / (1024 * 1024)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            return {
                "success": True,
                "count": len(processes[:count]),
                "processes": processes[:count]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========== DISK MONITORING ==========

    def get_disk_usage(self, path: Optional[str] = None) -> Dict:
        """
        Get disk usage for a specific path or all disks
        
        Args:
            path: Specific path to check (defaults to all partitions)
            
        Returns:
            Dict with disk usage information
        """
        try:
            if path:
                usage = psutil.disk_usage(path)
                return {
                    "success": True,
                    "path": path,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2)
                }
            else:
                partitions = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        partitions.append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent,
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2)
                        })
                    except PermissionError:
                        continue
                
                return {
                    "success": True,
                    "count": len(partitions),
                    "partitions": partitions
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_disk_io(self) -> Dict:
        """Get disk I/O statistics"""
        try:
            io_counters = psutil.disk_io_counters()
            
            if io_counters:
                return {
                    "success": True,
                    "read_count": io_counters.read_count,
                    "write_count": io_counters.write_count,
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes,
                    "read_time": io_counters.read_time,
                    "write_time": io_counters.write_time,
                    "read_mb": round(io_counters.read_bytes / (1024**2), 2),
                    "write_mb": round(io_counters.write_bytes / (1024**2), 2)
                }
            else:
                return {
                    "success": False,
                    "error": "Disk I/O counters not available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========== NETWORK MONITORING ==========

    def get_network_usage(self) -> Dict:
        """Get network I/O statistics"""
        try:
            net_io = psutil.net_io_counters()
            
            return {
                "success": True,
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
                "sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "sent_gb": round(net_io.bytes_sent / (1024**3), 2),
                "recv_gb": round(net_io.bytes_recv / (1024**3), 2)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_network_connections(self, kind: str = 'inet') -> Dict:
        """
        Get active network connections
        
        Args:
            kind: Connection type ('inet', 'inet4', 'inet6', 'tcp', 'udp', 'all')
            
        Returns:
            Dict with list of active connections
        """
        try:
            connections = []
            for conn in psutil.net_connections(kind=kind):
                try:
                    connections.append({
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid
                    })
                except:
                    continue
            
            return {
                "success": True,
                "count": len(connections),
                "connections": connections[:100]  # Limit to 100 connections
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_network_interfaces(self) -> Dict:
        """Get network interface addresses"""
        try:
            interfaces = {}
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in addrs.items():
                interface_info = {
                    "addresses": [],
                    "is_up": stats[interface_name].isup if interface_name in stats else False,
                    "speed": stats[interface_name].speed if interface_name in stats else None
                }
                
                for addr in addresses:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                
                interfaces[interface_name] = interface_info
            
            return {
                "success": True,
                "count": len(interfaces),
                "interfaces": interfaces
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========== TEMPERATURE MONITORING ==========

    def get_temperatures(self) -> Dict:
        """
        Get system temperatures (if available)
        
        Returns:
            Dict with temperature readings
        """
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                
                if not temps:
                    return {
                        "success": False,
                        "error": "No temperature sensors available"
                    }
                
                formatted_temps = {}
                for name, entries in temps.items():
                    formatted_temps[name] = []
                    for entry in entries:
                        formatted_temps[name].append({
                            "label": entry.label or name,
                            "current": entry.current,
                            "high": entry.high,
                            "critical": entry.critical
                        })
                
                return {
                    "success": True,
                    "sensors": formatted_temps
                }
            else:
                return {
                    "success": False,
                    "error": "Temperature monitoring not supported on this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_battery_status(self) -> Dict:
        """Get battery status (for laptops)"""
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                return {
                    "success": False,
                    "error": "No battery detected (desktop system)"
                }
            
            return {
                "success": True,
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "seconds_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                "minutes_left": round(battery.secsleft / 60, 1) if battery.secsleft not in [psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN] else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========== SYSTEM OVERVIEW ==========

    def get_system_overview(self) -> Dict:
        """
        Get comprehensive system overview
        
        Returns:
            Dict with all major system metrics
        """
        try:
            cpu_usage = self.get_cpu_usage()
            memory = self.get_memory_usage()
            disk = self.get_disk_usage()
            network = self.get_network_usage()
            
            boot_time = psutil.boot_time()
            uptime_seconds = int(time.time() - boot_time)
            
            return {
                "success": True,
                "timestamp": time.time(),
                "system": {
                    "platform": platform.system(),
                    "platform_release": platform.release(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "processor": platform.processor(),
                    "hostname": platform.node(),
                    "boot_time": boot_time,
                    "uptime_seconds": uptime_seconds,
                    "uptime_hours": round(uptime_seconds / 3600, 1)
                },
                "cpu": {
                    "usage_percent": cpu_usage.get("cpu_usage", 0),
                    "physical_cores": psutil.cpu_count(logical=False),
                    "logical_cores": psutil.cpu_count(logical=True)
                },
                "memory": memory.get("ram", {}),
                "disk": disk.get("partitions", []) if "partitions" in disk else disk,
                "network": {
                    "sent_mb": network.get("sent_mb", 0),
                    "recv_mb": network.get("recv_mb", 0)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_process_count(self) -> Dict:
        """Get count of running processes"""
        try:
            process_count = len(psutil.pids())
            return {
                "success": True,
                "process_count": process_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
