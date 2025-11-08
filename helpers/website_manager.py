# helpers/website_manager.py
"""
Website Manager Helper
Manages collect and warmup website files with rotation and caching
"""

import os
import re
import random
import threading
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger('TomSamAutobot')

# ========== CONSTANTS ==========
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ========== CACHE FOR WARMUP WEBSITES (SINGLETON PATTERN) ==========
_warmup_cache_lock = threading.Lock()
_warmup_websites_cache = None  # List of URLs, loaded once per app session
_warmup_cache_initialized = False


# ========== FUNCTION 1: SAVE COLLECTED URL ==========
def save_collected_url(url, collect_file_path):
    """
    Save URL to collect file with automatic rotation when file exceeds 10MB
    
    Args:
        url (str): URL to save
        collect_file_path (str): Path to collect file (user input)
    
    Returns:
        bool: Success status
    
    File naming:
        Original: collect-websites.txt
        Rotated:  collect-websites-08-11-2025-10-30.txt
    """
    try:
        # Validate input
        if not collect_file_path or not collect_file_path.strip():
            logger.debug("Collect file path not provided, skipping URL save")
            return False
        
        if not url or not url.strip():
            logger.debug("URL is empty, skipping save")
            return False
        
        url = url.strip()
        
        # Parse file path
        file_path = Path(collect_file_path)
        file_dir = file_path.parent
        base_name = file_path.stem  # Filename without extension
        extension = file_path.suffix  # .txt
        
        # ========== GET ACTIVE FILE (LATEST OR CREATE NEW) ==========
        active_file = _get_active_collect_file(file_dir, base_name, extension)
        
        # ========== CHECK FILE SIZE & ROTATE IF NEEDED ==========
        if active_file.exists():
            file_size = active_file.stat().st_size
            
            if file_size >= MAX_FILE_SIZE_BYTES:
                logger.info(f"Collect file exceeded {MAX_FILE_SIZE_MB}MB, rotating...")
                active_file = _create_rotated_file(file_dir, base_name, extension)
        
        # ========== SAVE URL TO FILE ==========
        # Check if URL already exists (avoid duplicates)
        if active_file.exists():
            with open(active_file, 'r', encoding='utf-8') as f:
                existing_urls = set(line.strip() for line in f if line.strip())
            
            if url in existing_urls:
                logger.debug(f"URL already exists in collect file: {url}")
                return True  # Already saved, consider success
        
        # Append URL to file
        with open(active_file, 'a', encoding='utf-8') as f:
            f.write(url + '\n')
        
        logger.debug(f"Saved URL to collect file: {url} -> {active_file.name}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save collected URL: {e}")
        return False


