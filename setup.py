import os
import sys
import subprocess

def install_packages(requirements_file="requirements.txt"):
    if not os.path.isfile(requirements_file):
        print(f"Error: {requirements_file} not found!")
        sys.exit(1)
    
    cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call(cmd)
        print("All packages have been installed successfully.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while installing packages.")
        sys.exit(e.returncode)


#jordbruksverket data (pre-downloaded from the API)
def download_assets():
    import os
    import gdown
    import rarfile

    #google drive id
    file_id = "1zl6ghwo1R5t11DP56-CY4NwSXKHk95x9"
    url = f"https://drive.google.com/uc?id={file_id}&export=download"

    #temp output
    output = "jordbruksverket_data/jordbruksverket_data.json"

    print("Downloading file from Google Drive...")
    # gdown will handle the confirmation automatically
    gdown.download(url, output, quiet=False)

    #verify download size
    if os.path.getsize(output) < 10000:
        print("Error: Downloaded file seems too small. The download may have failed.")
        exit(1)
    else:
        print("Download successful, unpacking the file...")



if __name__ == "__main__":
    install_packages()
    download_assets()
