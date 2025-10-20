# helpers/action_chain_manager.py

import threading
import time
import random

class ActionChainManager:
    """
    Manages action chains with global lock to prevent profile interference
    Only one profile can execute physical action chains at a time
    """
    
    _physical_action_lock = threading.Lock()
    _active_profile = None
    _lock_start_time = None
    
    @staticmethod
    def execute_chain(profile_id, chain_func, *args, **kwargs):
        """
        Execute a complete action chain with lock
        
        Args:
            profile_id: Profile ID for logging
            chain_func: Function that performs the action chain
            *args, **kwargs: Arguments to pass to chain_func
            
        Returns:
            Result from chain_func
        """
        acquired = False
        try:
            print(f"[ACTION CHAIN] [{profile_id}] Waiting for physical action lock...")
            ActionChainManager._physical_action_lock.acquire()
            acquired = True
            
            ActionChainManager._active_profile = profile_id
            ActionChainManager._lock_start_time = time.time()
            
            print(f"[ACTION CHAIN] [{profile_id}] ✓ Lock acquired, executing chain...")
            
            # Execute the complete action chain
            result = chain_func(*args, **kwargs)
            
            # Log completion time
            elapsed = time.time() - ActionChainManager._lock_start_time
            print(f"[ACTION CHAIN] [{profile_id}] ✓ Chain completed in {elapsed:.1f}s")
            
            # ========== FIX BUFFER SLEEP ==========
            # Random buffer sleep 2-4s to allow bring_to_front
            buffer_duration = random.uniform(2.0, 4.0)
            print(f"[ACTION CHAIN] [{profile_id}] Buffer sleep {buffer_duration:.1f}s before releasing lock...")
            time.sleep(buffer_duration)
            # =====================================
            
            return result
            
        finally:
            if acquired:
                ActionChainManager._active_profile = None
                ActionChainManager._lock_start_time = None
                ActionChainManager._physical_action_lock.release()
                print(f"[ACTION CHAIN] [{profile_id}] ✓ Lock released, next profile can proceed")
    
    @staticmethod
    def get_active_profile():
        """Get currently active profile ID"""
        return ActionChainManager._active_profile
    
    @staticmethod
    def is_locked():
        """Check if lock is currently held"""
        return ActionChainManager._physical_action_lock.locked()


