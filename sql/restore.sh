#!/bin/bash
# restore_ukmap.sh

BACKUP_FILE="$1"
DB_NAME="ukmap"
USER="postgres"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore_ukmap.sh <backup_file.sql.gz>"
    exit 1
fi

echo "Dropping and recreating database '$DB_NAME'..."
dropdb -U "$USER" "$DB_NAME"
createdb -U "$USER" "$DB_NAME"
psql -U "$USER" -d "$DB_NAME" -c "CREATE EXTENSION postgis;"

echo "Restoring from $BACKUP_FILE..."
gunzip -c "$BACKUP_FILE" | psql -U "$USER" -d "$DB_NAME"

echo "Restore complete."

