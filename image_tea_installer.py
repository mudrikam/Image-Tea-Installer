import os
import json
import zipfile
import urllib.request
import urllib.error
import shutil
import tempfile
import sys
from pathlib import Path


def load_config():
    """Load configuration from installer_configs.json"""
    config_path = Path(__file__).parent / "installer_configs.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_latest_release(repo_url):
    """Get latest release information from GitHub repository"""
    # Extract owner and repo name from URL
    # Example: https://github.com/mudrikam/Image-Tea-nano -> mudrikam/Image-Tea-nano
    parts = repo_url.rstrip('/').split('/')
    owner, repo = parts[-2], parts[-1]
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    
    try:
        with urllib.request.urlopen(api_url) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error fetching latest release: {e}")
        raise


def download_file(url, destination):
    """Download file from URL to destination with progress indicator"""
    print(f"\n{'=' * 60}")
    print(f"Downloading: {url}")
    print(f"Destination: {destination}")
    print(f"{'=' * 60}")
    
    try:
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(int(downloaded / total_size * 100), 100)
                bar_length = 40
                filled = int(bar_length * percent / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                
                sys.stdout.write(f'\r[{bar}] {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)')
                sys.stdout.flush()
                
                if downloaded >= total_size:
                    print()  # New line after completion
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\n✓ Download completed!")
        return True
    except Exception as e:
        print(f"\n✗ Error downloading file: {e}")
        return False


def extract_zip(zip_path, extract_to):
    """Extract zip file to specified directory, placing contents directly into extract_to
    (if the zip contains a single top-level directory, its children are moved up)."""
    print(f"\n{'=' * 60}")
    print(f"Extracting: {zip_path}")
    print(f"To: {extract_to}")
    print(f"{'=' * 60}")
    
    try:
        # Ensure target directory exists
        extract_to.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(dir=extract_to.parent) as tmpdir:
            tmp_path = Path(tmpdir)
            
            print("Extracting archive...", end='', flush=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_path)
            print(" ✓")

            entries = list(tmp_path.iterdir())

            print("Moving files...", end='', flush=True)
            # If the archive contains a single top-level directory, move its children up
            if len(entries) == 1 and entries[0].is_dir():
                source = entries[0]
                for item in source.iterdir():
                    dest = extract_to / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))
            else:
                # Move all entries into the target directory
                for item in entries:
                    dest = extract_to / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))
            print(" ✓")

        print("\n✓ Extraction completed!")
        return True
    except Exception as e:
        print(f"\n✗ Error extracting file: {e}")
        return False


def main():
    """Main installer function with enhanced CLI interface"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "IMAGE-TEA INSTALLER" + " " * 24 + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Load configuration
    try:
        config = load_config()
        application_repo = config['application_repo']
        installation_file = config['installation_file']
    except Exception as e:
        print(f"\n✗ Error loading configuration: {e}")
        input("\nPress Enter to exit...")
        return
    
    print(f"\n📦 Application: {application_repo.split('/')[-1]}")
    print(f"🔗 Repository:  {application_repo}")
    print(f"📄 Package:     {installation_file}")
    
    # Get latest release
    print(f"\n{'=' * 60}")
    print("Fetching latest release information...")
    print(f"{'=' * 60}")
    
    try:
        release_info = get_latest_release(application_repo)
        print(f"\n✓ Found release: {release_info['tag_name']}")
        print(f"  Name: {release_info['name']}")
        print(f"  Published: {release_info.get('published_at', 'N/A')}")
    except Exception as e:
        print(f"\n✗ Error fetching release information: {e}")
        input("\nPress Enter to exit...")
        return
    
    # Find the installation file in assets
    download_url = None
    for asset in release_info['assets']:
        if asset['name'] == installation_file:
            download_url = asset['browser_download_url']
            file_size = asset.get('size', 0)
            print(f"  Size: {file_size / (1024 * 1024):.2f} MB")
            break
    
    if not download_url:
        print(f"\n✗ Error: {installation_file} not found in latest release assets!")
        input("\nPress Enter to exit...")
        return
    
    # Prepare paths
    script_dir = Path(__file__).parent
    download_path = script_dir / installation_file
    extract_dir = script_dir / "Image-Tea"
    
    # Confirmation prompt
    print(f"\n{'=' * 60}")
    print("Installation will:")
    print(f"  • Download: {installation_file}")
    print(f"  • Extract to: {extract_dir}")
    print(f"{'=' * 60}")
    
    response = input("\nProceed with installation? [Y/n]: ").strip().lower()
    if response and response != 'y' and response != 'yes':
        print("\n✗ Installation cancelled by user.")
        return
    
    # Create extract directory if it doesn't exist
    extract_dir.mkdir(exist_ok=True)
    
    # Download the file
    if not download_file(download_url, download_path):
        input("\nPress Enter to exit...")
        return
    
    # Extract the file
    if not extract_zip(download_path, extract_dir):
        input("\nPress Enter to exit...")
        return
    
    # Remove the zip file after successful extraction
    print(f"\n{'=' * 60}")
    print("Cleaning up...")
    print(f"{'=' * 60}")
    try:
        if download_path.exists():
            download_path.unlink()
            print(f"✓ Removed: {download_path.name}")
    except Exception as e:
        print(f"⚠ Warning: Could not remove archive: {e}")
    
    # Success message
    print(f"\n{'╔' + '═' * 58 + '╗'}")
    print(f"{'║' + ' ' * 12 + '✓ INSTALLATION COMPLETED!' + ' ' * 21 + '║'}")
    print(f"{'╚' + '═' * 58 + '╝'}")
    print(f"\n📁 Application installed to: {extract_dir.absolute()}")
    print(f"\n{'=' * 60}")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Installation cancelled by user.")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\n\n✗ An error occurred: {e}")
        input("\nPress Enter to exit...")
