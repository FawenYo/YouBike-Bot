#!/bin/sh

set -e

PREFIX=${1:-dump}
PGUSER=${2:-postgres}
POSTGRES_DB=${3:-postgres}
PGHOST=${4:-localhost}
PGPORT=${5:-5432}
PGDUMP=${6:-'/dump'}
RETAIN_COUNT=${7:-0}

TABLE=$(date -d "1 day ago" +"%Y-%m-%d")

FILE="$PGDUMP/$PREFIX-$POSTGRES_DB-$TABLE.sql"

echo "Job started: $(date). Dumping to ${FILE}"

pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -f "$FILE" -d "$POSTGRES_DB" -t "$TABLE"
gzip "$FILE"

echo "Table $TABLE dumped to ${FILE}.gz. Deleting table $TABLE"
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$POSTGRES_DB" -c "DROP TABLE \"$TABLE\";"
echo "Table $TABLE deleted"

echo "Retaining ${RETAIN_COUNT} files"

if [[ ${RETAIN_COUNT} -gt 0 ]]; then
    file_count=1
    for file_name in $(ls -t $PGDUMP/*.gz); do
        if [[ ${file_count} > ${RETAIN_COUNT} ]]; then
            echo "Removing older dump file: ${file_name}"
            rm "${file_name}"
        fi
        file_count=$((file_count + 1))
    done
else
    echo "No RETAIN_COUNT! take care with disk space."
fi

echo "Job finished: $(date)"