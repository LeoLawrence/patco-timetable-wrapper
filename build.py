import os
import shutil
import subprocess

DIST_DIR = "dist"

def main():
    print("Building PATCO Scheduler Site...")
    
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    
    print("Running extractor...")
    subprocess.check_call(["python3", "extract_schedule.py"])
    
    print("Injecting JSON and copying files to dist/...")
    
    with open("schedule.json", "r") as f:
        json_content = f.read()
        
    with open("index.html", "r") as f:
        html_content = f.read()
    
    new_html_content = html_content.replace(
        "let scheduleData = null;", 
        f"let scheduleData = {json_content};"
    )
    
    if new_html_content == html_content:
        print("WARNING: Could not find placeholder in index.html to inject JSON.")
    
    with open(os.path.join(DIST_DIR, "index.html"), "w") as f:
        f.write(new_html_content)
        
    shutil.copy("schedule.json", os.path.join(DIST_DIR, "schedule.json"))
    
    print(f"Build complete. Files are in {os.path.abspath(DIST_DIR)}")

if __name__ == "__main__":
    main()
