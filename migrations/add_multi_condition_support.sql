-- 添加多条件组合支持到设备状态监控配置表

-- 添加条件间逻辑运算符字段
ALTER TABLE device_status_monitor_configs 
ADD COLUMN IF NOT EXISTS logic_operator VARCHAR(10) DEFAULT 'AND' COMMENT '条件间逻辑运算符：AND/OR';

-- 添加多条件组合配置字段（JSON格式）
ALTER TABLE device_status_monitor_configs 
ADD COLUMN IF NOT EXISTS conditions JSON COMMENT '多条件组合配置';

COMMENT ON COLUMN device_status_monitor_configs.logic_operator IS '条件间逻辑运算符：AND/OR';
COMMENT ON COLUMN device_status_monitor_configs.conditions IS '多条件组合配置（JSON格式），支持多个Topic/字段的组合匹配';
