import os
import json
import zipfile
import urllib.request
import urllib.error
import shutil
import tempfile
import sys
from pathlib import Path

# Platform-specific imports for keypress detection
if sys.platform == 'win32':
    import msvcrt
else:
    import tty
    import termios


# ANSI Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


def getch():
    """Get single character input without Enter"""
    if sys.platform == 'win32':
        return msvcrt.getch().decode('utf-8', errors='ignore').lower()
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def print_header(text):
    """Print styled header box"""
    width = 70
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * width}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}|{' ' * ((width - len(text) - 2) // 2)}{text}{' ' * ((width - len(text) - 1) // 2)}|{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * width}{Colors.RESET}\n")


def print_box(text, color=Colors.GREEN):
    """Print text in a colored box"""
    width = 70
    print(f"\n{color}{'=' * width}{Colors.RESET}")
    print(f"{color}| {text}{' ' * (width - len(text) - 3)}|{Colors.RESET}")
    print(f"{color}{'=' * width}{Colors.RESET}\n")


def print_section(title):
    """Print section separator"""
    print(f"\n{Colors.YELLOW}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.YELLOW}{title}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'=' * 70}{Colors.RESET}")


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
    print_section("DOWNLOADING")
    print(f"{Colors.CYAN}URL:         {Colors.WHITE}{url}{Colors.RESET}")
    print(f"{Colors.CYAN}Destination: {Colors.WHITE}{destination}{Colors.RESET}")
    print()
    
    try:
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(int(downloaded / total_size * 100), 100)
                bar_length = 50
                filled = int(bar_length * percent / 100)
                bar = '#' * filled + '-' * (bar_length - filled)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                
                sys.stdout.write(f'\r{Colors.GREEN}[{bar}] {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB){Colors.RESET}')
                sys.stdout.flush()
                
                if downloaded >= total_size:
                    print()
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print(f"\n{Colors.GREEN}[+] Download completed!{Colors.RESET}")
        return True
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error downloading file: {e}{Colors.RESET}")
        return False


def extract_zip(zip_path, extract_to):
    """Extract zip file to specified directory, placing contents directly into extract_to
    (if the zip contains a single top-level directory, its children are moved up)."""
    print_section("EXTRACTING")
    print(f"{Colors.CYAN}Archive: {Colors.WHITE}{zip_path}{Colors.RESET}")
    print(f"{Colors.CYAN}Target:  {Colors.WHITE}{extract_to}{Colors.RESET}")
    print()
    
    try:
        # Ensure target directory exists
        extract_to.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(dir=extract_to.parent) as tmpdir:
            tmp_path = Path(tmpdir)
            
            print(f"{Colors.YELLOW}[*] Extracting archive...{Colors.RESET}", end='', flush=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_path)
            print(f"\r{Colors.GREEN}[+] Extracting archive... Done{Colors.RESET}")

            entries = list(tmp_path.iterdir())

            print(f"{Colors.YELLOW}[*] Moving files...{Colors.RESET}", end='', flush=True)
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
            print(f"\r{Colors.GREEN}[+] Moving files... Done     {Colors.RESET}")

        print(f"\n{Colors.GREEN}[+] Extraction completed!{Colors.RESET}")
        return True
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error extracting file: {e}{Colors.RESET}")
        return False


def main():
    """Main installer function with enhanced CLI interface"""
    # Enable ANSI colors on Windows
    if sys.platform == 'win32':
        os.system('')
    
    print_header("IMAGE-TEA INSTALLER")
    
    # Load configuration
    try:
        config = load_config()
        application_repo = config['application_repo']
        installation_file = config['installation_file']
    except Exception as e:
        print(f"{Colors.RED}[!] Error loading configuration: {e}{Colors.RESET}")
        input("\nPress Enter to exit...")
        return
    
    print(f"{Colors.CYAN}Application:{Colors.RESET}  {Colors.WHITE}{application_repo.split('/')[-1]}{Colors.RESET}")
    print(f"{Colors.CYAN}Repository:{Colors.RESET}   {Colors.WHITE}{application_repo}{Colors.RESET}")
    print(f"{Colors.CYAN}Package:{Colors.RESET}      {Colors.WHITE}{installation_file}{Colors.RESET}")
    
    # Get latest release
    print_section("FETCHING RELEASE INFORMATION")
    
    try:
        release_info = get_latest_release(application_repo)
        print(f"{Colors.GREEN}[+] Found release:{Colors.RESET}")
        print(f"    {Colors.CYAN}Version:{Colors.RESET}   {Colors.WHITE}{release_info['tag_name']}{Colors.RESET}")
        print(f"    {Colors.CYAN}Name:{Colors.RESET}      {Colors.WHITE}{release_info['name']}{Colors.RESET}")
        print(f"    {Colors.CYAN}Published:{Colors.RESET} {Colors.WHITE}{release_info.get('published_at', 'N/A')}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[!] Error fetching release information: {e}{Colors.RESET}")
        input("\nPress Enter to exit...")
        return
    
    # Find the installation file in assets
    download_url = None
    for asset in release_info['assets']:
        if asset['name'] == installation_file:
            download_url = asset['browser_download_url']
            file_size = asset.get('size', 0)
            print(f"    {Colors.CYAN}Size:{Colors.RESET}      {Colors.WHITE}{file_size / (1024 * 1024):.2f} MB{Colors.RESET}")
            break
    
    if not download_url:
        print(f"{Colors.RED}[!] Error: {installation_file} not found in latest release assets!{Colors.RESET}")
        input("\nPress Enter to exit...")
        return
    
    # Prepare paths
    script_dir = Path(__file__).parent
    download_path = script_dir / installation_file
    extract_dir = script_dir / "Image-Tea"
    
    # Confirmation prompt
    print(f"\n{Colors.YELLOW}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.YELLOW}Installation will:{Colors.RESET}")
    print(f"  {Colors.CYAN}>{Colors.RESET} Download: {Colors.WHITE}{installation_file}{Colors.RESET}")
    print(f"  {Colors.CYAN}>{Colors.RESET} Extract to: {Colors.WHITE}{extract_dir}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'=' * 70}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Proceed with installation? [{Colors.GREEN}Y{Colors.RESET}{Colors.BOLD}/{Colors.RED}n{Colors.RESET}{Colors.BOLD}]:{Colors.RESET} ", end='', flush=True)
    
    response = getch()
    print(response)  # Echo the character
    
    if response not in ['y', 'Y', '\r', '\n', '']:
        print(f"\n{Colors.RED}[!] Installation cancelled by user.{Colors.RESET}")
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
    print_section("CLEANING UP")
    try:
        if download_path.exists():
            download_path.unlink()
            print(f"{Colors.GREEN}[+] Removed: {Colors.WHITE}{download_path.name}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Warning: Could not remove archive: {e}{Colors.RESET}")
    
    # Success message
    print_box("INSTALLATION COMPLETED!", Colors.GREEN)
    print(f"{Colors.CYAN}Application installed to:{Colors.RESET} {Colors.WHITE}{extract_dir.absolute()}{Colors.RESET}\n")
    
    input(f"{Colors.DIM}Press Enter to exit...{Colors.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}[!] Installation cancelled by user.{Colors.RESET}")
        input(f"\n{Colors.DIM}Press Enter to exit...{Colors.RESET}")
    except Exception as e:
        print(f"\n\n{Colors.RED}[!] An error occurred: {e}{Colors.RESET}")
        input(f"\n{Colors.DIM}Press Enter to exit...{Colors.RESET}")
