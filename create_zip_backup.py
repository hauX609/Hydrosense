import os
import zipfile

def zip_project(source_dir, output_filename):
    # Folders to exclude
    EXCLUDE_DIRS = {
        'node_modules', 
        '.git', 
        '__pycache__', 
        'venv', 
        'env', 
        '.idea', 
        '.vscode',
        'dist',
        'build',
        'coverage'
    }
    
    # Files to exclude
    EXCLUDE_FILES = {
        '.DS_Store',
        'Thumbs.db',
        os.path.basename(__file__) # Exclude this script itself
    }

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                
                if file.endswith('.zip'): # Don't zip other zip files
                    continue

                file_path = os.path.join(root, file)
                # Create relative path for the zip archive
                arcname = os.path.relpath(file_path, source_dir)
                
                print(f"Adding: {arcname}")
                try:
                    zipf.write(file_path, arcname)
                except Exception as e:
                    print(f"Error adding {file_path}: {e}")

if __name__ == "__main__":
    source = r"c:/Users/dell/OneDrive/Desktop/Bangladesh_Flood_Project/Bangladesh_Flood_Project"
    destination = r"c:/Users/dell/OneDrive/Desktop/Bangladesh_Flood_Project/Bangladesh_Flood_Project_Backup.zip"
    
    print(f"Zipping '{source}' to '{destination}'...")
    try:
        zip_project(source, destination)
        print("Zip created successfully!")
    except Exception as e:
        print(f"Failed to create zip: {e}")
