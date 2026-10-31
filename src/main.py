"""Module 1 smoke check: connect to PostgreSQL and report server info."""
import logging
import os
import sys

import psycopg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    # TODO 1: read DATABASE_URL from the environment.
    #   If it is missing, log an error and exit with sys.exit(1).
    #   Never log the URL itself: it contains the password.
    url = os.environ.get("DATABASE_URL")
    if not url:
        logger.error("DATABASE_URL environment variable is missing.")
        sys.exit(1)

    # TODO 2: connect and log two things:
    #   - the result of "SELECT version()"
    #   - the result of "SHOW timezone"
    #   hint: with psycopg.connect(url) as conn:
    #             value = conn.execute("...").fetchone()[0]
    try:
        with psycopg.connect(url) as conn:
            version = conn.execute("SELECT version();").fetchone()[0]
            logger.info("PostgreSQL Version: %s", version)

            timezone = conn.execute("SHOW timezone;").fetchone()[0]
            logger.info("Database Timezone: %s", timezone)

    except psycopg.Error as e:
        logger.error("Database connection or query failed: %s", e)
        sys.exit(1)

    logger.info("Database check OK")


if __name__ == "__main__":
    main()