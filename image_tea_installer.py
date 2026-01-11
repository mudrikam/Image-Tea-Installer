import os
import json
import zipfile
import urllib.request
import urllib.error
import shutil
import tempfile
import sys
import subprocess
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


INSTALLER_VERSION = "1.0.0"


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
    top = '╔' + '═' * (width - 2) + '╗'
    middle = '║' + ' ' * ((width - len(text) - 2) // 2) + text + ' ' * ((width - len(text) - 1) // 2) + '║'
    bottom = '╚' + '═' * (width - 2) + '╝'
    print(f"\n{Colors.CYAN}{Colors.BOLD}{top}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{middle}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{bottom}{Colors.RESET}")


def truncate_middle(s: str, maxlen: int) -> str:
    """Truncate string in the middle with '...' so total length <= maxlen."""
    if len(s) <= maxlen:
        return s
    if maxlen <= 3:
        return s[:maxlen]
    # split remaining length evenly
    rem = maxlen - 3
    left = rem // 2
    right = rem - left
    return s[:left] + '...' + s[-right:]


def print_frame(title, content_lines, color=Colors.CYAN, style='double'):
    """
    Generic frame printer
    title: Frame title (can be empty string for no title)
    content_lines: List of strings to display inside frame
    color: ANSI color code
    style: 'double' (╔═╗) or 'single' (┌─┐)
    """
    if not content_lines:
        return

    # Choose border characters
    if style == 'double':
        tl, tr, bl, br, h, v = '╔', '╗', '╚', '╝', '═', '║'
    else:
        tl, tr, bl, br, h, v = '┌', '┐', '└', '┘', '─', '│'

    # Maximum inner content width (inner chars excluding borders)
    MAX_INNER = 66  # total width - 4 for borders and padding

    # Truncate long lines to keep frames compact
    processed = []
    for line in ([title] if title else []) + content_lines:
        processed.append(truncate_middle(line, MAX_INNER))

    all_lines = processed
    max_len = max(len(line) for line in all_lines)
    width = max(70, max_len + 4)

    # Build frame
    top = tl + h * (width - 2) + tr
    lines_output = []

    if title:
        tline = processed[0]
        pad = width - len(tline) - 3
        lines_output.append(v + ' ' + tline + ' ' * pad + v)
        content_start = 1
    else:
        content_start = 0

    for line in processed[content_start:]:
        pad = width - len(line) - 3
        lines_output.append(v + ' ' + line + ' ' * pad + v)

    bottom = bl + h * (width - 2) + br

    # Print frame
    print(f"{color}{top}{Colors.RESET}")
    for line in lines_output:
        print(f"{color}{line}{Colors.RESET}")
    print(f"{color}{bottom}{Colors.RESET}")


def load_config():
    """Load configuration from installer_configs.json

    When packaged with PyInstaller using --onefile, data files are extracted
    to a temporary folder accessible via sys._MEIPASS. Use that path when
    available so the bundled config can be found at runtime.
    """
    base = getattr(sys, '_MEIPASS', None)
    if base:
        config_path = Path(base) / "installer_configs.json"
    else:
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
    lines = [
        f"URL:         {url}",
        f"Destination: {destination}",
        ""
    ]
    print_frame("DOWNLOADING", lines, Colors.YELLOW, 'single')
    
    try:
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(int(downloaded / total_size * 100), 100)
                bar_length = 50
                filled = int(bar_length * percent / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                
                sys.stdout.write(f'\r{Colors.GREEN}[{bar}]{Colors.RESET} {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)')
                sys.stdout.flush()
                
                if downloaded >= total_size:
                    print()
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        # Show completion inside a small frame
        print_frame("DOWNLOAD", ["[+] Download completed!"], Colors.GREEN, 'single')
        return True
    except Exception as e:
        print_frame("DOWNLOAD", [f"[!] Error downloading file: {e}"], Colors.RED, 'single')
        return False


def extract_zip(zip_path, extract_to):
    """Extract zip file to specified directory, placing contents directly into extract_to
    (if the zip contains a single top-level directory, its children are moved up)."""
    lines = [
        f"Archive: {zip_path}",
        f"Target:  {extract_to}",
        ""
    ]
    print_frame("EXTRACTING", lines, Colors.YELLOW, 'single')
    
    try:
        # Ensure target directory exists
        extract_to.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(dir=extract_to.parent) as tmpdir:
            tmp_path = Path(tmpdir)
            

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_path)
            entries = list(tmp_path.iterdir())
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

        # Show extraction status inside a frame
        status_lines = [
            "[+] Extracting archive... Done",
            "[+] Moving files... Done",
            "[+] Extraction completed!"
        ]
        print_frame("EXTRACTING STATUS", status_lines, Colors.GREEN, 'single')
        return True
    except Exception as e:
        print_frame("EXTRACTING STATUS", [f"[!] Error extracting file: {e}"], Colors.RED, 'single')
        return False


def uninstall(extract_dir: Path) -> bool:
    """Uninstall Image Tea with safety confirmations"""
    if not extract_dir.exists():
        print_frame("UNINSTALL", ["[!] Image Tea is not installed."], Colors.RED, 'single')
        return False
    
    # Show warning frame
    warning_lines = [
        "WARNING: This will permanently delete:",
        "",
        f"Folder: {extract_dir.absolute()}",
        "",
        "All files and subdirectories will be removed.",
        "This action CANNOT be undone!"
    ]
    print_frame("UNINSTALL WARNING", warning_lines, Colors.RED, 'double')
    
    # First confirmation
    while True:
        print(f"{Colors.BOLD}Are you sure you want to uninstall? [{Colors.RED}Y{Colors.RESET}/{Colors.GREEN}N{Colors.RESET}]: {Colors.RESET}", end='', flush=True)
        r1 = getch()
        print(r1)
        if r1 in ['n', 'N', '\r', '\n', '']:
            print_frame("UNINSTALL", ["[+] Uninstall cancelled."], Colors.GREEN, 'single')
            return False
        if r1 in ['y', 'Y']:
            break
    
    # Second confirmation
    while True:
        print(f"{Colors.BOLD}Final confirmation - Delete Image Tea folder? [{Colors.RED}Y{Colors.RESET}/{Colors.GREEN}N{Colors.RESET}]: {Colors.RESET}", end='', flush=True)
        r2 = getch()
        print(r2)
        if r2 in ['n', 'N', '\r', '\n', '']:
            print_frame("UNINSTALL", ["[+] Uninstall cancelled."], Colors.GREEN, 'single')
            return False
        if r2 in ['y', 'Y']:
            break
    
    # Perform uninstall
    try:
        shutil.rmtree(extract_dir)
        print_frame("UNINSTALL", ["[+] Image Tea has been successfully uninstalled."], Colors.GREEN, 'double')
        return True
    except Exception as e:
        print_frame("UNINSTALL", [f"[!] Error during uninstall: {e}"], Colors.RED, 'double')
        return False


def run_launcher(extract_dir: Path) -> bool:
    """Attempt to run the project's launcher depending on platform.
    Returns True if a launcher was found and launched, False otherwise."""
    # Windows -> Launcher.bat
    if sys.platform.startswith('win'):
        launcher = extract_dir / 'Launcher.bat'
        if not launcher.exists():
            return False
        try:
            # Use shell to allow .bat to run properly
            subprocess.Popen([str(launcher)], cwd=extract_dir, shell=True)
            return True
        except Exception:
            return False

    # macOS/Linux -> Launcher.sh (or executable 'Launcher')
    else:
        launcher_sh = extract_dir / 'Launcher.sh'
        launcher_bin = extract_dir / 'Launcher'
        target = None
        if launcher_sh.exists():
            target = launcher_sh
        elif launcher_bin.exists():
            target = launcher_bin

        if not target:
            return False

        try:
            # Ensure executable
            try:
                mode = target.stat().st_mode
                if not (mode & 0o111):
                    target.chmod(mode | 0o111)
            except Exception:
                pass
            subprocess.Popen(['sh', str(target)], cwd=extract_dir)
            return True
        except Exception:
            return False


def main():
    """Main setup function with enhanced CLI interface"""
    # Enable ANSI colors on Windows
    if sys.platform == 'win32':
        os.system('')

    # Load configuration first so we can show the installer version in the header
    try:
        config = load_config()
        application_repo = config['application_repo']
        installation_file = config['installation_file']
        installer_version = config.get('installer_version', INSTALLER_VERSION)
    except Exception as e:
        # Print header with default version when config can't be loaded
        print_header(f"IMAGE-TEA SETUP v{INSTALLER_VERSION}")
        lines = [f"[!] Error loading configuration: {e}"]
        print_frame("ERROR", lines, Colors.RED, 'double')
        input("Press Enter to exit...")
        return

    # Now print header including detected installer version
    print_header(f"IMAGE-TEA SETUP v{installer_version}")
    
    # Application info frame
    lines = [
        f"Application:  {application_repo.split('/')[-1]}",
        f"Repository:   {application_repo}",
        f"Package:      {installation_file}",
        f"Installer:    {installer_version}"
    ]
    print_frame("APPLICATION INFO", lines, Colors.CYAN, 'double')
    
    # Prepare paths early for detection
    # When running as PyInstaller executable, use the exe location, not __file__ (which points to temp)
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use executable's directory
        script_dir = Path(sys.executable).parent
    else:
        # Running as normal Python script
        script_dir = Path(__file__).parent
    
    download_path = script_dir / installation_file
    extract_dir = script_dir / "Image-Tea"
    
    # Check if already installed
    if extract_dir.exists() and any(extract_dir.iterdir()):
        lines = [
            "Image Tea is already installed!",
            "",
            f"Location: {extract_dir.absolute()}",
            "",
            "Options:",
            "  [L] Launch Image Tea now",
            "  [R] Reinstall (download and setup again)",
            "  [U] Uninstall (delete Image Tea folder)",
            "  [X] Exit"
        ]
        print_frame("ALREADY INSTALLED", lines, Colors.GREEN, 'double')
        
        while True:
            print(f"{Colors.BOLD}Choose option [{Colors.GREEN}L{Colors.RESET}/{Colors.YELLOW}R{Colors.RESET}/{Colors.RED}U{Colors.RESET}/{Colors.CYAN}X{Colors.RESET}]: {Colors.RESET}", end='', flush=True)
            choice = getch()
            print(choice)
            
            if choice in ['l', 'L']:
                launched = run_launcher(extract_dir)
                if launched:
                    print_frame("LAUNCH", ["[+] Launched Image Tea."], Colors.GREEN, 'single')
                else:
                    print_frame("LAUNCH", ["[!] Launcher not found or failed to start."], Colors.RED, 'single')
                return
            elif choice in ['r', 'R']:
                print_frame("REINSTALL", ["[+] Proceeding with reinstall..."], Colors.YELLOW, 'single')
                break  # Continue with normal setup process
            elif choice in ['u', 'U']:
                if uninstall(extract_dir):
                    return
                else:
                    continue  # Return to options menu
            elif choice in ['x', 'X', '\r', '\n', '']:
                print_frame("EXIT", ["[+] Setup cancelled."], Colors.CYAN, 'single')
                return
    
    # Get latest release
    try:
        release_info = get_latest_release(application_repo)
        lines = [
            f"Version:   {release_info['tag_name']}",
            f"Name:      {release_info['name']}",
            f"Published: {release_info.get('published_at', 'N/A')}"
        ]
    except Exception as e:
        lines = [f"[!] Error fetching release information: {e}"]
        print_frame("ERROR", lines, Colors.RED, 'double')
        input("Press Enter to exit...")
        return
    
    # Find the installation file in assets
    download_url = None
    for asset in release_info['assets']:
        if asset['name'] == installation_file:
            download_url = asset['browser_download_url']
            file_size = asset.get('size', 0)
            lines.append(f"Size:      {file_size / (1024 * 1024):.2f} MB")
            break
    
    print_frame("RELEASE INFO", lines, Colors.GREEN, 'double')
    
    if not download_url:
        lines = [f"[!] Error: {installation_file} not found in latest release assets!"]
        print_frame("ERROR", lines, Colors.RED, 'double')
        input("Press Enter to exit...")
        return
    
# Confirmation prompt (frame contains only the plan; prompt is outside)
    lines = [
        f"> Download: {installation_file}",
        f"> Extract to: {extract_dir}"
    ]
    print_frame("SETUP PLAN", lines, Colors.YELLOW, 'double')

    # Prompt outside frame, accept Y/N (uppercase shown) — instant keypress
    while True:
        print(f"{Colors.BOLD}Proceed with setup? [{Colors.GREEN}Y{Colors.RESET}/{Colors.RED}N{Colors.RESET}]: {Colors.RESET}", end='', flush=True)
        response = getch()
        print(response)
        if response in ['y', 'Y', '\r', '\n', '']:
            proceed = True
            break
        if response in ['n', 'N']:
            proceed = False
            break
        # ignore other keys and loop again

    if not proceed:
        lines = ["Setup cancelled by user."]
        print_frame("CANCELLED", lines, Colors.RED, 'double')
        return
    
    # Create extract directory if it doesn't exist
    extract_dir.mkdir(exist_ok=True)
    
    # Download the file
    if not download_file(download_url, download_path):
        input("Press Enter to exit...")
        return
    
    # Extract the file
    if not extract_zip(download_path, extract_dir):
        input("Press Enter to exit...")
        return
    
    # Remove the zip file after successful extraction
    lines = []
    try:
        if download_path.exists():
            download_path.unlink()
            lines.append(f"[+] Removed: {download_path.name}")
    except Exception as e:
        lines.append(f"[!] Warning: Could not remove archive: {e}")
    
    print_frame("CLEANING UP", lines, Colors.YELLOW, 'single')
    
    # Success message
    lines = [
        "SETUP COMPLETED!",
        "",
        f"Application installed to: {extract_dir.absolute()}"
    ]
    print_frame("SUCCESS", lines, Colors.GREEN, 'double')
    
    # Prompt to run application now (outside frame)
    while True:
        print(f"{Colors.BOLD}Run Image Tea now? [{Colors.GREEN}Y{Colors.RESET}/{Colors.RED}N{Colors.RESET}]: {Colors.RESET}", end='', flush=True)
        r = getch()
        print(r)
        if r in ['y', 'Y', '\r', '\n', '']:
            launched = run_launcher(extract_dir)
            if launched:
                print_frame("LAUNCH", ["[+] Launched Image Tea."], Colors.GREEN, 'single')
            else:
                print_frame("LAUNCH", ["[!] Launcher not found or failed to start."], Colors.RED, 'single')
            break
        if r in ['n', 'N']:
            break
        # otherwise loop until valid key pressed


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        lines = ["Setup cancelled by user."]
        print_frame("CANCELLED", lines, Colors.RED, 'double')
        input(f"{Colors.DIM}Press Enter to exit...{Colors.RESET}")
    except Exception as e:
        lines = [f"An error occurred: {e}"]
        print_frame("ERROR", lines, Colors.RED, 'double')
        input(f"{Colors.DIM}Press Enter to exit...{Colors.RESET}")
