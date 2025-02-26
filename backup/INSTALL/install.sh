#!/bin/bash

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Define paths for installation
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="/etc/backup"
CONFIG_FILE="$CONFIG_DIR/backup-config.conf"
LOG_DIR="/var/log"
LOG_FILE="$LOG_DIR/backup.log"
BIN_NAME="backup"
SCRIPT_NAME="backup.py"
CONFIG_TEMPLATE="backup-config.conf"

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
    exit 1
fi

# Install dependencies
info "Installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv sshpass

# Create log directory if it doesn't exist
info "Setting up log directory..."
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    chmod 755 "$LOG_DIR"
    info "Log directory created at $LOG_DIR."
else
    info "Log directory already exists."
fi

# Create configuration directory if it doesn't exist
info "Setting up configuration directory..."
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    chmod 755 "$CONFIG_DIR"
    info "Configuration directory created at $CONFIG_DIR."
else
    info "Configuration directory already exists."
fi

# Move the configuration file
info "Moving the configuration file to $CONFIG_FILE..."
if [ ! -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_TEMPLATE" "$CONFIG_FILE"
    chmod 644 "$CONFIG_FILE"
    info "Configuration file copied to $CONFIG_FILE."
else
    info "Configuration file already exists at $CONFIG_FILE."
fi

# Move the backup script
info "Moving the backup script to $INSTALL_DIR/$BIN_NAME..."
cp "$SCRIPT_NAME" "$INSTALL_DIR/$BIN_NAME"
chmod +x "$INSTALL_DIR/$BIN_NAME"
info "Backup script installed at $INSTALL_DIR/$BIN_NAME."

# Create symbolic link to /usr/local/bin
info "Creating symbolic link for easy access..."
ln -sf "$INSTALL_DIR/$BIN_NAME" /usr/local/bin/$BIN_NAME

# Set up the log file
info "Setting up log file..."
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    chmod 664 "$LOG_FILE"
    chown root:adm "$LOG_FILE"
    info "Log file created at $LOG_FILE."
    chmod 777 $LOG_FILE
else
    info "Log file already exists."
fi

# Print completion message
info "Installation complete! You can now run the backup program by typing '${BLUE}backup${RESET}' in your terminal."

# Exit
exit 0
