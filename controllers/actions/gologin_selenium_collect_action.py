# controllers/actions/gologin_selenium_collect_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class GoLoginSeleniumCollectAction(BaseAction):
    """Handler for GoLogin Selenium Collect Profiles action"""
    
    def prepare_play(self):
        """Execute GoLogin Selenium Collect"""
        try:
            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN COLLECT] Error: API key variable name is required")
                self.set_variable(False)
                return
            
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN COLLECT] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN COLLECT] Using API token from variable: {api_key_variable}")
            
            # Get profile IDs
            profile_ids_raw = self.params.get("profile_ids", "").strip()
            if not profile_ids_raw:
                print("[GOLOGIN COLLECT] Error: Profile IDs is required")
                self.set_variable(False)
                return
            
            # Parse profile IDs (separated by semicolon)
            text_items = [item.strip() for item in profile_ids_raw.split(";") if item.strip()]
            if not text_items:
                print("[GOLOGIN COLLECT] Error: No valid profile IDs found")
                self.set_variable(False)
                return
            
            # Select profile ID based on how_to_get
            how_to_get_profile = self.params.get("how_to_get", "Random")
            selected_text = self._select_text(text_items, how_to_get_profile)
            profile_id = self._process_text(selected_text)
            
            print(f"[GOLOGIN COLLECT] Selected profile ID: {profile_id}")
            
            # Get websites list from TXT file
            websites = self._load_websites_from_file()
            if not websites:
                print("[GOLOGIN COLLECT] Error: No valid websites found")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN COLLECT] Loaded {len(websites)} website(s) from file")
            
            # Get duration
            try:
                duration_minutes = float(self.params.get("duration_minutes", "5"))
                total_seconds = int(duration_minutes * 60)
                print(f"[GOLOGIN COLLECT] Duration: {duration_minutes} minute(s) ({total_seconds}s)")
            except:
                print("[GOLOGIN COLLECT] Error: Invalid duration value")
                self.set_variable(False)
                return
            
            # Get output folder
            output_folder = self._get_output_folder()
            if not output_folder:
                print("[GOLOGIN COLLECT] Error: Output folder is required")
                self.set_variable(False)
                return
            
            # Start profile
            gologin = get_gologin_api(api_token)
            success, result = gologin.start_profile(profile_id, wait_for_ready=True, max_wait=180)
            
            if not success:
                print(f"[GOLOGIN COLLECT] ✗ Failed to start profile: {result}")
                self.set_variable(False)
                return
            
            debugger_address = result
            print(f"[GOLOGIN COLLECT] ✓ Profile started: {debugger_address}")
            
            # Get profile name via API
            profile_name = self._get_profile_name(gologin, profile_id)
            
            # Connect Selenium to GoLogin Orbita
            driver = self._connect_selenium(debugger_address)
            if not driver:
                print("[GOLOGIN COLLECT] ✗ Failed to connect Selenium")
                gologin.stop_profile(profile_id)
                self.set_variable(False)
                return
            
            print("[GOLOGIN COLLECT] ✓ Selenium connected to Orbita")
            
            # Browse websites for specified duration
            self._browse_websites(driver, websites, total_seconds)
            
            # Wait for async localStorage operations to complete
            print("[GOLOGIN COLLECT] Waiting for localStorage to settle...")
            time.sleep(5)  # Wait 5s for async localStorage operations

            # Navigate back to last visited page to ensure localStorage context
            try:
                current_url = driver.current_url
                print(f"[GOLOGIN COLLECT] Current URL before save: {current_url}")
            except:
                pass
            
            # Save data before closing
            save_path = self._save_collected_data(driver, gologin, profile_id, profile_name, output_folder)
            
            # Close browser
            driver.quit()
            print("[GOLOGIN COLLECT] ✓ Browser closed")
            
            # Wait for Chrome to fully release all file locks
            time.sleep(3)
            print(f"[GOLOGIN COLLECT] Waiting for Chrome cleanup...")
            
            # Stop profile (sync to cloud)
            gologin.stop_profile(profile_id)
            print("[GOLOGIN COLLECT] ✓ Profile stopped and synced to cloud")
            
            # Store result in variable
            variable_name = self.params.get("variable", "")
            if variable_name:
                GlobalVariables().set(variable_name, save_path if save_path else "")
                print(f"[GOLOGIN COLLECT] Variable '{variable_name}' = {save_path}")
            
            self.set_variable(True)
            
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def _select_text(self, text_items, how_to_get):
        """Select text based on how_to_get method"""
        if how_to_get == "Sequential by loop":
            loop_index = GlobalVariables().get("loop_index", "0")
            try:
                index = int(loop_index) % len(text_items)
                return text_items[index]
            except:
                return text_items[0]
        else:  # Random
            return random.choice(text_items)
    
    def _process_text(self, text):
        """Process special formats like <variable_name>"""
        if text.startswith("<") and text.endswith(">"):
            var_name = text[1:-1]
            return str(GlobalVariables().get(var_name, ""))
        return text
    
    def _load_websites_from_file(self):
        """Load websites from TXT file (variable has priority)"""
        # Priority 1: Variable name containing file path
        websites_variable = self.params.get("websites_variable", "").strip()
        file_path = None
        
        if websites_variable:
            file_path = GlobalVariables().get(websites_variable, "")
            if file_path:
                print(f"[GOLOGIN COLLECT] Using websites file from variable '{websites_variable}': {file_path}")
        
        # Priority 2: Direct file path
        if not file_path:
            file_path = self.params.get("websites_file", "").strip()
            if file_path:
                print(f"[GOLOGIN COLLECT] Using direct websites file: {file_path}")
        
        # If no file specified, return empty list
        if not file_path:
            print("[GOLOGIN COLLECT] No websites file specified")
            return []
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"[GOLOGIN COLLECT] ✗ Websites file not found: {file_path}")
            return []
        
        # Read file and parse URLs (one URL per line)
        try:
            websites = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    # Skip empty lines and comments (lines starting with #)
                    if url and not url.startswith('#'):
                        websites.append(url)
            
            if not websites:
                print(f"[GOLOGIN COLLECT] ✗ No valid URLs found in file: {file_path}")
                return []
            
            print(f"[GOLOGIN COLLECT] ✓ Loaded {len(websites)} website(s) from file")
            return websites
            
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Error reading file: {e}")
            return []
    
    def _get_output_folder(self):
        """Get output folder path (variable has priority)"""
        # Priority 1: Variable name
        folder_variable = self.params.get("folder_variable", "").strip()
        if folder_variable:
            folder_path = GlobalVariables().get(folder_variable, "")
            if folder_path:
                print(f"[GOLOGIN COLLECT] Using folder from variable '{folder_variable}': {folder_path}")
                return folder_path
        
        # Priority 2: Direct path
        folder_path = self.params.get("folder_path", "").strip()
        if folder_path:
            print(f"[GOLOGIN COLLECT] Using direct folder path: {folder_path}")
            return folder_path
        
        return None
    
    def _get_profile_name(self, gologin, profile_id):
        """Get profile name via API"""
        try:
            import requests
            url = f"{gologin.base_url}/browser/{profile_id}"
            response = requests.get(url, headers=gologin.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                name = data.get("name", profile_id)
                print(f"[GOLOGIN COLLECT] Profile name: {name}")
                return name
            else:
                return profile_id
        except:
            return profile_id
    
    def _connect_selenium(self, debugger_address):
        """Connect Selenium to GoLogin Orbita browser"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
        
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
           
            # Detect Chrome version first
            chrome_version = self._get_chrome_version_from_debugger(debugger_address)
        
            if chrome_version:
                print(f"[GOLOGIN COLLECT] Installing ChromeDriver for Chrome {chrome_version}...")
                service = Service(ChromeDriverManager(driver_version=chrome_version).install())
            else:
                print(f"[GOLOGIN COLLECT] Installing ChromeDriver with auto-detection...")
                service = Service(ChromeDriverManager().install())
        
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"[GOLOGIN COLLECT] ✓ Selenium connected to Orbita")
            return driver
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Selenium connection error: {e}")
            import traceback
            traceback.print_exc()
            return None


    def _get_chrome_version_from_debugger(self, debugger_address):
        """Get Chrome version from debugger address"""
        try:
            import requests
            host, port = debugger_address.split(":")
            response = requests.get(f"http://{host}:{port}/json/version", timeout=5)
            if response.status_code == 200:
                data = response.json()
                browser_version = data.get("Browser", "")
                # Extract version like "Chrome/139.0.7258.127"
                if "/" in browser_version:
                    version = browser_version.split("/")[1]
                    major_version = version.split(".")[0]
                    print(f"[GOLOGIN COLLECT] Detected Chrome version: {version}")
                    return major_version
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Failed to detect Chrome version: {e}")
        return None

    
    def _browse_websites(self, driver, websites, total_seconds):
        """Browse websites with human-like actions until time limit"""
        from helpers.selenium_actions import SeleniumHumanActions  # Import helper
    
        print(f"[GOLOGIN COLLECT] Starting human-like browsing for {total_seconds}s...")
    
        # Initialize human actions helper
        human = SeleniumHumanActions(driver)
    
        # Get how_to_get setting for websites
        how_to_get_websites = self.params.get("how_to_get_websites", "Random")
    
        start_time = time.time()
        visit_count = 0
        action_count = 0
        current_index = 0  # For sequential mode
    
        # MAIN LOOP: Chạy cho đến khi hết thời gian
        while time.time() - start_time < total_seconds:
            # Check time remaining
            time_remaining = total_seconds - (time.time() - start_time)
            if time_remaining < 5:  # Nếu còn dưới 5s thì dừng
                print(f"[GOLOGIN COLLECT] Time limit reached, stopping...")
                break
        
            # Select URL based on how_to_get setting
            if how_to_get_websites == "Sequential by loop":
                url = websites[current_index % len(websites)]
                current_index += 1
            else:
                url = random.choice(websites)
        
            try:
                # Visit website
                print(f"[GOLOGIN COLLECT] [{visit_count+1}] Visiting: {url}")
                driver.get(url)
                visit_count += 1
                time.sleep(random.uniform(1.5, 3.0))  # Wait for page load
            
                # Perform 3-7 random human actions on this page
                num_actions = random.randint(3, 7)
            
                for i in range(num_actions):
                    # Check time again before each action
                    if time.time() - start_time >= total_seconds:
                        print(f"[GOLOGIN COLLECT] Time limit reached during actions")
                        break
                
                    # Execute random human-like action
                    action = human.execute_random_action()
                    action_count += 1
                    print(f"[GOLOGIN COLLECT]   Action {i+1}/{num_actions}: {action}")
                
                    # Random pause between actions
                    time.sleep(random.uniform(0.5, 2.0))
            
                # Sometimes click a link to go deeper (50% chance)
                if random.random() < 0.5 and time.time() - start_time < total_seconds:
                    print(f"[GOLOGIN COLLECT]   Trying to click a link...")
                    if human.click_random_link():
                        time.sleep(random.uniform(2.0, 4.0))
                        # Do a few more actions on new page
                        for _ in range(random.randint(1, 3)):
                            if time.time() - start_time >= total_seconds:
                                break
                            human.execute_random_action()
                            time.sleep(random.uniform(0.5, 1.5))
            
            except Exception as e:
                print(f"[GOLOGIN COLLECT] Error during browsing: {e}")
                time.sleep(2)
    
        elapsed = int(time.time() - start_time)
        print(f"[GOLOGIN COLLECT] ✓ Browsing completed:")
        print(f"  - Time: {elapsed}s / {total_seconds}s")
        print(f"  - Websites visited: {visit_count}")
        print(f"  - Human actions performed: {action_count}")

    
    def _save_collected_data(self, driver, gologin, profile_id, profile_name, base_folder):
        """Save collected data (IndexDB, Cookies, localStorage, History, Fingerprint)"""
        try:
            now = datetime.now()
            
            # Create folder structure: BASE/DD_MM_YYYY/
            date_folder_name = now.strftime("%d_%m_%Y")
            date_folder = os.path.join(base_folder, date_folder_name)
            
            if not os.path.exists(date_folder):
                os.makedirs(date_folder)
                print(f"[GOLOGIN COLLECT] Created date folder: {date_folder}")
            
            # Create subfolder: PROFILENAME_DD_MM_YYYY_HH_MM_SS/
            profile_folder_name = now.strftime(f"{profile_name.upper()}_%d_%m_%Y_%H_%M_%S")
            profile_folder = os.path.join(date_folder, profile_folder_name)
            os.makedirs(profile_folder)
            print(f"[GOLOGIN COLLECT] Created profile folder: {profile_folder}")
            
            # Get save options
            save_indexdb = self.params.get("save_indexdb", False)
            save_cookies = self.params.get("save_cookies", True)
            save_localstorage = self.params.get("save_localstorage", False)
            save_fingerprint = self.params.get("save_fingerprint", False)
            
            # Save IndexDB
            if save_indexdb:
                indexdb_path = self._save_indexdb(driver, profile_folder, profile_name, now)
                if indexdb_path:
                    print(f"[GOLOGIN COLLECT] ✓ Saved IndexDB: {indexdb_path}")
            
            # Save Cookies
            if save_cookies:
                cookies_path = self._save_cookies(driver, profile_folder, profile_name, now)
                if cookies_path:
                    print(f"[GOLOGIN COLLECT] ✓ Saved Cookies: {cookies_path}")
            
            # Save localStorage
            if save_localstorage:
                localstorage_path = self._save_localstorage(driver, profile_folder, profile_name, now)
                if localstorage_path:
                    print(f"[GOLOGIN COLLECT] ✓ Saved localStorage: {localstorage_path}")           
            
            # Save Fingerprint Profile (CSV via API)
            if save_fingerprint:
                fingerprint_path = self._save_fingerprint_profile(gologin, profile_id, profile_folder, profile_name, now)
                if fingerprint_path:
                    print(f"[GOLOGIN COLLECT] ✓ Saved Fingerprint CSV: {fingerprint_path}")
            
            return profile_folder
            
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Error saving data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _save_indexdb(self, driver, folder, profile_name, timestamp):
        """Save IndexDB data with full content"""
        try:
            print("[GOLOGIN COLLECT] Extracting IndexedDB...")
        
            # NEW SCRIPT: Extract FULL data from all databases
            script = """
            return new Promise(async (resolve) => {
                try {
                    const databases = await indexedDB.databases();
                
                    if (!databases || databases.length === 0) {
                        console.log('No IndexedDB databases found');
                        resolve({});
                        return;
                    }
                
                    console.log('Found databases:', databases.map(d => d.name));
                    const result = {};
                
                    for (const dbInfo of databases) {
                        console.log('Processing database:', dbInfo.name);
                    
                        try {
                            // Open database
                            const db = await new Promise((res, rej) => {
                                const request = indexedDB.open(dbInfo.name);
                                request.onsuccess = () => res(request.result);
                                request.onerror = () => rej(request.error);
                                request.onblocked = () => {
                                    console.log('DB blocked:', dbInfo.name);
                                    rej(new Error('Database blocked'));
                                };
                            });
                        
                            const dbData = {
                                name: dbInfo.name,
                                version: db.version,
                                objectStores: []
                            };
                        
                            // Loop through all object stores
                            const storeNames = Array.from(db.objectStoreNames);
                            console.log('Object stores in', dbInfo.name, ':', storeNames);
                        
                            for (const storeName of storeNames) {
                                try {
                                    const tx = db.transaction(storeName, 'readonly');
                                    const store = tx.objectStore(storeName);
                                
                                    // Get all data from store
                                    const storeData = await new Promise((res, rej) => {
                                        const request = store.getAll();
                                        request.onsuccess = () => {
                                            console.log('Store', storeName, 'has', request.result.length, 'items');
                                            res(request.result);
                                        };
                                        request.onerror = () => {
                                            console.log('Error reading store:', storeName);
                                            res([]);
                                        };
                                    });
                                
                                    // Get all keys
                                    const storeKeys = await new Promise((res, rej) => {
                                        const request = store.getAllKeys();
                                        request.onsuccess = () => res(request.result);
                                        request.onerror = () => res([]);
                                    });
                                
                                    dbData.objectStores.push({
                                        name: storeName,
                                        keyPath: store.keyPath,
                                        autoIncrement: store.autoIncrement,
                                        keys: storeKeys,
                                        data: storeData
                                    });
                                
                                    console.log('Extracted', storeData.length, 'items from', storeName);
                                } catch (storeError) {
                                    console.log('Error processing store:', storeName, storeError);
                                }
                            }
                        
                            db.close();
                            result[dbInfo.name] = dbData;
                        
                        } catch (dbError) {
                            console.log('Error opening database:', dbInfo.name, dbError);
                            result[dbInfo.name] = {
                                name: dbInfo.name,
                                error: dbError.toString()
                            };
                        }
                    }
                
                    console.log('IndexedDB extraction complete');
                    resolve(result);
                
                } catch (error) {
                    console.error('IndexedDB extraction error:', error);
                    resolve({error: error.toString()});
                }
            });
            """
        
            # Execute script with timeout
            indexdb_data = driver.execute_script(script)
        
            # Check if data is empty
            if not indexdb_data or len(indexdb_data) == 0:
                print("[GOLOGIN COLLECT] ⚠️ No IndexedDB data found")
                # Still save empty file for consistency
                indexdb_data = {"message": "No IndexedDB databases found"}
            else:
                total_items = 0
                for db_name, db_content in indexdb_data.items():
                    if isinstance(db_content, dict) and 'objectStores' in db_content:
                        for store in db_content['objectStores']:
                            total_items += len(store.get('data', []))
                print(f"[GOLOGIN COLLECT] ✓ Extracted {len(indexdb_data)} database(s) with {total_items} total items")
        
            # Save to JSON file
            filename = timestamp.strftime(f"{profile_name.upper()}_INDEXDB_%d_%m_%Y_%H_%M_%S.json")
            filepath = os.path.join(folder, filename)
        
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(indexdb_data, f, indent=2, ensure_ascii=False)
        
            return filepath
        
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Error saving IndexDB: {e}")
            import traceback
            traceback.print_exc()
            return None

    
    def _save_cookies(self, driver, folder, profile_name, timestamp):
        """Save Cookies"""
        try:
            cookies = driver.get_cookies()
            
            filename = timestamp.strftime(f"{profile_name.upper()}_COOKIES_%d_%m_%Y_%H_%M_%S.json")
            filepath = os.path.join(folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            return filepath
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Error saving Cookies: {e}")
            return None
    
    def _save_localstorage(self, driver, folder, profile_name, timestamp):
        """Save localStorage from all domains visited during session"""
        try:
            print("[GOLOGIN COLLECT] Collecting localStorage from all visited domains...")
        
            all_localstorage = {}
        
            # Get all window handles (tabs)
            current_handle = driver.current_window_handle
            all_handles = driver.window_handles
        
            print(f"[GOLOGIN COLLECT] Found {len(all_handles)} tab(s)")
        
            # Collect localStorage from each tab
            for handle in all_handles:
                try:
                    driver.switch_to.window(handle)
                    current_url = driver.current_url
                
                    # Execute JS to get localStorage
                    script = "return Object.assign({}, window.localStorage);"
                    localstorage_data = driver.execute_script(script)
                
                    if localstorage_data and len(localstorage_data) > 0:
                        # Get domain from URL
                        from urllib.parse import urlparse
                        parsed = urlparse(current_url)
                        domain = parsed.netloc or "unknown"
                    
                        all_localstorage[domain] = {
                            "url": current_url,
                            "localStorage": localstorage_data
                        }
                        print(f"[GOLOGIN COLLECT] ✓ {domain}: {len(localstorage_data)} items")
                
                except Exception as e:
                    print(f"[GOLOGIN COLLECT] Error collecting from tab: {e}")
                    continue
        
            # Switch back to original handle
            try:
                driver.switch_to.window(current_handle)
            except:
                pass
        
            if not all_localstorage or len(all_localstorage) == 0:
                print("[GOLOGIN COLLECT] ⚠️ No localStorage data found in any tab")
                # Save empty structure for consistency
                all_localstorage = {"message": "No localStorage data found"}
            else:
                total_items = sum(len(data["localStorage"]) for data in all_localstorage.values())
                print(f"[GOLOGIN COLLECT] ✓ Collected localStorage from {len(all_localstorage)} domain(s), {total_items} total items")
        
            # Save to JSON file
            filename = timestamp.strftime(f"{profile_name.upper()}_LOCALSTORAGE_%d_%m_%Y_%H_%M_%S.json")
            filepath = os.path.join(folder, filename)
        
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_localstorage, f, indent=2, ensure_ascii=False)
        
            return filepath
        
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Error saving localStorage: {e}")
            import traceback
            traceback.print_exc()
            return None

    
    def _save_fingerprint_profile(self, gologin, profile_id, folder, profile_name, timestamp):
        """Save Fingerprint Profile as CSV via GoLogin API"""
        try:
            import requests
            
            # API: POST https://api.gologin.com/browser/browsers.csv
            url = f"{gologin.base_url}/browser/browsers.csv"
            
            body = {
                "browsersIds": [profile_id]
            }
            
            print(f"[GOLOGIN COLLECT] Exporting fingerprint profile via API...")
            response = requests.post(url, headers=gologin.headers, json=body, timeout=30)
            
            if response.status_code in [200, 201]:
                # Save CSV content
                filename = timestamp.strftime(f"{profile_name.upper()}_FINGERPRINT_%d_%m_%Y_%H_%M_%S.csv")
                filepath = os.path.join(folder, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return filepath
            else:
                print(f"[GOLOGIN COLLECT] ✗ Export fingerprint failed: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[GOLOGIN COLLECT] Error saving fingerprint: {e}")
            return None
    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
