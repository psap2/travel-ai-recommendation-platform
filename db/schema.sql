-- The catalog: one row per bookable stay.
CREATE TABLE listings (
    id              TEXT PRIMARY KEY,
    city            TEXT        NOT NULL,
    name            TEXT        NOT NULL,
    kind            TEXT        NOT NULL,         -- 'hotel' | 'villa' | 'hostel' | ...
    price_per_night NUMERIC(8,2) NOT NULL,
    rating          REAL        NOT NULL,
    reviews         INT         NOT NULL DEFAULT 0,
    lat             REAL        NOT NULL,
    lon             REAL        NOT NULL,
    tags            TEXT[]      NOT NULL DEFAULT '{}',
    description     TEXT        NOT NULL DEFAULT '',
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Searches filter by city + price, so index that pair.
CREATE INDEX idx_listings_city_price ON listings (city, price_per_night);
-- GIN index makes tag-overlap (&&) lookups fast.
CREATE INDEX idx_listings_tags ON listings USING GIN (tags);
-- Full-text search vector over name + description, kept current by the query.
CREATE INDEX idx_listings_fts ON listings
    USING GIN (to_tsvector('english', name || ' ' || description));

-- Every view/click/booking — the personalization + quality signal.
CREATE TABLE interactions (
    user_id    TEXT NOT NULL,
    listing_id TEXT NOT NULL REFERENCES listings(id),
    action     TEXT NOT NULL,                    -- 'view' | 'click' | 'book'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_interactions_user ON interactions (user_id, created_at DESC);
CREATE INDEX idx_interactions_time ON interactions (created_at DESC);
