#!/bin/sh
set -e

if [[ -z $COMMAND ]];
then
   COMMAND=${1:-dump-cron}
fi

CRON_SCHEDULE=${CRON_SCHEDULE:-0 1 * * *}
PREFIX=${PREFIX:-dump}
PGUSER=${PGUSER:-postgres}
PGPORT=${PGPORT:-5432}
POSTGRES_DB=${POSTGRES_DB:-postgres}
PGDUMP=${PGDUMP:-'/dump'}
PGHOST=${PGHOST:-db}

##################################
# Environment variables settings #
##################################

echo "COMMAND: ${COMMAND}"
echo "CRON_SCHEDULE: ${CRON_SCHEDULE}"
echo "PREFIX: ${PREFIX}"
echo "PGUSER: ${PGUSER}"
echo "POSTGRES_DB: ${POSTGRES_DB}"
echo "PGHOST: ${PGHOST}"
echo "PGPORT: ${PGPORT}"
echo "PGDUMP: ${PGDUMP}"

if [[ -n ${POSTGRES_PASSWORD_FILE} ]];
then
  echo "POSTGRES_PASSWORD_FILE: ${POSTGRES_PASSWORD_FILE}"
fi

if [[ -f ${POSTGRES_PASSWORD_FILE} ]];
then
   POSTGRES_PASSWORD=$(cat "${POSTGRES_PASSWORD_FILE}")
else
   echo "WARN: No password file found!"
   echo "It is suggested that a docker secrets file is used for security concerns."

   if [[ -n ${PGPASSWORD} ]];
   then
      POSTGRES_PASSWORD=${PGPASSWORD}
   elif [[ -z ${POSTGRES_PASSWORD} ]];
   then
      echo "ERROR: No POSTGRES_PASSWORD set!"
      exit 1
   fi
fi

# Save postgres password to file
echo "${PGHOST}:${PGPORT}:${POSTGRES_DB}:${PGUSER}:${POSTGRES_PASSWORD}" > /root/.pgpass
chmod 600 /root/.pgpass

#################
# Database dump #
#################

CRON_ENV="'${PREFIX}' '${PGUSER}' '${POSTGRES_DB}' '${PGHOST}' '${PGPORT}' '${PGDUMP}'"

if [[ ! -z "${RETAIN_COUNT}" ]]; then
  CRON_ENV="$CRON_ENV '${RETAIN_COUNT}'"
fi

echo "$CRON_SCHEDULE /app/dump.sh $CRON_ENV" >> /var/spool/cron/crontabs/root

crond -l 2 -f
