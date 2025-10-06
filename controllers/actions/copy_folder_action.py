# controllers/actions/copy_folder_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import os
import shutil
import zipfile

class CopyFolderAction(BaseAction):
    """Handler để copy file/folder với các options: zip, extract, rename, delete source"""
    
    def prepare_play(self):
        """Thực hiện copy file/folder sau khi trì hoãn"""
        
        try:
            # Lấy type
            copy_type = self.params.get("copy_type", "Folder")
            
            # Lấy source path
            source_path = self.get_source_path()
            
            # Lấy destination path
            dest_path = self.get_dest_path(source_path)
            
            # Lấy options
            rename_name = self.params.get("rename_name", "").strip()
            delete_source = self.params.get("delete_source", False)
            
            print(f"[COPY] Type: {copy_type}")
            print(f"[COPY] Source: {source_path}")
            print(f"[COPY] Destination: {dest_path}")
            print(f"[COPY] Rename: {rename_name}")
            
            # Kiểm tra source tồn tại
            if not source_path or not os.path.exists(source_path):
                print(f"[COPY] Error: Source not found: {source_path}")
                self.set_variable(False)
                return
            
            # Đảm bảo destination tồn tại
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
                print(f"[COPY] Created destination: {dest_path}")
            
            # Thực hiện copy theo type
            success = False
            
            if copy_type == "Folder":
                success = self.handle_folder_copy(source_path, dest_path, rename_name)
            else:  # File
                success = self.handle_file_copy(source_path, dest_path, rename_name)
            
            # Xóa source nếu cần
            if success and delete_source:
                self.delete_source(source_path, copy_type)
            
            # Set variable
            self.set_variable(success)
            
        except Exception as e:
            print(f"[COPY] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def get_source_path(self):
        """Lấy source path (ưu tiên variable)"""
        # Priority 1: source_variable
        source_variable = self.params.get("source_variable", "").strip()
        if source_variable:
            source_path = GlobalVariables().get(source_variable, "")
            if source_path:
                print(f"[COPY] Using source from variable '{source_variable}': {source_path}")
                return source_path
        
        # Priority 2: source_browse
        source_browse = self.params.get("source_browse", "").strip()
        if source_browse:
            print(f"[COPY] Using source from browse: {source_browse}")
            return source_browse
        
        print("[COPY] No source path provided")
        return ""
    
    def get_dest_path(self, source_path):
        """Lấy destination path (ưu tiên variable, fallback = same location)"""
        # Priority 1: dest_variable
        dest_variable = self.params.get("dest_variable", "").strip()
        if dest_variable:
            dest_path = GlobalVariables().get(dest_variable, "")
            if dest_path:
                print(f"[COPY] Using destination from variable '{dest_variable}': {dest_path}")
                return dest_path
        
        # Priority 2: dest_browse
        dest_browse = self.params.get("dest_browse", "").strip()
        if dest_browse:
            print(f"[COPY] Using destination from browse: {dest_browse}")
            return dest_browse
        
        # Priority 3: Same location as source
        if source_path:
            dest_path = os.path.dirname(source_path)
            print(f"[COPY] Using same location as source: {dest_path}")
            return dest_path
        
        print("[COPY] No destination path, using current directory")
        return os.getcwd()
    
    def handle_folder_copy(self, source_path, dest_path, rename_name):
        """Handle folder copy logic"""
        zip_folder = self.params.get("zip_folder", False)
        
        if zip_folder:
            return self.copy_folder_with_zip(source_path, dest_path, rename_name)
        else:
            return self.copy_folder_normal(source_path, dest_path, rename_name)
    
    def handle_file_copy(self, source_path, dest_path, rename_name):
        """Handle file copy logic"""
        extract_file = self.params.get("extract_file", False)
        
        # Check if file is zip
        is_zip = source_path.lower().endswith('.zip')
        
        if extract_file and is_zip:
            return self.copy_file_with_extract(source_path, dest_path, rename_name)
        else:
            return self.copy_file_normal(source_path, dest_path, rename_name)
    
    def copy_file_normal(self, source_path, dest_path, rename_name):
        """Copy file thường"""
        try:
            file_name = os.path.basename(source_path)
            
            # Nếu có rename, dùng tên mới (giữ extension)
            if rename_name:
                _, ext = os.path.splitext(file_name)
                file_name = rename_name + ext
            
            final_dest = os.path.join(dest_path, file_name)
            
            # Xóa nếu đã tồn tại
            if os.path.exists(final_dest):
                print(f"[COPY] Destination exists, removing: {final_dest}")
                os.remove(final_dest)
            
            print(f"[COPY] Copying file...")
            shutil.copy2(source_path, final_dest)
            
            print(f"[COPY] File copied successfully to: {final_dest}")
            return True
            
        except Exception as e:
            print(f"[COPY] Error copying file: {e}")
            return False
    
    def copy_file_with_extract(self, source_path, dest_path, rename_name):
        """Copy file zip và extract"""
        try:
            # Bước 1: Copy file zip
            zip_name = os.path.basename(source_path)
            
            # Nếu có rename, đổi tên file zip trước
            if rename_name:
                zip_name = f"{rename_name}.zip"
            
            temp_zip = os.path.join(dest_path, zip_name)
            
            print(f"[COPY] Copying zip file to: {temp_zip}")
            shutil.copy2(source_path, temp_zip)
            print(f"[COPY] Zip file copied: {os.path.getsize(temp_zip)} bytes")
            
            # Bước 2: Extract zip
            print(f"[COPY] Extracting zip...")
            
            # Extract vào folder với tên = tên zip (không có .zip)
            extract_folder_name = zip_name[:-4] if zip_name.endswith('.zip') else zip_name
            extract_path = os.path.join(dest_path, extract_folder_name)
            
            # Xóa folder extract cũ nếu tồn tại
            if os.path.exists(extract_path):
                print(f"[COPY] Removing existing extract folder: {extract_path}")
                shutil.rmtree(extract_path)
            
            # Extract
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            print(f"[COPY] Extracted to: {extract_path}")
            
            # Bước 3: Xóa file zip sau khi extract
            os.remove(temp_zip)
            print(f"[COPY] Removed zip file after extraction")
            
            return True
            
        except Exception as e:
            print(f"[COPY] Error extracting file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def copy_folder_normal(self, source_path, dest_path, rename_name):
        """Copy folder bình thường"""
        try:
            folder_name = os.path.basename(source_path)
            
            # Nếu có rename, dùng tên mới
            if rename_name:
                folder_name = rename_name
            
            final_dest = os.path.join(dest_path, folder_name)
            
            # Xóa nếu đã tồn tại
            if os.path.exists(final_dest):
                print(f"[COPY] Destination exists, removing: {final_dest}")
                shutil.rmtree(final_dest)
            
            print(f"[COPY] Copying folder...")
            shutil.copytree(source_path, final_dest)
            
            print(f"[COPY] Folder copied successfully to: {final_dest}")
            return True
            
        except Exception as e:
            print(f"[COPY] Error copying folder: {e}")
            return False
    
    def copy_folder_with_zip(self, source_path, dest_path, rename_name):
        """Zip folder trước rồi copy file zip"""
        try:
            folder_name = os.path.basename(source_path)
            
            # Tên file zip
            if rename_name:
                zip_name = f"{rename_name}.zip"
            else:
                zip_name = f"{folder_name}.zip"
            
            # Tạo file zip tạm
            temp_zip_path = os.path.join(os.path.dirname(source_path), f"_temp_{zip_name}")
            
            print(f"[COPY] Creating zip file: {temp_zip_path}")
            
            # Zip folder
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_path)
                        zipf.write(file_path, arcname)
            
            print(f"[COPY] Zip created: {os.path.getsize(temp_zip_path)} bytes")
            
            # Copy file zip đến destination
            final_zip_path = os.path.join(dest_path, zip_name)
            
            # Xóa nếu đã tồn tại
            if os.path.exists(final_zip_path):
                print(f"[COPY] Destination zip exists, removing: {final_zip_path}")
                os.remove(final_zip_path)
            
            shutil.copy2(temp_zip_path, final_zip_path)
            
            # Xóa file zip tạm
            os.remove(temp_zip_path)
            
            print(f"[COPY] Zip file copied successfully to: {final_zip_path}")
            return True
            
        except Exception as e:
            print(f"[COPY] Error zipping folder: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_source(self, source_path, copy_type):
        """Xóa source (file hoặc folder) sau khi copy xong"""
        try:
            print(f"[COPY] Deleting source: {source_path}")
            
            if copy_type == "Folder":
                shutil.rmtree(source_path)
            else:  # File
                os.remove(source_path)
            
            print(f"[COPY] Source deleted successfully")
            
        except Exception as e:
            print(f"[COPY] Error deleting source: {e}")
            import traceback
            traceback.print_exc()
    
    def set_variable(self, success):
        """Set variable với kết quả True/False"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
            print(f"[COPY] Variable '{variable}' = {'true' if success else 'false'}")
