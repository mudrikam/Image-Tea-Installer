import os
import json
import zipfile
import urllib.request
import urllib.error
import shutil
import tempfile
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
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
    """Download file from URL to destination"""
    print(f"Downloading from: {url}")
    print(f"Saving to: {destination}")
    
    try:
        urllib.request.urlretrieve(url, destination)
        print("Download completed!")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def extract_zip(zip_path, extract_to):
    """Extract zip file to specified directory, placing contents directly into extract_to
    (if the zip contains a single top-level directory, its children are moved up)."""
    print(f"Extracting {zip_path} to {extract_to}")
    
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

        print("Extraction completed!")
        return True
    except Exception as e:
        print(f"Error extracting file: {e}")
        return False


def cli_main():
    print("=" * 60)
    print("Image-Tea Installer")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    application_repo = config['application_repo']
    installation_file = config['installation_file']
    
    print(f"\nApplication Repository: {application_repo}")
    print(f"Installation File: {installation_file}")
    
    # Get latest release
    print("\nFetching latest release information...")
    release_info = get_latest_release(application_repo)
    
    print(f"Latest Release: {release_info['tag_name']}")
    print(f"Release Name: {release_info['name']}")
    
    # Find the installation file in assets
    download_url = None
    for asset in release_info['assets']:
        if asset['name'] == installation_file:
            download_url = asset['browser_download_url']
            break
    
    if not download_url:
        print(f"\nError: {installation_file} not found in latest release assets!")
        return
    
    # Prepare paths
    script_dir = Path(__file__).parent
    download_path = script_dir / installation_file
    extract_dir = script_dir / "Image-Tea"
    
    # Create extract directory if it doesn't exist
    extract_dir.mkdir(exist_ok=True)
    
    # Download the file
    print("\n" + "=" * 60)
    if not download_file(download_url, download_path):
        return
    
    # Extract the file
    print("\n" + "=" * 60)
    if extract_zip(download_path, extract_dir):
        print("\n" + "=" * 60)
        print("Installation completed successfully!")
        print(f"Application installed to: {extract_dir}")
        print("=" * 60)
        
        # Remove the zip file after successful extraction
        try:
            if download_path.exists():
                download_path.unlink()
                print(f"Removed downloaded archive: {download_path}")
        except Exception as e:
            print(f"Warning: failed to remove downloaded archive: {e}")
    

def download_file_with_progress(url, destination, progress_callback=None, cancel_event=None):
    """Download file with progress callback. progress_callback(percent)"""
    print(f"Downloading from: {url}")
    print(f"Saving to: {destination}")

    try:
        def reporthook(blocknum, blocksize, totalsize):
            if cancel_event and cancel_event.is_set():
                raise Exception("Download cancelled")
            if totalsize > 0:
                downloaded = blocknum * blocksize
                percent = min(downloaded / totalsize * 100, 100)
                if progress_callback:
                    progress_callback(percent)

        urllib.request.urlretrieve(url, destination, reporthook)
        if progress_callback:
            progress_callback(100)
        print("Download completed!")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        try:
            if destination.exists():
                destination.unlink()
        except Exception:
            pass
        return False


def run_install_worker(config, q, cancel_event):
    """Background worker that downloads and extracts the installation zip and reports status to queue q"""
    try:
        application_repo = config['application_repo']
        installation_file = config['installation_file']

        q.put(('status', 'Fetching latest release...'))
        release_info = get_latest_release(application_repo)

        q.put(('info', {'tag': release_info.get('tag_name'), 'name': release_info.get('name')}))

        # Find asset
        download_url = None
        for asset in release_info.get('assets', []):
            if asset.get('name') == installation_file:
                download_url = asset.get('browser_download_url')
                break

        if not download_url:
            q.put(('error', f"{installation_file} not found in latest release assets"))
            return

        script_dir = Path(__file__).parent
        download_path = script_dir / installation_file
        extract_dir = script_dir / "Image-Tea"
        extract_dir.mkdir(exist_ok=True)

        q.put(('status', 'Downloading...'))

        def progress_cb(pct):
            q.put(('progress', pct))

        if not download_file_with_progress(download_url, download_path, progress_cb, cancel_event):
            if cancel_event.is_set():
                q.put(('status', 'Cancelled'))
            else:
                q.put(('error', 'Download failed'))
            return

        if cancel_event.is_set():
            q.put(('status', 'Cancelled'))
            return

        q.put(('status', 'Extracting...'))
        if not extract_zip(download_path, extract_dir):
            q.put(('error', 'Extraction failed'))
            return

        # Remove the downloaded archive
        try:
            if download_path.exists():
                download_path.unlink()
        except Exception:
            pass

        q.put(('progress', 100))
        q.put(('status', 'Installation completed successfully'))
        q.put(('done', None))
    except Exception as e:
        q.put(('error', str(e)))


