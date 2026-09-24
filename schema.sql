CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    result_count INTEGER NOT NULL DEFAULT 0,
    searched_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE monitor_keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY,
    notify_new_items BOOLEAN NOT NULL DEFAULT TRUE,
    notify_price_drops BOOLEAN NOT NULL DEFAULT TRUE,
    notify_no_change BOOLEAN NOT NULL DEFAULT FALSE,
    min_price_drop_amount INTEGER NOT NULL DEFAULT 0,
    min_price_drop_percent NUMERIC(5, 1) NOT NULL DEFAULT 0
);

INSERT INTO notification_settings (
    id,
    notify_new_items,
    notify_price_drops,
    notify_no_change,
    min_price_drop_amount,
    min_price_drop_percent
) VALUES (
    1,
    TRUE,
    TRUE,
    TRUE,
    0,
    0.0
);

CREATE TABLE product_history (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    item_code VARCHAR(255) NOT NULL,
    product_name TEXT NOT NULL,
    price INTEGER NOT NULL,
    product_url TEXT,
    checked_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
