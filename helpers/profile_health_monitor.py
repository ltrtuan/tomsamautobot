# helpers/profile_health_monitor.py

"""
Profile Health Monitor - Detect when profile closes/crashes and force release action lock

FEATURES:
- Monitor profile health (driver alive, window exists)
- Pause monitoring temporarily (during crashed tab fix)
- Resume monitoring after fix
"""

import threading
import time

class ProfileHealthMonitor:
    """Monitor profile health and force release lock if profile closes"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.active_monitors = {}
        self.stop_events = {}
        self.dict_lock = threading.Lock()
        
        # NEW: Pause events for each monitor (to pause during crashed tab fix)
        self.pause_events = {}  # profile_id → Event (set = paused)
        
        self._initialized = True
        print("[HEALTH MONITOR] ✓ Initialized")
    
    def start_monitoring(self, profile_id, driver, debugger_address, callback_on_close, log_prefix="[MONITOR]"):
        """Start monitoring a profile"""
        with self.dict_lock:
            if profile_id in self.active_monitors:
                self.stop_monitoring(profile_id)
            
            stop_event = threading.Event()
            self.stop_events[profile_id] = stop_event
            
            # NEW: Create pause event (not set initially = not paused)
            pause_event = threading.Event()
            self.pause_events[profile_id] = pause_event
            
            monitor_thread = threading.Thread(
                target=self._monitor_loop,
                args=(profile_id, driver, debugger_address, callback_on_close, stop_event, pause_event, log_prefix),
                daemon=True,
                name=f"HealthMonitor-{profile_id[:8]}"
            )
            
            self.active_monitors[profile_id] = monitor_thread
            monitor_thread.start()
            
            print(f"{log_prefix} [{profile_id}] ✓ Health monitoring started")
    
    def pause_monitoring(self, profile_id):
        """
        Pause monitoring temporarily (e.g., during crashed tab fix)
        
        Args:
            profile_id: Profile ID to pause monitoring
        """
        with self.dict_lock:
            if profile_id in self.pause_events:
                self.pause_events[profile_id].set()  # Set = paused
                print(f"[HEALTH MONITOR] [{profile_id}] ⏸️ Monitoring paused")
    
    def resume_monitoring(self, profile_id):
        """
        Resume monitoring after pause
        
        Args:
            profile_id: Profile ID to resume monitoring
        """
        with self.dict_lock:
            if profile_id in self.pause_events:
                self.pause_events[profile_id].clear()  # Clear = resumed
                print(f"[HEALTH MONITOR] [{profile_id}] ▶️ Monitoring resumed")
    
    def stop_monitoring(self, profile_id):
        """Stop monitoring a profile"""
        with self.dict_lock:
            if profile_id in self.stop_events:
                self.stop_events[profile_id].set()
                
                if profile_id in self.active_monitors:
                    self.active_monitors[profile_id].join(timeout=2)
                
                # Cleanup
                del self.stop_events[profile_id]
                if profile_id in self.active_monitors:
                    del self.active_monitors[profile_id]
                if profile_id in self.pause_events:
                    del self.pause_events[profile_id]
                
                print(f"[HEALTH MONITOR] [{profile_id}] Monitoring stopped")
                
    
    def _monitor_loop(self, profile_id, driver, debugger_address, callback_on_close, stop_event, pause_event, log_prefix):
        """
        Background thread monitoring profile health
    
        Loop:
        1. Check if should pause (crashed tab fix in progress)
        2. Check driver health (alive, window exists)
        3. If dead → force release lock → exit
        4. Sleep and repeat
    
        Args:
            profile_id: Profile ID to monitor
            driver: Selenium WebDriver instance
            debugger_address: Chrome debugger address (not used in current impl)
            callback_on_close: Callback để force release lock
            stop_event: Event để stop monitoring
            pause_event: Event để pause monitoring
            log_prefix: Prefix cho log messages
        """
        check_interval = 2  # Check mỗi 2 giây
        consecutive_failures = 0
        max_failures = 3  # Failed 3 lần liên tiếp mới force release
    
        print(f"{log_prefix} [{profile_id}] 🔍 Monitoring started (check every {check_interval}s)")
    
        while not stop_event.is_set():
            try:
                # ========== CHECK 1: PAUSE EVENT ==========
                # Nếu đang pause (fixing crashed tab), skip health check
                if pause_event.is_set():
                    # print(f"{log_prefix} [{profile_id}] ⏸ Monitoring paused")
                    time.sleep(check_interval)
                    continue
            
                # ========== CHECK 2: DRIVER HEALTH ==========
                try:
                    # Test 1: Driver có còn alive không
                    _ = driver.current_url
                
                    # Test 2: Window có tồn tại không
                    _ = driver.window_handles
                
                    # Health check passed
                    consecutive_failures = 0
                    # print(f"{log_prefix} [{profile_id}] ✓ Health check passed")
                
                except Exception as health_error:
                    consecutive_failures += 1
                    print(f"{log_prefix} [{profile_id}] ⚠ Health check failed ({consecutive_failures}/{max_failures}): {health_error}")
                
                    # ========== TRIGGER FORCE RELEASE ==========
                    if consecutive_failures >= max_failures:
                        print(f"{log_prefix} [{profile_id}] ❌ PROFILE DEAD - Forcing lock release")
                    
                        # Call force release callback
                        try:
                            callback_on_close()
                            print(f"{log_prefix} [{profile_id}] ✓ Lock force released")
                        except Exception as release_error:
                            print(f"{log_prefix} [{profile_id}] ✗ Failed to force release: {release_error}")
                    
                        # Exit monitoring loop
                        print(f"{log_prefix} [{profile_id}] 🛑 Monitoring stopped (profile dead)")
                        break
            
                # Sleep before next check
                time.sleep(check_interval)
            
            except Exception as e:
                print(f"{log_prefix} [{profile_id}] ✗ Monitoring error: {e}")
                time.sleep(check_interval)
    
        # Cleanup khi exit
        print(f"{log_prefix} [{profile_id}] 🛑 Monitoring thread exiting")
        with self.dict_lock:
            if profile_id in self.active_monitors:
                del self.active_monitors[profile_id]
            if profile_id in self.stop_events:
                del self.stop_events[profile_id]
            if profile_id in self.pause_events:
                del self.pause_events[profile_id]


    
    def _check_profile_alive(self, driver, debugger_address, profile_id, log_prefix):
        """Check if profile is still alive"""
        try:
            # CHECK 1: JavaScript execution
            try:
                result = driver.execute_script("return 1;")
                if result != 1:
                    return False
            except Exception:
                return False
            
            # CHECK 2: Window handles exist
            try:
                handles = driver.window_handles
                if not handles or len(handles) == 0:
                    return False
            except Exception:
                return False
            
            # CHECK 3: DevTools API responds
            try:
                import requests
                response = requests.get(f"http://{debugger_address}/json", timeout=2)
                if response.status_code != 200:
                    return False
            except:
                return False
            
            return True
            
        except Exception:
            return False


_health_monitor = ProfileHealthMonitor()

def get_health_monitor():
    """Get the global ProfileHealthMonitor instance"""
    return _health_monitor
