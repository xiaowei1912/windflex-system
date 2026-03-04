#!/bin/bash
# Initialize PostgreSQL database for Windflex
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Test results table
    CREATE TABLE IF NOT EXISTS test_results (
        id          SERIAL PRIMARY KEY,
        suite_name  VARCHAR(255) NOT NULL,
        test_name   VARCHAR(255) NOT NULL,
        status      VARCHAR(20)  NOT NULL,  -- PASS / FAIL / SKIP
        message     TEXT,
        duration_s  FLOAT,
        created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
        jenkins_build_url TEXT
    );

    -- Test tags table
    CREATE TABLE IF NOT EXISTS test_tags (
        id          SERIAL PRIMARY KEY,
        result_id   INT NOT NULL REFERENCES test_results(id) ON DELETE CASCADE,
        tag         VARCHAR(100) NOT NULL
    );

    -- Jenkins builds summary
    CREATE TABLE IF NOT EXISTS build_summary (
        id          SERIAL PRIMARY KEY,
        build_number INT,
        total       INT DEFAULT 0,
        passed      INT DEFAULT 0,
        failed      INT DEFAULT 0,
        skipped     INT DEFAULT 0,
        created_at  TIMESTAMP NOT NULL DEFAULT NOW()
    );

    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $POSTGRES_USER;
EOSQL

echo "Database initialized successfully."
