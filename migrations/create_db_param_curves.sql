-- DB参数曲线表
CREATE TABLE IF NOT EXISTS db_param_curves (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id),
    curve_name VARCHAR(200) NOT NULL,
    part_number VARCHAR(100),
    servo_axis VARCHAR(100) NOT NULL,
    curve_data JSON NOT NULL,
    total_duration_ms INTEGER,
    max_value FLOAT,
    min_value FLOAT,
    data_points_count INTEGER,
    value_tolerance FLOAT NOT NULL DEFAULT 5.0,
    time_tolerance_ms INTEGER NOT NULL DEFAULT 100,
    enabled INTEGER NOT NULL DEFAULT 1,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_db_param_curves_device_id ON db_param_curves(device_id);
CREATE INDEX idx_db_param_curves_part_number ON db_param_curves(part_number);
CREATE INDEX idx_db_param_curves_enabled ON db_param_curves(enabled);
