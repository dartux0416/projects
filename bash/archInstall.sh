#!/bin/bash

# Ensure the script is run as root
if [ "$(id -u)" -ne 0 ]; then
   echo "This script must be run as root"
   exit 1
fi

# Ask for the disk to use
read -p "Enter the disk to install on (form: /dev/sda): " DISK
echo "Selected $DISK for installation."

# Set the system clock
timedatectl set-ntp true

# Partitioning the disk
# Warning: This will erase data on the selected disk!
echo "Partitioning the disk..."
(
  echo o      # Create a new partition table
  echo n      # New partition (primary)
  echo p      # Primary partition
  echo 1      # Partition number
  echo        # First sector (accepts default)
  echo +512M  # Size of the EFI partition
  echo t      # Change partition type
  echo 1      # Type EFI
  echo n      # New partition
  echo p      # Primary partition
  echo 2      # Partition number
  echo        # First sector (accepts default)
  echo        # Last sector (accepts default, rest of the disk)
  echo w      # Write changes and exit
) | fdisk $DISK

# Formatting the partitions
echo "Formatting partitions..."
mkfs.fat -F32 ${DISK}1  # Format the EFI partition
mkfs.ext4 ${DISK}2      # Format the root partition

# Mounting the partitions
echo "Mounting partitions..."
mount ${DISK}2 /mnt          # Mount the root partition
mkdir /mnt/efi
mount ${DISK}1 /mnt/efi      # Mount the EFI partition

# Installing the base system
echo "Installing the base system..."
pacstrap /mnt base linux linux-firmware vim intel-ucode amd-ucode

# Generating fstab
genfstab -U /mnt >> /mnt/etc/fstab

# Setting root password
echo "Setting up root password."
arch-chroot /mnt /bin/bash -c "echo 'Please enter new root password: '; passwd root"

# User setup
read -p "Enter new username to create: " USERNAME
arch-chroot /mnt /bin/bash <<EOF
useradd -m -G wheel -s /bin/bash $USERNAME
echo "Please enter password for new user $USERNAME: "
passwd $USERNAME
echo "$USERNAME ALL=(ALL) ALL" >> /etc/sudoers
EOF

# Chroot and system configuration
arch-chroot /mnt /bin/bash <<EOF
echo "archlinux" > /etc/hostname
ln -sf /usr/share/zoneinfo/Region/City /etc/localtime
hwclock --systohc
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf
echo "KEYMAP=pl" > /etc/vconsole.conf
mkinitcpio -P
systemctl enable dhcpcd
EOF

# Bootloader installation
arch-chroot /mnt /bin/bash <<EOF
pacman -S --noconfirm grub efibootmgr
grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
EOF

echo "Installation complete. Rebooting..."
reboot

