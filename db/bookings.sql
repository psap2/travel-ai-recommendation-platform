-- Bookings are state: a quote becomes a confirmed reservation.
CREATE TABLE bookings (
    id              TEXT PRIMARY KEY,           -- the idempotency key
    user_id         TEXT        NOT NULL,
    listing_id      TEXT        NOT NULL REFERENCES listings(id),
    nights          INT         NOT NULL CHECK (nights > 0),
    total_price     NUMERIC(10,2) NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'confirmed',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_bookings_user ON bookings (user_id, created_at DESC);
