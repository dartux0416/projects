#!/usr/bin/env python3

import os
import zipfile
import tarfile
import subprocess
from colorama import Fore, init
from configparser import ConfigParser
from tqdm import tqdm  # For progress bar
from datetime import datetime
import argparse

# Initialize colorama
init(autoreset=True)

# Colors
COLOR_ERROR = Fore.RED
COLOR_DIR = Fore.CYAN
COLOR_SUCCESS = Fore.GREEN

files_to_zip = []
CONFIG_FILE = "/etc/backup/backup-config.conf"
LOG_DIR = "/var/log/"
LOG_FILE = os.path.join(LOG_DIR, "backup.log")


def log(message):
    """Log a message to the console and the log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)

    # Ensure the log directory exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, mode=0o755)  # Create the directory with appropriate permissions

    # Append to the log file
    with open(LOG_FILE, "a") as f:
        f.write(log_message + "\n")


def parse_human_readable_size(size_str):
    """Convert human-readable size (e.g., 2M, 4G, 1K) into bytes."""
    size_str = size_str.strip().upper()
    multiplier = 1
    if size_str.endswith('K'):
        multiplier = 1024
        size_str = size_str[:-1]
    elif size_str.endswith('M'):
        multiplier = 1024 ** 2
        size_str = size_str[:-1]
    elif size_str.endswith('G'):
        multiplier = 1024 ** 3
        size_str = size_str[:-1]
    try:
        return int(size_str) * multiplier
    except ValueError:
        raise ValueError(f"Invalid size format: {size_str}")


def load_config(config_file):
    """Load configuration settings from the config file."""
    config = ConfigParser()
    config.read(config_file)

    try:
        base_folder = config.get("Backup", "BASE_FOLDER")
        exclude = [item.strip() for item in config.get("Backup", "EXCLUDE", fallback="").split(",") if item.strip()]
        exclude_prefix = [item.strip() for item in config.get("Backup", "EXCLUDE_PREFIX", fallback="").split(",") if item.strip()]
        exclude_suffix = [item.strip() for item in config.get("Backup", "EXCLUDE_SUFFIX", fallback="").split(",") if item.strip()]
        backup_filename = config.get("Backup", "BACKUP_FILENAME")
        backup_type = config.get("Backup", "TYPE").lower()

        # Parse max size
        max_size = config.get("Backup", "MAX_SIZE", fallback="0").strip()
        max_size = parse_human_readable_size(max_size) if max_size else 0

        remote_backup = config.getboolean("RemoteBackup", "ENABLE", fallback=False)
        remote_server = config.get("RemoteBackup", "SERVER", fallback="")
        remote_user = config.get("RemoteBackup", "REMOTE_USER", fallback="")
        remote_path = config.get("RemoteBackup", "REMOTE_PATH", fallback="")
        rsync_options = config.get("RemoteBackup", "RSYNC_OPTIONS", fallback="").strip()
        remote_password = config.get("RemoteBackup", "PASSWORD", fallback="")

        return (base_folder, exclude, exclude_prefix, exclude_suffix,
                backup_filename, backup_type, max_size, 
                remote_backup, remote_server, remote_user, remote_path, rsync_options, remote_password)

    except Exception as e:
        print(COLOR_ERROR + f"Error reading config file: {e}")
        exit(1)


def manual_config():
    """Allow user to manually configure the backup config file."""
    print(COLOR_SUCCESS + "Manual configuration setup:")

    config = ConfigParser()

    # Load the existing configuration to avoid overwriting it
    config.read(CONFIG_FILE)

    # Ensure Backup and RemoteBackup sections exist
    if not config.has_section('Backup'):
        config.add_section('Backup')
    
    if not config.has_section('RemoteBackup'):
        config.add_section('RemoteBackup')

    # Backup section
    base_folder = input(f"Enter the base folder to backup (current: {load_config(CONFIG_FILE)[0]}): ").strip()
    if base_folder:
        config.set('Backup', 'BASE_FOLDER', base_folder)
    
    exclude = input(f"Enter a comma-separated list of files to exclude (current: {', '.join(load_config(CONFIG_FILE)[1])}): ").strip()
    if exclude:
        config.set('Backup', 'EXCLUDE', exclude)

    exclude_prefix = input(f"Enter a comma-separated list of file prefix exclusions (current: {', '.join(load_config(CONFIG_FILE)[2])}): ").strip()
    if exclude_prefix:
        config.set('Backup', 'EXCLUDE_PREFIX', exclude_prefix)

    exclude_suffix = input(f"Enter a comma-separated list of file suffix exclusions (current: {', '.join(load_config(CONFIG_FILE)[3])}): ").strip()
    if exclude_suffix:
        config.set('Backup', 'EXCLUDE_SUFFIX', exclude_suffix)

    backup_filename = input(f"Enter the backup filename (current: {load_config(CONFIG_FILE)[4]}): ").strip()
    if backup_filename:
        config.set('Backup', 'BACKUP_FILENAME', backup_filename)

    backup_type = input(f"Enter the backup type (zip or tar, current: {load_config(CONFIG_FILE)[5]}): ").strip().lower()
    if backup_type:
        config.set('Backup', 'TYPE', backup_type)
    
    max_size = input(f"Enter the max file size for backup (e.g., 2M, 500K, 5G, current: {load_config(CONFIG_FILE)[6]}): ").strip()
    if max_size:  # Only update if the user enters a value
        config.set('Backup', 'MAX_SIZE', max_size)

    # Remote Backup section
    enable_remote = input(f"Enable remote backup? (yes/no, current: {load_config(CONFIG_FILE)[7]}): ").strip().lower()
    if enable_remote == 'yes' or enable_remote == 'y':
        config.set('RemoteBackup', 'ENABLE', 'True')
    else:
        config.set('RemoteBackup', 'ENABLE', 'False')

    # Always ask for remote backup server details
    remote_server = input(f"Enter the remote server address (current: {load_config(CONFIG_FILE)[8]}): ").strip()
    if remote_server:
        config.set('RemoteBackup', 'SERVER', remote_server)

    remote_user = input(f"Enter the remote user (current: {load_config(CONFIG_FILE)[9]}): ").strip()
    if remote_user:
        config.set('RemoteBackup', 'REMOTE_USER', remote_user)

    remote_path = input(f"Enter the remote path (current: {load_config(CONFIG_FILE)[10]}): ").strip()
    if remote_path:
        config.set('RemoteBackup', 'REMOTE_PATH', remote_path)

    rsync_options = input(f"Enter rsync options (current: {load_config(CONFIG_FILE)[11]}): ").strip()
    if rsync_options:
        config.set('RemoteBackup', 'RSYNC_OPTIONS', rsync_options)

    remote_password = input(f"Enter the remote server password (current: {load_config(CONFIG_FILE)[12]}): ").strip()
    if remote_password:
        config.set('RemoteBackup', 'PASSWORD', remote_password)

    # Write the configuration file
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    
    print(COLOR_SUCCESS + f"Configuration file saved to {CONFIG_FILE}")




def list_rec(dir, exclude, exclude_prefix, exclude_suffix, max_size):
    """Recursively list files for backup, applying exclusions."""
    try:
        entries = os.listdir(dir)

        for entry in entries:
            path = os.path.join(dir, entry)

            if (
                entry in exclude or
                any(entry.lower().startswith(prefix.lower()) for prefix in exclude_prefix) or
                any(entry.lower().endswith(suffix.lower()) for suffix in exclude_suffix)
            ):
                log(f"Excluding {path} (matched exclude list)")
                continue

            if os.path.isfile(path):
                if max_size and os.path.getsize(path) > max_size:
                    log(f"Excluding {path} (size exceeds max size: {max_size} bytes)")
                    continue
                files_to_zip.append(path)
            elif os.path.isdir(path):
                list_rec(path, exclude, exclude_prefix, exclude_suffix, max_size)

    except PermissionError:
        log(f" - [Permission Denied] {dir}")
    except FileNotFoundError:
        log(f"Directory not found: {dir}")
    except Exception as e:
        log(f"An error occurred: {e}")


def zip_rec(zip_filename, base_dir):
    """Create a ZIP file containing all files to backup."""
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in tqdm(files_to_zip, desc="Creating ZIP backup", unit="files"):
                relative_path = os.path.relpath(file, base_dir)
                zipf.write(file, relative_path)
        log(f"Successfully created zip file: {zip_filename}")
    except Exception as e:
        log(f"An error occurred while zipping: {e}")


def tar_rec(tar_filename, base_dir):
    """Create a TAR file containing all files to backup."""
    try:
        with tarfile.open(tar_filename, 'w:gz') as tarf:
            for file in tqdm(files_to_zip, desc="Creating TAR backup", unit="files"):
                relative_path = os.path.relpath(file, base_dir)
                tarf.add(file, relative_path)
        log(f"Successfully created tar file: {tar_filename}")
    except Exception as e:
        log(f"An error occurred while tarring: {e}")


def rsync_backup(local_file, remote_server, remote_user, remote_path, rsync_options, password):
    """Perform a remote backup using rsync."""
    try:
        if "@" not in remote_server:
            remote_destination = f"{remote_user}@{remote_server}:{remote_path}"
        else:
            remote_destination = f"{remote_server}:{remote_path}"

        rsync_command = f"sshpass -p '{password}' rsync {rsync_options} {local_file} {remote_destination}"
        log(f"Running rsync command: {rsync_command}")
        subprocess.run(rsync_command, shell=True, check=True)
        log(f"Successfully copied backup to remote server: {remote_destination}")
    except subprocess.CalledProcessError as e:
        log(f"An error occurred while copying to remote server: {e}")
    except Exception as e:
        log(f"An unexpected error occurred during rsync: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup script")
    parser.add_argument('--manual-config', action='store_true', help="Manually configure the backup config")
    args = parser.parse_args()

    if args.manual_config:
        manual_config()
        exit(0)

    if not os.path.exists(CONFIG_FILE):
        log(f"Config file not found: {CONFIG_FILE}")
        exit(1)

    (base_folder, exclude, exclude_prefix, exclude_suffix,
     backup_filename, backup_type, max_size, 
     remote_backup, remote_server, remote_user, remote_path, rsync_options, remote_password) = load_config(CONFIG_FILE)

    if not os.path.exists(base_folder):
        log(f"Invalid directory path: {base_folder}")
        exit(1)

    log(f"Starting backup of {base_folder} at {datetime.now()}")
    list_rec(base_folder, exclude, exclude_prefix, exclude_suffix, max_size)

    backup_file = os.path.expanduser(backup_filename)
    if not os.path.isabs(backup_file):
        backup_file = os.path.join(os.getcwd(), backup_file)

    if backup_type == "zip":
        backup_file += ".zip"
        zip_rec(backup_file, base_folder)
    elif backup_type == "tar":
        backup_file += ".tar"
        tar_rec(backup_file, base_folder)
    else:
        log("Invalid backup type in config file")

    if remote_backup:
        rsync_backup(backup_file, remote_server, remote_user, remote_path, rsync_options, remote_password)
