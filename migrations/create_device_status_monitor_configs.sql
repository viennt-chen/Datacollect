-- 设备状态监控配置表
CREATE TABLE IF NOT EXISTS device_status_monitor_configs (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id),
    status_type VARCHAR(50) NOT NULL,
    topic_name VARCHAR(255) NOT NULL,
    field_path VARCHAR(255) NOT NULL,
    match_rule VARCHAR(50) NOT NULL,
    match_value TEXT,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_device_status_monitor_configs_device_id ON device_status_monitor_configs(device_id);
CREATE INDEX idx_device_status_monitor_configs_status_type ON device_status_monitor_configs(status_type);
CREATE INDEX idx_device_status_monitor_configs_enabled ON device_status_monitor_configs(enabled);

COMMENT ON TABLE device_status_monitor_configs IS '设备状态监控配置表';
COMMENT ON COLUMN device_status_monitor_configs.device_id IS '设备ID';
COMMENT ON COLUMN device_status_monitor_configs.status_type IS '状态类型：processing/mold_change/fault/alarm/material_shortage/stop';
COMMENT ON COLUMN device_status_monitor_configs.topic_name IS 'MQTT Topic名称';
COMMENT ON COLUMN device_status_monitor_configs.field_path IS '字段路径';
COMMENT ON COLUMN device_status_monitor_configs.match_rule IS '匹配规则类型';
COMMENT ON COLUMN device_status_monitor_configs.match_value IS '匹配值（JSON格式）';
COMMENT ON COLUMN device_status_monitor_configs.enabled IS '是否启用';
COMMENT ON COLUMN device_status_monitor_configs.priority IS '优先级';
COMMENT ON COLUMN device_status_monitor_configs.description IS '备注说明';
