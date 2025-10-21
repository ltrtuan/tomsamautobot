# helpers/action_chain_manager.py

"""
Action Chain Manager - Centralized lock management for physical actions

FEATURES:
1. Single global lock for physical actions (mouse, keyboard)
2. Profile health monitoring during chain execution
3. Force release lock when profile closes/crashes
4. Smart waiting with bring-to-front for next profile

WORKFLOW:
- Profile A: acquire lock → start monitor → execute chain → release lock → stop monitor
- Profile B: wait for lock → (if A closes → A force releases) → bring to front → acquire lock → execute
"""

import threading
import time
import random

# Import health monitor
from helpers.profile_health_monitor import get_health_monitor

class ActionChainManager:
    """
    Manages action chains with global lock to prevent profile interference
    Only one profile can execute physical action chains at a time
    
    NEW FEATURES:
    - Health monitoring: Detect when profile closes during execution
    - Force release: Release lock immediately when profile closes
    - Smart waiting: Next profile brings itself to front if previous closed
    """
    
    # ==================== GLOBAL LOCK ====================
    # This lock ensures only ONE profile can perform physical actions (mouse/keyboard) at a time
    physical_action_lock = threading.Lock()
    
    # ==================== PROFILE TRACKING ====================
    active_profile = None  # Currently executing profile ID
    lock_start_time = None  # When current profile acquired lock
    
    # NEW: Track which profile currently holds the lock (for health monitoring)
    current_holder = None  # profile_id of current lock holder
    holder_lock = threading.Lock()  # Lock to safely access current_holder
    
    # NEW: Track profiles that have closed/crashed
    closed_profiles = set()  # Set of profile_ids that closed abnormally
    closed_lock = threading.Lock()  # Lock to safely access closed_profiles
    
   
    @staticmethod
    def execute_chain(profile_id, chain_function, *args, **kwargs):
        """
        Execute một action chain với global lock (BLOCKING)
    
        Args:
            profile_id: Profile ID
            chain_function: Chain function để execute
            *args: Arguments (expected: driver, keyword, profile_id, debugger_address, log_prefix)
            **kwargs: Keyword arguments
        """
        manager = ActionChainManager()
        log_prefix = f"[CHAIN MANAGER][{profile_id}]"
    
        # ========== DECLARE VARIABLES OUTSIDE TRY BLOCK ==========
        lock_acquired = False
        driver = None
        debugger_address = None
        health_monitor = None
    
        print(f"\n{log_prefix} ========================================")
        print(f"{log_prefix} REQUESTING ACTION LOCK")
        print(f"{log_prefix} ========================================")
    
        try:
            # ========== STEP 1: ACQUIRE LOCK (BLOCKING) ==========
            wait_start = time.time()
        
            while not manager.acquire_lock(profile_id):
                elapsed = time.time() - wait_start
            
                # Log mỗi 5 giây
                if int(elapsed) % 5 == 0 and elapsed > 0:
                    current_holder = manager.current_lock_holder
                    print(f"{log_prefix} ⏳ Waiting for lock... (waited {elapsed:.1f}s, current holder: {current_holder})")
            
                time.sleep(0.5)
            
                # Safety timeout (5 phút)
                if elapsed > 300:
                    print(f"{log_prefix} ✗ TIMEOUT waiting for lock after {elapsed:.1f}s")
                    return False
        
            lock_acquired = True
            wait_time = time.time() - wait_start
            print(f"{log_prefix} ✓ LOCK ACQUIRED (waited {wait_time:.1f}s)")
        
            # ========== STEP 2: START HEALTH MONITORING ==========
            health_monitor = get_health_monitor()
        
            # Extract driver và debugger_address từ args
            # Expected args: (driver, keyword, profile_id, debugger_address, log_prefix)
            if args and hasattr(args[0], 'quit'):
                driver = args[0]
        
            if len(args) > 3:
                debugger_address = args[3]
        
            if driver and debugger_address:
                # Tạo callback cho health monitor
                def on_profile_close():
                    print(f"{log_prefix} 🚨 Profile closed detected, force releasing lock")
                    manager.force_release_lock(profile_id)
            
                health_monitor.start_monitoring(
                    profile_id, 
                    driver, 
                    debugger_address,
                    on_profile_close,
                    log_prefix=log_prefix
                )
                print(f"{log_prefix} ✓ Health monitoring started")
            else:
                print(f"{log_prefix} ⚠ No driver/debugger found, health monitoring skipped")
        
            # ========== STEP 3: VERIFY WINDOW FOCUS ==========
            if driver:
                try:
                    print(f"{log_prefix} Verifying window focus...")
                    driver.switch_to.window(driver.current_window_handle)
                
                    try:
                        driver.maximize_window()
                        print(f"{log_prefix}   ✓ Window maximized")
                    except Exception as e:
                        print(f"{log_prefix}   ⚠ Could not maximize: {e}")
                
                    time.sleep(0.5)
                    print(f"{log_prefix} ✓ Window focus verified")
                
                except Exception as e:
                    print(f"{log_prefix} ⚠ Window focus verification failed: {e}")
        
            # ========== STEP 4: EXECUTE CHAIN ==========
            result = False
            execution_start = time.time()
        
            try:
                print(f"\n{log_prefix} ========================================")
                print(f"{log_prefix} EXECUTING CHAIN")
                print(f"{log_prefix} ========================================\n")
            
                result = chain_function(*args, **kwargs)
            
                execution_time = time.time() - execution_start
            
                if result:
                    print(f"\n{log_prefix} ========================================")
                    print(f"{log_prefix} ✓ CHAIN COMPLETED ({execution_time:.1f}s)")
                    print(f"{log_prefix} ========================================")
                else:
                    print(f"\n{log_prefix} ========================================")
                    print(f"{log_prefix} ✗ CHAIN FAILED ({execution_time:.1f}s)")
                    print(f"{log_prefix} ========================================")
            
            except Exception as e:
                execution_time = time.time() - execution_start
                print(f"\n{log_prefix} ========================================")
                print(f"{log_prefix} ✗ CHAIN EXCEPTION ({execution_time:.1f}s)")
                print(f"{log_prefix} Error: {e}")
                print(f"{log_prefix} ========================================")
                import traceback
                traceback.print_exc()
                result = False
        
            return result
        
        except Exception as outer_e:
            print(f"{log_prefix} ✗ CRITICAL ERROR in execute_chain: {outer_e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # ========== CLEANUP: ALWAYS EXECUTE ==========
            # Stop health monitoring
            if driver and health_monitor:
                try:
                    health_monitor.stop_monitoring(profile_id)
                    print(f"{log_prefix} ✓ Health monitoring stopped")
                except Exception as e:
                    print(f"{log_prefix} ⚠ Error stopping health monitoring: {e}")
        
            # Release lock
            if lock_acquired:
                try:
                    manager.release_lock(profile_id)
                    print(f"{log_prefix} ✓ LOCK RELEASED")
                except Exception as e:
                    print(f"{log_prefix} ✗ Error releasing lock: {e}")
        
            print(f"{log_prefix} ========================================\n")


    
    # ==================== LOCK MANAGEMENT METHODS ====================

    def acquire_lock(self, profile_id):
        """
        Acquire physical action lock
    
        Args:
            profile_id: Profile ID requesting lock
    
        Returns:
            bool: True nếu acquire thành công, False nếu lock đang bị giữ
        """
        # Try to acquire lock (non-blocking)
        acquired = ActionChainManager.physical_action_lock.acquire(blocking=False)
    
        if acquired:
            # Update tracking
            ActionChainManager.active_profile = profile_id
            ActionChainManager.lock_start_time = time.time()
        
            with ActionChainManager.holder_lock:
                ActionChainManager.current_holder = profile_id
        
            return True
    
        return False

    def release_lock(self, profile_id):
        """
        Release physical action lock
    
        Args:
            profile_id: Profile ID releasing lock
        """
        try:
            # Verify this profile is the one holding the lock
            with ActionChainManager.holder_lock:
                if ActionChainManager.current_holder != profile_id:
                    print(f"[ACTION CHAIN] ⚠ [{profile_id}] Trying to release lock but not holder (current: {ActionChainManager.current_holder})")
                    return
            
                ActionChainManager.current_holder = None
        
            # Clear tracking
            ActionChainManager.active_profile = None
            ActionChainManager.lock_start_time = None
        
            # Release lock
            ActionChainManager.physical_action_lock.release()
        
        except Exception as e:
            print(f"[ACTION CHAIN] ✗ [{profile_id}] Error releasing lock: {e}")

    def force_release_lock(self, profile_id):
        """
        Force release lock (called by health monitor when profile crashes)
    
        Args:
            profile_id: Profile ID that crashed
        """
        print(f"[ACTION CHAIN] ⚠ [{profile_id}] FORCE RELEASING LOCK (profile crashed)")
    
        try:
            # Mark profile as closed
            ActionChainManager._mark_profile_closed(profile_id)
        
            # Check if this profile is holding the lock
            with ActionChainManager.holder_lock:
                if ActionChainManager.current_holder == profile_id:
                    print(f"[ACTION CHAIN] [{profile_id}] Was holding lock, releasing...")
                
                    # Clear tracking
                    ActionChainManager.current_holder = None
                    ActionChainManager.active_profile = None
                    ActionChainManager.lock_start_time = None
                
                    # Release lock
                    try:
                        ActionChainManager.physical_action_lock.release()
                        print(f"[ACTION CHAIN] [{profile_id}] ✓ Lock force released")
                    except Exception as e:
                        print(f"[ACTION CHAIN] [{profile_id}] ⚠ Lock already released: {e}")
                else:
                    print(f"[ACTION CHAIN] [{profile_id}] Was not holding lock, no release needed")
                
        except Exception as e:
            print(f"[ACTION CHAIN] ✗ [{profile_id}] Error during force release: {e}")
            import traceback
            traceback.print_exc()

    @property
    def current_lock_holder(self):
        """Get current lock holder profile ID"""
        with ActionChainManager.holder_lock:
            return ActionChainManager.current_holder


    
    # ==================== HELPER METHODS ====================
    
    @staticmethod
    def _check_previous_holder_closed():
        with ActionChainManager.holder_lock:
            prev_holder = ActionChainManager.current_holder
    
        # THÊM 3 DÒNG DEBUG NÀY
        print(f"[ACTION CHAIN] DEBUG: Checking previous holder...")
        print(f"[ACTION CHAIN] DEBUG: Previous holder = {prev_holder}")
    
        if not prev_holder:
            print(f"[ACTION CHAIN] DEBUG: No previous holder")  # THÊM DÒNG NÀY
            return False
    
        with ActionChainManager.closed_lock:
            print(f"[ACTION CHAIN] DEBUG: Closed profiles = {ActionChainManager.closed_profiles}")  # THÊM DÒNG NÀY
        
            if prev_holder in ActionChainManager.closed_profiles:
                print(f"[ACTION CHAIN] ⚠ Detected previous holder {prev_holder} closed abnormally")
                ActionChainManager.closed_profiles.discard(prev_holder)
                return True
    
        print(f"[ACTION CHAIN] DEBUG: Previous holder did not close abnormally")  # THÊM DÒNG NÀY
        return False


    
    @staticmethod
    def _mark_profile_closed(profile_id):
        """
        Mark a profile as closed (called by health monitor)
        
        Args:
            profile_id: Profile ID that closed
            
        Purpose:
            Next profile waiting for lock can detect this and bring itself to front
        """
        with ActionChainManager.closed_lock:
            ActionChainManager.closed_profiles.add(profile_id)
            print(f"[ACTION CHAIN] [{profile_id}] Marked as closed in registry")
    
    # ==================== EXISTING UTILITY METHODS ====================
    
    @staticmethod
    def get_active_profile():
        """Get currently active profile ID"""
        return ActionChainManager.active_profile
    
    @staticmethod
    def is_locked():
        """Check if lock is currently held"""
        return ActionChainManager.physical_action_lock.locked()
