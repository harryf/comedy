#!/bin/zsh
#
# backup_comedybot.zsh
# 
# Creates a backup of the ~/.comedybot directory as a tar.gz file
# and places it in the ~/Code/comedy/archive/backup directory
# with a timestamp in the filename.

# Ensure the backup directory exists
BACKUP_DIR=~/Code/comedy/archive/backup
mkdir -p "$BACKUP_DIR"

# Source directory to backup
SOURCE_DIR=~/.comedybot

# Create timestamp in YYYYMMDDHHMMSS format
TIMESTAMP=$(date +"%Y%m%d%H%M%S")

# Create the backup filename
BACKUP_FILE="comedybot_${TIMESTAMP}.tar.gz"

# Full path to the backup file
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Create the backup
echo "Creating backup of $SOURCE_DIR..."
tar -czf "$BACKUP_PATH" -C $(dirname "$SOURCE_DIR") $(basename "$SOURCE_DIR")

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup created successfully: $BACKUP_PATH"
    echo "Backup size: $(du -h "$BACKUP_PATH" | cut -f1)"
else
    echo "Error: Backup creation failed!"
    exit 1
fi
