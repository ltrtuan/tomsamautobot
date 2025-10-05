# controllers/actions/read_csv_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import random
import os
import csv

class ReadCsvAction(BaseAction):
    """Handler for read CSV/Excel file action."""
    
    def prepare_play(self):
        """Execute read CSV/Excel file action after delay"""
        if self.should_stop():
            return
        
        # ➊ PRIORITY: Get file path from variable
        file_path = self._resolve_file_path()
    
        if not file_path:
            print("[READ_CSV] Error: No file path specified")
            return
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"[READ_CSV] Error: File not found: {file_path}")
            return
        
        # Read file based on extension
        try:
            rows = self._read_file(file_path)
        except Exception as e:
            print(f"[READ_CSV] Error reading file: {e}")
            return
        
        if not rows:
            print("[READ_CSV] Error: File is empty or contains no valid rows")
            return
        
        # Skip header if specified
        skip_header = self.params.get("skip_header", False)
        if skip_header and len(rows) > 1:
            rows = rows[1:]
            print(f"[READ_CSV] Skipped header row, {len(rows)} data rows remaining")
        
        # Get how_to_get method
        how_to_get = self.params.get("how_to_get", "Random")
        
        # Select row based on method
        selected_row = self._select_row(rows, how_to_get)
        
        print(f"[READ_CSV] Selected row: {selected_row}")
        
        # ➊ Get variables from COMMON PARAMS (not separate field)
        variables_str = self.params.get("variable", "")  # From common params!
        if variables_str:
            self._assign_variables(selected_row, variables_str)
    
    def _read_file(self, file_path):
        """Read CSV or Excel file and return rows"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.csv':
            return self._read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            return self._read_excel(file_path)
        else:
            print(f"[READ_CSV] Warning: Unknown file type {ext}, trying CSV format...")
            return self._read_csv(file_path)
    
    def _read_csv(self, file_path):
        """Read CSV file"""
        rows = []
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    rows.append(row)
        return rows
    
    def _read_excel(self, file_path):
        """Read Excel file"""
        try:
            import openpyxl
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            sheet = workbook.active
            
            rows = []
            for row in sheet.iter_rows(values_only=True):
                if any(cell is not None for cell in row):
                    row_data = [str(cell) if cell is not None else "" for cell in row]
                    rows.append(row_data)
            
            return rows
        except ImportError:
            print("[READ_CSV] Error: openpyxl not installed. Install with: pip install openpyxl")
            return []
        except Exception as e:
            print(f"[READ_CSV] Error reading Excel file: {e}")
            return []
    
    def _select_row(self, rows, how_to_get):
        """Select row based on how_to_get method"""
        if how_to_get == "Random":
            return random.choice(rows)
        elif how_to_get == "Sequential by loop":
            globals_var = GlobalVariables()
            loop_index_str = globals_var.get("loop_index", "1")
            try:
                loop_index = int(loop_index_str)
                index = (loop_index - 1) % len(rows)
                return rows[index]
            except:
                return rows[0]
        else:
            return rows[0]
    
    def _assign_variables(self, row, variables_str):
        """
        Assign row columns to variables (multi-variable support)
        Example: variables_str = "USERNAME;PASSWORD;EMAIL"
        """
        # ➊ Parse variables string: "USERNAME;PASSWORD;EMAIL"
        variable_names = [v.strip() for v in variables_str.split(';') if v.strip()]
        
        if not variable_names:
            print("[READ_CSV] No variables specified")
            return
        
        globals_var = GlobalVariables()
        
        # ➋ Assign columns to variables (stop when either list ends)
        for i, var_name in enumerate(variable_names):
            if i < len(row):
                value = row[i]
                globals_var.set(var_name, value)
                print(f"[READ_CSV] Set variable '{var_name}' = '{value}'")
            else:
                # More variables than columns - skip remaining variables
                print(f"[READ_CSV] Skipped variable '{var_name}' (no corresponding column)")
                break


    def _resolve_file_path(self):
        """
        Resolve file path with priority:
        1. From global variable (if file_path_variable is set)
        2. From direct file_path parameter
        """
        from models.global_variables import GlobalVariables
    
        # ➊ Try to get from variable first (PRIORITY)
        file_path_variable = self.params.get("file_path_variable", "").strip()
    
        if file_path_variable:
            globals_var = GlobalVariables()
            file_path_from_var = globals_var.get(file_path_variable, "")
        
            if file_path_from_var:
                print(f"[READ_CSV] Using file path from variable '{file_path_variable}': {file_path_from_var}")
                return file_path_from_var
            else:
                print(f"[READ_CSV] Warning: Variable '{file_path_variable}' not found or empty")
    
        # ➋ Fallback to direct file path
        file_path = self.params.get("file_path", "").strip()
    
        if file_path:
            print(f"[READ_CSV] Using direct file path: {file_path}")
            return file_path
    
        return None