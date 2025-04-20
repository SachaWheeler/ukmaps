#!/bin/bash
# dump_ukmap.sh

DB_NAME="ukmap"
BACKUP_FILE="dumps/ukmap_$(date +%Y%m%d_%H%M%S).sql.gz"
USER="postgres"

echo "Dumping database '$DB_NAME' to $BACKUP_FILE..."
pg_dump -U "$USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "Done."

