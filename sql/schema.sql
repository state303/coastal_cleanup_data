CREATE TABLE IF NOT EXISTS country
(
    id   SERIAL
        PRIMARY KEY,
    name VARCHAR(512)
        CONSTRAINT uq__country__name
            UNIQUE
);

CREATE TABLE IF NOT EXISTS state
(
    id   SERIAL
        PRIMARY KEY,
    name VARCHAR(512)
        CONSTRAINT uq__state__name
            UNIQUE
);

CREATE TABLE IF NOT EXISTS zone
(
    id   SERIAL
        PRIMARY KEY,
    name VARCHAR(512)
        CONSTRAINT uq__zone__name
            UNIQUE
);

CREATE TABLE IF NOT EXISTS cleanup_group
(
    id   SERIAL
        PRIMARY KEY,
    name VARCHAR(512)
        CONSTRAINT uq__cleanup_group__name
            UNIQUE
);

CREATE TABLE IF NOT EXISTS litter
(
    id   SERIAL
        PRIMARY KEY,
    name VARCHAR(256)
        CONSTRAINT uq__litter__name
            UNIQUE
);

CREATE TABLE IF NOT EXISTS cleanup_type
(
    id   SERIAL
        PRIMARY KEY,
    name VARCHAR(128)
        CONSTRAINT uq__cleanup_type__name
            UNIQUE
);

CREATE TABLE IF NOT EXISTS environment
(
    id   SERIAL
        PRIMARY KEY,
    name VARCHAR(128)
        CONSTRAINT uq__environment__name
            UNIQUE
);

CREATE TABLE IF NOT EXISTS cleanup
(
    id               SERIAL
        PRIMARY KEY,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    cleaned_at       DATE             NOT NULL,
    adult            INTEGER          DEFAULT 0,
    child            INTEGER          DEFAULT 0,
    kilograms        DOUBLE PRECISION,
    distance         DOUBLE PRECISION,
    area             DOUBLE PRECISION DEFAULT 0,
    zone_id          INTEGER
        CONSTRAINT fk__cleanup__zone_id
            REFERENCES zone,
    country_id       INTEGER
        CONSTRAINT fk__cleanup__country_id
            REFERENCES country,
    state_id         INTEGER
        CONSTRAINT fk__cleanup__state_id
            REFERENCES state,
    cleanup_group_id INTEGER
        CONSTRAINT fk__cleanup__cleanup_group_id
            REFERENCES cleanup_group,
    environment_id   INTEGER
        CONSTRAINT fk__cleanup__environment_id
            REFERENCES environment,
    cleanup_type_id  INTEGER
        CONSTRAINT fk__cleanup__type_id
            REFERENCES cleanup_type
);

CREATE TABLE IF NOT EXISTS cleanup_litter
(
    litter_id  INTEGER
        CONSTRAINT fk__cleanup_litter__litter_id
            REFERENCES litter,
    cleanup_id INTEGER
        CONSTRAINT fk__cleanup_litter__cleanup_id
            REFERENCES cleanup,
    count      INTEGER,
    CONSTRAINT pk__cleanup_litter__litter_id_cleanup_id
        UNIQUE (litter_id, cleanup_id)
);