def _get_active_collect_file(file_dir, base_name, extension):
    """
    Get the latest (active) collect file to write to
    
    Logic:
        1. List all files matching pattern:
           - base_name.extension
           - base_name-DD-MM-YYYY-HH-MM.extension
           - base_name-DD-MM-YYYY-HH-MM-2.extension (NEW)
           - base_name-DD-MM-YYYY-HH-MM-3.extension (NEW)
        2. Extract timestamp and counter from filenames
        3. Sort by (timestamp DESC, counter DESC) → newest with highest counter first
        4. Return first file that is < 10MB, else return base file
    
    Returns:
        Path: Active file path
    """
    try:
        # Pattern: base_name[-DD-MM-YYYY-HH-MM][-counter].extension
        # Groups: (day, month, year, hour, minute, counter)
        pattern = re.compile(
            rf"^{re.escape(base_name)}"  # Base name
            rf"(?:-(\d{{2}})-(\d{{2}})-(\d{{4}})-(\d{{2}})-(\d{{2}})"  # Optional timestamp
            rf"(?:-(\d+))?)?"  # Optional counter (NEW)
            rf"{re.escape(extension)}$"
        )
        
        # List all matching files
        matching_files = []
        
        for file in file_dir.glob(f"{base_name}*{extension}"):
            match = pattern.match(file.name)
            if match:
                day, month, year, hour, minute, counter_str = match.groups()
                
                if day:  # Has timestamp
                    # Parse timestamp
                    timestamp = datetime(
                        int(year), int(month), int(day),
                        int(hour), int(minute)
                    )
                    # Parse counter (default to 1 if not present)
                    counter = int(counter_str) if counter_str else 1
                else:
                    # Base file (no timestamp) - treat as oldest
                    timestamp = datetime.min
                    counter = 0
                
                matching_files.append({
                    'file': file,
                    'timestamp': timestamp,
                    'counter': counter
                })
        
        # Sort by timestamp DESC, then counter DESC (newest + highest counter first)
        matching_files.sort(
            key=lambda x: (x['timestamp'], x['counter']),
            reverse=True
        )
        
        # Return first file that is < 10MB
        for item in matching_files:
            file = item['file']
            
            if file.exists():
                file_size = file.stat().st_size
                
                if file_size < MAX_FILE_SIZE_BYTES:
                    logger.debug(f"Active collect file: {file.name} ({file_size / 1024 / 1024:.1f} MB)")
                    return file
        
        # No valid file found, return base file path
        base_file = file_dir / f"{base_name}{extension}"
        logger.debug(f"No active file < {MAX_FILE_SIZE_MB}MB, using base: {base_file.name}")
        return base_file
    
    except Exception as e:
        logger.error(f"Error getting active collect file: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to base file
        return file_dir / f"{base_name}{extension}"



def _create_rotated_file(file_dir, base_name, extension):
    """
    Create new rotated file with timestamp, with collision handling
    
    Format: base_name-DD-MM-YYYY-HH-MM.extension
    
    Collision handling:
        If file exists AND >= 10MB:
            - Try: base_name-DD-MM-YYYY-HH-MM-2.extension
            - Try: base_name-DD-MM-YYYY-HH-MM-3.extension
            - ... until find available filename
    
    Example:
        VN server (GMT+7):  collect-websites-08-11-2025-10-30.txt (10.2 MB)
        US server (GMT-5):  collect-websites-08-11-2025-10-30.txt (exists!)
        → Creates:          collect-websites-08-11-2025-10-30-2.txt
    
    Args:
        file_dir (Path): Directory to create file in
        base_name (str): Base filename without extension
        extension (str): File extension (e.g., '.txt')
    
    Returns:
        Path: New file path (guaranteed to be unique and < 10MB if exists)
    """
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%Y-%H-%M")
    
    # Try base timestamp filename first
    counter = 1
    max_attempts = 1000  # Safety limit
    
    while counter <= max_attempts:
        # Build filename
        if counter == 1:
            # First attempt: no counter suffix
            new_filename = f"{base_name}-{timestamp}{extension}"
        else:
            # Subsequent attempts: add counter suffix
            new_filename = f"{base_name}-{timestamp}-{counter}{extension}"
        
        new_file_path = file_dir / new_filename
        
        # ========== CHECK IF FILE EXISTS ==========
        if not new_file_path.exists():
            # File doesn't exist → use this filename
            logger.info(f"Created new rotated collect file: {new_filename}")
            return new_file_path
        
        # File exists → check size
        try:
            file_size = new_file_path.stat().st_size
            
            if file_size < MAX_FILE_SIZE_BYTES:
                # File exists but < 10MB → reuse this file
                logger.info(f"Reusing existing rotated file (< {MAX_FILE_SIZE_MB}MB): {new_filename}")
                return new_file_path
            else:
                # File exists and >= 10MB → try next counter
                logger.debug(f"File exists and >= {MAX_FILE_SIZE_MB}MB, trying next: {new_filename}")
                counter += 1
        
        except OSError as e:
            # File exists but can't stat (permission error?) → try next
            logger.warning(f"Cannot stat file {new_filename}, trying next: {e}")
            counter += 1
    
    # ========== FALLBACK (SHOULD NEVER REACH) ==========
    # If somehow all 1000 filenames are >= 10MB, use UUID
    import uuid
    fallback_filename = f"{base_name}-{timestamp}-{uuid.uuid4().hex[:8]}{extension}"
    fallback_path = file_dir / fallback_filename
    
    logger.warning(f"Max attempts reached, using fallback filename: {fallback_filename}")
    return fallback_path



# ========== FUNCTION 2: LOAD WARMUP WEBSITES (FROM RANDOM FILE) ==========
def load_warmup_websites(warmup_file_path):
    """
    Load warmup websites from a random file matching pattern
    
    Logic:
        1. Extract base name from input file (remove timestamp AND counter if exists)
        2. Find all files matching base name pattern
        3. Randomly select one file
        4. Read and return URLs from that file
    
    Args:
        warmup_file_path (str): Path to warmup file (user input, may have timestamp + counter)
    
    Returns:
        list: List of URLs, or empty list if error/no file
    
    Example:
        Input:  "warmup-websites-08-11-2025-10-30-2.txt"  (NEW: with counter)
        Files:  ["warmup-websites.txt", 
                 "warmup-websites-07-11-2025-14-20.txt",
                 "warmup-websites-08-11-2025-10-30.txt",
                 "warmup-websites-08-11-2025-10-30-2.txt"]
        Action: Randomly pick one → Read URLs → Return list
    """
    try:
        # Validate input
        if not warmup_file_path or not warmup_file_path.strip():
            logger.debug("Warmup file path not provided")
            return []
        
        # Parse file path
        file_path = Path(warmup_file_path)
        file_dir = file_path.parent
        file_name = file_path.name
        extension = file_path.suffix
        
        # ========== EXTRACT BASE NAME (REMOVE TIMESTAMP AND COUNTER) ==========
        # Pattern: base_name[-DD-MM-YYYY-HH-MM][-counter].extension
        # Groups: (base_name, optional_timestamp_and_counter)
        pattern = re.compile(
            rf"^(.+?)"  # Base name (non-greedy)
            rf"(?:-\d{{2}}-\d{{2}}-\d{{4}}-\d{{2}}-\d{{2}}"  # Optional timestamp
            rf"(?:-\d+)?)?"  # Optional counter (NEW!)
            rf"{re.escape(extension)}$"
        )
        
        match = pattern.match(file_name)
        if not match:
            logger.error(f"Invalid warmup file name format: {file_name}")
            return []
        
        base_name = match.group(1)
        logger.debug(f"Extracted base name: '{base_name}' from '{file_name}'")
        
        # ========== FIND ALL MATCHING FILES ==========
        # Pattern to match during search (same as above, but for validation)
        search_pattern = re.compile(
            rf"^{re.escape(base_name)}"
            rf"(?:-\d{{2}}-\d{{2}}-\d{{4}}-\d{{2}}-\d{{2}}"
            rf"(?:-\d+)?)?"
            rf"{re.escape(extension)}$"
        )
        
        matching_files = []
        
        for file in file_dir.glob(f"{base_name}*{extension}"):
            if file.is_file() and search_pattern.match(file.name):
                matching_files.append(file)
        
        if not matching_files:
            logger.warning(f"No warmup files found matching pattern: {base_name}*{extension}")
            return []
        
        logger.info(f"Found {len(matching_files)} warmup files matching '{base_name}'")
        for f in matching_files:
            logger.debug(f"  - {f.name}")
        
        # ========== RANDOMLY SELECT ONE FILE ==========
        selected_file = random.choice(matching_files)
        logger.info(f"Randomly selected warmup file: {selected_file.name}")
        
        # ========== READ URLs FROM FILE ==========
        urls = []
        
        with open(selected_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                url = line.strip()
                
                # Skip empty lines and comments
                if not url or url.startswith('#'):
                    continue
                
                # Basic URL validation
                if url.startswith('http://') or url.startswith('https://'):
                    urls.append(url)
                else:
                    logger.warning(f"Invalid URL at line {line_num} in {selected_file.name}: {url}")
        
        logger.info(f"Loaded {len(urls)} valid URLs from warmup file: {selected_file.name}")
        
        return urls
    
    except Exception as e:
        logger.error(f"Failed to load warmup websites: {e}")
        import traceback
        traceback.print_exc()
        return []



# ========== FUNCTION 3: GET RANDOM WARMUP URL (WITH CACHING) ==========
def get_random_warmup_url(warmup_file_path=None):
    """
    Get a random warmup URL from cache
    
    Features:
        - Loads warmup URLs ONCE per app session (cached)
        - Thread-safe
        - Returns random URL from cache on each call
        - No profile_id or driver dependency (works with non-Selenium actions)
    
    Args:
        warmup_file_path (str, optional): Path to warmup file
            - Only used on FIRST call to initialize cache
            - Ignored on subsequent calls (cache already loaded)
    
    Returns:
        str: Random URL from cache, or None if cache empty
    
    Usage:
        # First call (initialization)
        url = get_random_warmup_url("warmup-websites.txt")
        
        # Subsequent calls (use cache)
        url = get_random_warmup_url()  # No file path needed
        url = get_random_warmup_url()  # Returns different random URL
    """
    global _warmup_websites_cache, _warmup_cache_initialized
    
    try:
        # ========== THREAD-SAFE CACHE INITIALIZATION ==========
        with _warmup_cache_lock:
            # Check if cache already initialized
            if _warmup_cache_initialized:
                # Cache exists, return random URL
                if _warmup_websites_cache and len(_warmup_websites_cache) > 0:
                    return random.choice(_warmup_websites_cache)
                else:
                    logger.warning("Warmup cache is empty")
                    return None
            
            # ========== FIRST CALL - INITIALIZE CACHE ==========
            if not warmup_file_path or not warmup_file_path.strip():
                logger.warning("Warmup file path not provided on first call")
                _warmup_cache_initialized = True  # Mark as initialized (but empty)
                _warmup_websites_cache = []
                return None
            
            logger.info(f"Initializing warmup websites cache from: {warmup_file_path}")
            
            # Load URLs from file
            _warmup_websites_cache = load_warmup_websites(warmup_file_path)
            _warmup_cache_initialized = True
            
            if _warmup_websites_cache:
                logger.info(f"Warmup cache initialized with {len(_warmup_websites_cache)} URLs")
                return random.choice(_warmup_websites_cache)
            else:
                logger.warning("Warmup cache initialized but empty (no URLs loaded)")
                return None
    
    except Exception as e:
        logger.error(f"Error getting random warmup URL: {e}")
        return None


# ========== HELPER: RESET CACHE (FOR TESTING) ==========
def reset_warmup_cache():
    """
    Reset warmup cache (useful for testing or manual reload)
    
    Note: This is NOT called automatically. Only use for debugging/testing.
    """
    global _warmup_websites_cache, _warmup_cache_initialized
    
    with _warmup_cache_lock:
        _warmup_websites_cache = None
        _warmup_cache_initialized = False
        logger.info("Warmup cache reset")


# ========== HELPER: GET CACHE STATUS (FOR DEBUGGING) ==========
def get_warmup_cache_status():
    """
    Get current cache status (for debugging)
    
    Returns:
        dict: Cache status info
    """
    with _warmup_cache_lock:
        return {
            'initialized': _warmup_cache_initialized,
            'url_count': len(_warmup_websites_cache) if _warmup_websites_cache else 0,
            'cache_size_bytes': sum(len(url) for url in _warmup_websites_cache) if _warmup_websites_cache else 0
        }
