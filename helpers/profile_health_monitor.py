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
    
        # Main monitoring loop
        while not stop_event.is_set():
            try:
                # ========== CHECK 1: PAUSE EVENT ==========
                if pause_event and pause_event.is_set():
                    # Monitoring paused (e.g., during crashed tab fix)
                    # print(f"{log_prefix} [{profile_id}] ⏸ Monitoring paused")
                    time.sleep(check_interval)
                    continue
        
                # ========== CHECK 2: DRIVER HEALTH (NO PAGE LOAD BLOCKING) ==========
                try:
                    # Check window handles (fast, no page load wait)
                    handles = driver.window_handles
            
                    # If we can get handles, driver is alive
                    if handles and len(handles) > 0:
                        # Driver alive, reset failure counter
                        consecutive_failures = 0
                        # print(f"{log_prefix} [{profile_id}] ✓ Driver alive ({len(handles)} tabs)")
                    else:
                        # No handles = browser closed
                        raise Exception("No window handles found")
        
                except Exception as health_error:
                    # Driver check failed
                    consecutive_failures += 1
                    print(f"{log_prefix} [{profile_id}] ⚠ Health check failed ({consecutive_failures}/{max_failures}): {health_error}")
            
                    # If max failures reached, force release lock
                    if consecutive_failures >= max_failures:
                        print(f"{log_prefix} [{profile_id}] ❌ Profile closed/crashed, force releasing lock")
                
                        # Call callback to force release lock
                        if callback_on_close:
                            try:
                                callback_on_close()
                            except Exception as callback_error:
                                print(f"{log_prefix} [{profile_id}] Callback error: {callback_error}")
                
                        # Stop monitoring
                        break
        
                # Sleep before next check
                time.sleep(check_interval)
    
            except Exception as loop_error:
                print(f"{log_prefix} [{profile_id}] Loop error: {loop_error}")
                time.sleep(check_interval)

        # Cleanup
        print(f"{log_prefix} [{profile_id}] Monitor stopped")



    
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
