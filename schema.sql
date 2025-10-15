CREATE TABLE title (
    id          INTEGER NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    synopsis    TEXT NOT NULL,
    thumbnail   TEXT NOT NULL,
    banner      TEXT NOT NULL
    -- PRIMARY KEY (id)     -- split indexing
);

CREATE TABLE subtitle (
    title_id    INTEGER NOT NULL,
    id          INTEGER NOT NULL,
    name        TEXT NOT NULL,
    date        INTEGER NOT NULL,
    thumbnail   TEXT NOT NULL,
    comment     TEXT NOT NULL,
    FOREIGN KEY (title_id) REFERENCES title (id) ON DELETE CASCADE,
    PRIMARY KEY (title_id, id)
);

CREATE TABLE subtitle_image (
    title_id    INTEGER NOT NULL,
    subtitle_id INTEGER NOT NULL,
    id          INTEGER NOT NULL,
    image       TEXT NOT NULL,
    FOREIGN KEY (title_id, subtitle_id) REFERENCES subtitle (title_id, id) ON DELETE CASCADE,
    PRIMARY KEY (title_id, subtitle_id, id)
);

CREATE TABLE artist (
    id          INTEGER NOT NULL,
    name        TEXT NOT NULL,
    profile     TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE title_artist (
    title_id    INTEGER NOT NULL,
    artist_id   INTEGER NOT NULL,
    role        TEXT NOT NULL,
    FOREIGN KEY (title_id) REFERENCES title (id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES artist (id) ON DELETE CASCADE,
    PRIMARY KEY (title_id, artist_id)
);