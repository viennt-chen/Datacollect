-- 新增 show_on_dashboard 字段，控制设备是否在看板显示
ALTER TABLE devices ADD COLUMN show_on_dashboard BOOLEAN DEFAULT FALSE COMMENT '是否在看板显示';
