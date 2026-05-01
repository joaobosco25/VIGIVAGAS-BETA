#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
pg_dump "$DATABASE_URL" -F p -f "backups/vigivagas_backup_$(date +%Y%m%d_%H%M%S).sql"
echo "Backup finalizado."
