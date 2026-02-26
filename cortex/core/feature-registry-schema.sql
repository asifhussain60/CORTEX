
CREATE TABLE IF NOT EXISTS features (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    enabled BOOLEAN NOT NULL DEFAULT false,
    category VARCHAR(100),
    version VARCHAR(50),
    rollout_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    constraints TEXT
);

CREATE TABLE IF NOT EXISTS feature_audit (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    feature_id VARCHAR(255) NOT NULL,
    action VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);

CREATE TABLE IF NOT EXISTS feature_rollout (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    feature_id VARCHAR(255) NOT NULL,
    user_segment VARCHAR(100),
    rollout_percentage INTEGER,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);
