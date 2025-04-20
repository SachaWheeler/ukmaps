-- Example: towns table
CREATE TABLE towns (
    id SERIAL PRIMARY KEY,
    name TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    geom GEOGRAPHY(Point, 4326)
);

CREATE TABLE pubs (
    id SERIAL PRIMARY KEY,
    name TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    geom GEOGRAPHY(Point, 4326)
);

CREATE TABLE train_stations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    geom GEOGRAPHY(Point, 4326)
);

CREATE TABLE rivers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOGRAPHY(LINESTRING, 4326)
);