def launch_gui():
    root = tk.Tk()
    root.title('Download and Install Image Tea')

    cfg = load_config()

    frm = ttk.Frame(root, padding=12)
    frm.grid(row=0, column=0, sticky='nsew')

    ttk.Label(frm, text='Repository:').grid(row=0, column=0, sticky='w')
    repo_lbl = ttk.Label(frm, text=cfg['application_repo'])
    repo_lbl.grid(row=0, column=1, sticky='w')

    ttk.Label(frm, text='Installation File:').grid(row=1, column=0, sticky='w')
    file_lbl = ttk.Label(frm, text=cfg['installation_file'])
    file_lbl.grid(row=1, column=1, sticky='w')

    ttk.Label(frm, text='Release:').grid(row=2, column=0, sticky='w')
    release_lbl = ttk.Label(frm, text='-')
    release_lbl.grid(row=2, column=1, sticky='w')

    progress = ttk.Progressbar(frm, orient='horizontal', length=360, mode='determinate', maximum=100)
    progress.grid(row=3, column=0, columnspan=2, pady=(10, 0))

    status_lbl = ttk.Label(frm, text='Idle')
    status_lbl.grid(row=4, column=0, columnspan=2, sticky='w', pady=(6, 0))

    # Make column 1 expand so controls on the right can align
    frm.columnconfigure(1, weight=1)

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=5, column=1, sticky='e', pady=(10, 0))

    start_btn = ttk.Button(btn_frame, text='Start')
    start_btn.grid(row=0, column=0, padx=(0, 6))
    cancel_btn = ttk.Button(btn_frame, text='Cancel')
    cancel_btn.grid(row=0, column=1)

    q = queue.Queue()
    cancel_event = threading.Event()
    worker_thread = {'t': None}

    def on_start():
        start_btn.config(state='disabled')
        cancel_btn.config(state='normal')
        progress['value'] = 0
        status_lbl.config(text='Starting...')
        cancel_event.clear()
        worker = threading.Thread(target=run_install_worker, args=(cfg, q, cancel_event), daemon=True)
        worker_thread['t'] = worker
        worker.start()
        root.after(100, poll_queue)

    def on_cancel():
        cancel_event.set()
        status_lbl.config(text='Cancelling...')

    def poll_queue():
        try:
            while True:
                msg, val = q.get_nowait()
                if msg == 'progress':
                    progress['value'] = val
                elif msg == 'status':
                    status_lbl.config(text=val)
                elif msg == 'info':
                    release_lbl.config(text=f"{val.get('tag')} - {val.get('name')}")
                elif msg == 'error':
                    messagebox.showerror('Error', val)
                    start_btn.config(state='normal')
                    cancel_btn.config(state='disabled')
                elif msg == 'done':
                    messagebox.showinfo('Done', 'Installation completed successfully')
                    start_btn.config(state='normal')
                    cancel_btn.config(state='disabled')
        except queue.Empty:
            # no messages
            pass
        # if worker still alive, continue polling
        t = worker_thread.get('t')
        if t and t.is_alive():
            root.after(100, poll_queue)
        else:
            start_btn.config(state='normal')
            cancel_btn.config(state='disabled')

    start_btn.config(command=on_start)
    cancel_btn.config(command=on_cancel)
    cancel_btn.config(state='disabled')

    root.protocol('WM_DELETE_WINDOW', lambda: (cancel_event.set(), root.destroy()))

    # Center window on screen at first display
    try:
        root.update_idletasks()
        w = root.winfo_width()
        h = root.winfo_height()
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        # If centering fails for any reason, proceed without failing
        pass

    root.mainloop()


if __name__ == "__main__":
    try:
        launch_gui()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
