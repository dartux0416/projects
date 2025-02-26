#!/bin/bash

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Define some variables
SCRIPT_NAME="backup.py"
INSTALL_DIR="/usr/local/bin"
CONFIG_FILE="/etc/backup-config.conf"
LOG_DIR="/var/log"
BIN_NAME="backup"

# Function to display messages with colors
info() {
    echo -e "${GREEN}[INFO] $1${RESET}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${RESET}"
}

error() {
    echo -e "${RED}[ERROR] $1${RESET}"
}

# Check if the script is being run as root
if [ "$(id -u)" -ne 0 ]; then
    error "This script must be run as root."
    echo -e "${RED}Exiting...${RESET}"
    exit 1
fi

# Remove the backup script
info "Removing the backup script from $INSTALL_DIR..."
if [ -f "$INSTALL_DIR/$BIN_NAME" ]; then
    sudo rm "$INSTALL_DIR/$BIN_NAME"
    info "Backup script removed from $INSTALL_DIR."
else
    warning "Backup script not found at $INSTALL_DIR."
fi

# Remove the symbolic link
info "Removing the symbolic link for 'backup' command..."
if [ -L "/usr/local/bin/$BIN_NAME" ]; then
    sudo rm "/usr/local/bin/$BIN_NAME"
    info "Symbolic link removed from /usr/local/bin."
else
    warning "Symbolic link not found in /usr/local/bin."
fi

# Remove the configuration file
info "Removing the configuration file $CONFIG_FILE..."
if [ -f "$CONFIG_FILE" ]; then
    sudo rm "$CONFIG_FILE"
    info "Configuration file removed."
else
    warning "Configuration file not found at $CONFIG_FILE."
fi

# Remove the log directory if empty
info "Checking and removing the log directory if empty..."
if [ -d "$LOG_DIR" ]; then
    if [ -z "$(ls -A $LOG_DIR)" ]; then
        sudo rmdir "$LOG_DIR"
        info "Log directory removed."
    else
        info "Log directory not empty, skipping removal."
    fi
else
    warning "Log directory not found."
fi

# Completion message
info "Uninstallation complete! All changes made by the installation script have been undone."

# Exit
exit 0
