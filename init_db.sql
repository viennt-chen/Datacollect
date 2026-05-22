-- ============================================================
-- WebAdmin 数据库初始化脚本
-- 数据库: MySQL (datacollect)
-- ============================================================

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================
-- 1. 设备表 (devices) - 无外键依赖，优先创建
-- ============================================================
CREATE TABLE IF NOT EXISTS `devices` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `device_code` VARCHAR(100) NOT NULL,
    `device_name` VARCHAR(255) NOT NULL,
    `device_type` VARCHAR(100) NULL,
    `model` VARCHAR(255) NULL,
    `manufacturer` VARCHAR(255) NULL,
    `line_code` VARCHAR(100) NULL,
    `factory_code` VARCHAR(100) NULL,
    `group_code` VARCHAR(100) NULL,
    `description` TEXT NULL,
    `location` VARCHAR(255) NULL,
    `status` VARCHAR(20) NULL DEFAULT 'active',
    `is_enabled` BOOL NULL DEFAULT 1,
    `ip_address` VARCHAR(50) NULL,
    `mqtt_topics` TEXT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` VARCHAR(100) NULL,
    `updated_by` VARCHAR(100) NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_devices_device_code` (`device_code`),
    INDEX `ix_devices_device_code` (`device_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 2. 用户表 (users)
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `salt` VARCHAR(100) NOT NULL,
    `full_name` VARCHAR(100) NULL,
    `is_active` BOOL NULL DEFAULT 1,
    `is_superuser` BOOL NULL DEFAULT 0,
    `role` VARCHAR(50) NULL DEFAULT 'user',
    `last_login` DATETIME NULL,
    `failed_login_attempts` INTEGER NULL DEFAULT 0,
    `locked_until` DATETIME NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_users_username` (`username`),
    UNIQUE KEY `uq_users_email` (`email`),
    INDEX `ix_users_id` (`id`),
    INDEX `ix_users_username` (`username`),
    INDEX `ix_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 3. 登录日志表 (login_logs)
-- ============================================================
CREATE TABLE IF NOT EXISTS `login_logs` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `user_id` INTEGER NULL,
    `username_attempted` VARCHAR(100) NULL,
    `ip_address` VARCHAR(50) NULL,
    `user_agent` VARCHAR(500) NULL,
    `success` BOOL NULL,
    `failure_reason` VARCHAR(200) NULL,
    `timestamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `ix_login_logs_id` (`id`),
    INDEX `ix_login_logs_user_id` (`user_id`),
    INDEX `ix_login_logs_username_attempted` (`username_attempted`),
    INDEX `ix_login_logs_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 4. 刷新令牌表 (refresh_tokens)
-- ============================================================
CREATE TABLE IF NOT EXISTS `refresh_tokens` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `user_id` INTEGER NOT NULL,
    `token` VARCHAR(500) NOT NULL,
    `expires_at` DATETIME NOT NULL,
    `is_revoked` BOOL NULL DEFAULT 0,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `ip_address` VARCHAR(50) NULL,
    `user_agent` VARCHAR(500) NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_refresh_tokens_token` (`token`),
    INDEX `ix_refresh_tokens_id` (`id`),
    INDEX `ix_refresh_tokens_user_id` (`user_id`),
    INDEX `ix_refresh_tokens_token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 5. 物料表 (products)
-- ============================================================
CREATE TABLE IF NOT EXISTS `products` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `u9_material_code` VARCHAR(100) NOT NULL,
    `part_number` VARCHAR(100) NULL,
    `product_name` VARCHAR(255) NOT NULL,
    `description` TEXT NULL,
    `specification` VARCHAR(255) NULL,
    `category` VARCHAR(100) NULL,
    `project` VARCHAR(255) NULL,
    `unit` VARCHAR(50) NULL,
    `unit_work_time` NUMERIC(10,5) NULL,
    `material_type` VARCHAR(20) NOT NULL DEFAULT 'product' COMMENT '物料类型: product(产品)/semi_finished(半成品)/material(原材料)/auxiliary(辅料)',
    `status` VARCHAR(20) NULL DEFAULT 'active',
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` VARCHAR(100) NULL,
    `updated_by` VARCHAR(100) NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_products_u9_material_code` (`u9_material_code`),
    INDEX `ix_products_u9_material_code` (`u9_material_code`),
    INDEX `ix_products_part_number` (`part_number`),
    INDEX `ix_products_material_type` (`material_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 6. 产品订单表 (product_orders)
-- ============================================================
CREATE TABLE IF NOT EXISTS `product_orders` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `doc_no` VARCHAR(100) NOT NULL,
    `part_number` VARCHAR(100) NOT NULL,
    `u9_material_code` VARCHAR(100) NOT NULL,
    `specs` VARCHAR(255) NULL,
    `item_code` VARCHAR(100) NULL,
    `item_name` TEXT NULL,
    `planned_output` INTEGER NULL DEFAULT 0,
    `query_date` VARCHAR(20) NOT NULL,
    `product_qty` FLOAT NULL DEFAULT 0,
    `total_complete_qty` FLOAT NULL DEFAULT 0,
    `total_eligible_qty` FLOAT NULL DEFAULT 0,
    `total_scrap_qty` FLOAT NULL DEFAULT 0,
    `complete_wh` VARCHAR(255) NULL,
    `complete_wh_code` VARCHAR(50) NULL,
    `line_number` VARCHAR(100) NULL,
    `line_code` VARCHAR(50) NULL,
    `line_description` TEXT NULL,
    `department_code` VARCHAR(50) NULL,
    `department_name` VARCHAR(255) NULL,
    `doc_type_code` VARCHAR(50) NULL,
    `doc_type` VARCHAR(100) NULL,
    `doc_state` VARCHAR(50) NULL,
    `project` VARCHAR(255) NULL,
    `mold_no` VARCHAR(100) NULL,
    `cavity_number` VARCHAR(100) NULL,
    `short_code` VARCHAR(50) NULL,
    `packet_qty` FLOAT NULL DEFAULT 0,
    `cycle_time` VARCHAR(50) NULL,
    `machine` VARCHAR(100) NULL,
    `over_rate` FLOAT NULL DEFAULT 0,
    `start_date` DATETIME NULL,
    `description` TEXT NULL,
    `query_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_product_orders_doc_no` (`doc_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 7. 产品订单查询日志表 (product_order_query_logs)
-- ============================================================
CREATE TABLE IF NOT EXISTS `product_order_query_logs` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `part_number` VARCHAR(100) NULL,
    `specs` VARCHAR(200) NULL,
    `planned_output` INTEGER NULL DEFAULT 0,
    `order_count` INTEGER NULL DEFAULT 0,
    `saved_count` INTEGER NULL DEFAULT 0,
    `status` VARCHAR(50) NULL DEFAULT 'success',
    `error_message` TEXT NULL,
    `query_date` VARCHAR(20) NULL,
    `execution_type` VARCHAR(50) NULL DEFAULT 'manual',
    `duration_seconds` FLOAT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `ix_product_order_query_logs_id` (`id`),
    INDEX `ix_product_order_query_logs_part_number` (`part_number`),
    INDEX `ix_product_order_query_logs_query_date` (`query_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 8. 工艺参数表 (process_parameters)
-- ============================================================
CREATE TABLE IF NOT EXISTS `process_parameters` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `process_type` VARCHAR(50) NULL,
    `machine_id` VARCHAR(50) NULL,
    `product_model` VARCHAR(100) NULL,
    `param_name` VARCHAR(100) NOT NULL,
    `param_value` FLOAT NOT NULL,
    `unit` VARCHAR(20) NULL,
    `start_code` VARCHAR(50) NULL,
    `process_no` VARCHAR(50) NULL,
    `batch_no` VARCHAR(50) NULL,
    `operator` VARCHAR(50) NULL,
    `remark` TEXT NULL,
    PRIMARY KEY (`id`),
    INDEX `ix_process_parameters_id` (`id`),
    INDEX `ix_process_parameters_create_time` (`create_time`),
    INDEX `ix_process_parameters_process_type` (`process_type`),
    INDEX `ix_process_parameters_machine_id` (`machine_id`),
    INDEX `ix_process_parameters_product_model` (`product_model`),
    INDEX `ix_process_parameters_param_name` (`param_name`),
    INDEX `ix_process_parameters_start_code` (`start_code`),
    INDEX `ix_process_parameters_process_no` (`process_no`),
    INDEX `idx_time_machine` (`create_time`, `machine_id`),
    INDEX `idx_process_param` (`process_type`, `param_name`),
    INDEX `idx_start_code` (`start_code`, `process_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 9. 加工事件表 (processing_events)
-- ============================================================
CREATE TABLE IF NOT EXISTS `processing_events` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `event_uid` VARCHAR(255) NOT NULL,
    `start_code` VARCHAR(100) NOT NULL,
    `skin_code` VARCHAR(500) NULL,
    `start_time` DATETIME(3) NULL,
    `end_time` DATETIME(3) NULL,
    `start_signal` DATETIME(3) NULL,
    `end_signal` DATETIME(3) NULL,
    `duringtime` INTEGER NULL,
    `machine_duringtime` INTEGER NULL,
    `machine_id` VARCHAR(100) NULL,
    `operator_id` VARCHAR(50) NULL,
    `operator_name` VARCHAR(100) NULL,
    `group_code` VARCHAR(50) NULL,
    `group_name` VARCHAR(100) NULL,
    `group_short_name` VARCHAR(50) NULL,
    `factory_code` VARCHAR(50) NULL,
    `factory_name` VARCHAR(100) NULL,
    `line_code` VARCHAR(50) NULL,
    `process_no` VARCHAR(50) NULL,
    `extra_data` TEXT NULL,
    `created_at` DATETIME(3) NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updated_at` DATETIME(3) NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_processing_events_event_uid` (`event_uid`),
    INDEX `ix_processing_events_start_time` (`start_time`),
    INDEX `ix_processing_events_start_code` (`start_code`),
    INDEX `ix_processing_events_machine_id` (`machine_id`),
    INDEX `ix_processing_events_operator_id` (`operator_id`),
    INDEX `ix_processing_events_group_code` (`group_code`),
    INDEX `ix_processing_events_factory_code` (`factory_code`),
    INDEX `ix_processing_events_process_no` (`process_no`),
    INDEX `idx_group_factory` (`group_code`, `factory_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 10. 加工事件数据表 (event_data)
-- ============================================================
CREATE TABLE IF NOT EXISTS `event_data` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `event_uid` VARCHAR(100) NULL,
    `start_code` VARCHAR(200) NULL,
    `skin_code` VARCHAR(500) NULL,
    `start_time` BIGINT NULL,
    `end_time` BIGINT NULL,
    `start_signal` BIGINT NULL,
    `end_signal` BIGINT NULL,
    `duringtime` INTEGER NULL,
    `machine_duringtime` INTEGER NULL,
    `machine_id` VARCHAR(100) NULL,
    `operator_id` VARCHAR(100) NULL,
    `operator_name` VARCHAR(200) NULL,
    `group_code` VARCHAR(50) NULL,
    `group_name` VARCHAR(200) NULL,
    `group_short_name` VARCHAR(100) NULL,
    `factory_code` VARCHAR(50) NULL,
    `factory_name` VARCHAR(200) NULL,
    `line_code` VARCHAR(50) NULL,
    `process_no` VARCHAR(50) NULL,
    `extra_data` TEXT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_event_data_event_uid` (`event_uid`),
    INDEX `idx_event_uid` (`event_uid`),
    INDEX `idx_machine_id` (`machine_id`),
    INDEX `idx_operator_id` (`operator_id`),
    INDEX `idx_start_time` (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 11. 采集数据表 (collected_data)
-- ============================================================
CREATE TABLE IF NOT EXISTS `collected_data` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `topic_name` VARCHAR(200) NOT NULL,
    `message_id` VARCHAR(100) NULL,
    `event_time` DATETIME NULL,
    `collect_time` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `data_string` VARCHAR(500) NULL,
    `data_float` FLOAT NULL,
    `data_int` INTEGER NULL,
    `data_boolean` BOOL NULL,
    `data_json` TEXT NULL,
    `quality` VARCHAR(20) NULL DEFAULT 'GOOD',
    `source_ip` VARCHAR(50) NULL,
    PRIMARY KEY (`id`),
    INDEX `ix_collected_data_id` (`id`),
    INDEX `ix_collected_data_topic_name` (`topic_name`),
    INDEX `ix_collected_data_message_id` (`message_id`),
    INDEX `idx_topic_time` (`topic_name`, `event_time`),
    INDEX `idx_collect_time` (`collect_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 12. 采集日志表 (collector_logs)
-- ============================================================
CREATE TABLE IF NOT EXISTS `collector_logs` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `log_level` VARCHAR(20) NOT NULL,
    `log_type` VARCHAR(50) NOT NULL,
    `topic_name` VARCHAR(200) NULL,
    `message_id` VARCHAR(100) NULL,
    `db_operation` VARCHAR(50) NULL,
    `table_name` VARCHAR(100) NULL,
    `affected_rows` INTEGER NULL,
    `error_message` TEXT NULL,
    `execution_time_ms` INTEGER NULL,
    `summary` VARCHAR(500) NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `ix_collector_logs_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 13. MQTT Topic 配置表 (mqtt_topic_configs)
-- ============================================================
CREATE TABLE IF NOT EXISTS `mqtt_topic_configs` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `topic_name` VARCHAR(255) NOT NULL,
    `description` TEXT NULL,
    `topic_type` VARCHAR(50) NOT NULL DEFAULT 'custom',
    `enabled` BOOL NOT NULL DEFAULT 1,
    `qos` INTEGER NULL DEFAULT 1,
    `storage_policy` VARCHAR(50) NULL DEFAULT 'save_raw',
    `parse_rules` TEXT NULL,
    `device_id` INTEGER NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_mqtt_topic_configs_topic_name` (`topic_name`),
    INDEX `ix_mqtt_topic_configs_topic_name` (`topic_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 14. 压缩参数表 (compressed_params)
-- ============================================================
CREATE TABLE IF NOT EXISTS `compressed_params` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `topic` VARCHAR(200) NOT NULL,
    `event_uid` VARCHAR(100) NULL,
    `timestamp_ms` BIGINT NOT NULL,
    `original_timestamp` BIGINT NULL,
    `compressed_payload` LONGBLOB NOT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `ix_compressed_params_topic` (`topic`),
    INDEX `ix_compressed_params_event_uid` (`event_uid`),
    INDEX `ix_compressed_params_timestamp_ms` (`timestamp_ms`),
    INDEX `ix_compressed_params_created_at` (`created_at`),
    INDEX `idx_topic_timestamp` (`topic`, `timestamp_ms`),
    INDEX `idx_event_uid` (`event_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 15. 报警压缩参数表 (alarm_compressed_params)
-- ============================================================
CREATE TABLE IF NOT EXISTS `alarm_compressed_params` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `topic` VARCHAR(200) NOT NULL,
    `event_uid` VARCHAR(100) NULL,
    `timestamp` DATETIME(6) NOT NULL,
    `original_timestamp` DATETIME(6) NULL,
    `compressed_payload` LONGBLOB NOT NULL,
    `created_at` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    INDEX `ix_alarm_compressed_params_topic` (`topic`),
    INDEX `ix_alarm_compressed_params_event_uid` (`event_uid`),
    INDEX `ix_alarm_compressed_params_timestamp` (`timestamp`),
    INDEX `ix_alarm_compressed_params_created_at` (`created_at`),
    INDEX `idx_alarm_topic_timestamp` (`topic`, `timestamp`),
    INDEX `idx_alarm_event_uid` (`event_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 16. PV 压缩参数表 (pv_compressed_params)
-- ============================================================
CREATE TABLE IF NOT EXISTS `pv_compressed_params` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `topic` VARCHAR(200) NOT NULL,
    `event_uid` VARCHAR(100) NULL,
    `timestamp` DATETIME(6) NOT NULL,
    `original_timestamp` DATETIME(6) NULL,
    `compressed_payload` LONGBLOB NOT NULL,
    `created_at` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    INDEX `ix_pv_compressed_params_topic` (`topic`),
    INDEX `ix_pv_compressed_params_event_uid` (`event_uid`),
    INDEX `ix_pv_compressed_params_timestamp` (`timestamp`),
    INDEX `ix_pv_compressed_params_created_at` (`created_at`),
    INDEX `idx_pv_topic_timestamp` (`topic`, `timestamp`),
    INDEX `idx_pv_event_uid` (`event_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 17. SV 压缩参数表 (sv_compressed_params)
-- ============================================================
CREATE TABLE IF NOT EXISTS `sv_compressed_params` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `topic` VARCHAR(200) NOT NULL,
    `event_uid` VARCHAR(100) NULL,
    `timestamp` DATETIME(6) NOT NULL,
    `original_timestamp` DATETIME(6) NULL,
    `compressed_payload` LONGBLOB NOT NULL,
    `created_at` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    INDEX `ix_sv_compressed_params_topic` (`topic`),
    INDEX `ix_sv_compressed_params_event_uid` (`event_uid`),
    INDEX `ix_sv_compressed_params_timestamp` (`timestamp`),
    INDEX `ix_sv_compressed_params_created_at` (`created_at`),
    INDEX `idx_sv_topic_timestamp` (`topic`, `timestamp`),
    INDEX `idx_sv_event_uid` (`event_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 18. 原始数据块表 (raw_data_blocks)
-- ============================================================
CREATE TABLE IF NOT EXISTS `raw_data_blocks` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `topic` VARCHAR(255) NOT NULL,
    `event_uid` VARCHAR(255) NULL,
    `timestamp_ms` BIGINT NOT NULL,
    `original_timestamp` BIGINT NULL,
    `compressed_payload` LONGBLOB NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `ix_raw_data_blocks_topic` (`topic`),
    INDEX `ix_raw_data_blocks_event_uid` (`event_uid`),
    INDEX `ix_raw_data_blocks_timestamp_ms` (`timestamp_ms`),
    INDEX `ix_raw_data_blocks_original_timestamp` (`original_timestamp`),
    INDEX `idx_topic_timestamp` (`topic`, `timestamp_ms`),
    INDEX `idx_event_uid` (`event_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 19. 报警记录表 (alarm_records)
-- ============================================================
CREATE TABLE IF NOT EXISTS `alarm_records` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `alarm_code` VARCHAR(100) NOT NULL,
    `alarm_source` VARCHAR(50) NOT NULL,
    `alarm_level` VARCHAR(20) NOT NULL,
    `alarm_type` VARCHAR(100) NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT NULL,
    `device_code` VARCHAR(100) NULL,
    `device_name` VARCHAR(255) NULL,
    `alarm_value` FLOAT NULL,
    `threshold_value` FLOAT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `handler` VARCHAR(100) NULL,
    `handled_at` DATETIME NULL,
    `handle_remark` TEXT NULL,
    `alarm_time` DATETIME NOT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_alarm_records_alarm_code` (`alarm_code`),
    INDEX `ix_alarm_records_alarm_code` (`alarm_code`),
    INDEX `ix_alarm_records_alarm_level` (`alarm_level`),
    INDEX `ix_alarm_records_device_code` (`device_code`),
    INDEX `ix_alarm_records_status` (`status`),
    INDEX `ix_alarm_records_alarm_time` (`alarm_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 20. DB 参数曲线表 (db_param_curves) - 依赖 devices
-- ============================================================
CREATE TABLE IF NOT EXISTS `db_param_curves` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `device_id` INTEGER NOT NULL,
    `curve_name` VARCHAR(200) NOT NULL,
    `part_number` VARCHAR(100) NULL,
    `servo_axis` VARCHAR(100) NOT NULL,
    `curve_data` JSON NOT NULL,
    `total_duration_ms` INTEGER NULL,
    `max_value` FLOAT NULL,
    `min_value` FLOAT NULL,
    `data_points_count` INTEGER NULL,
    `value_tolerance` FLOAT NULL DEFAULT 5.0,
    `time_tolerance_ms` INTEGER NULL DEFAULT 100,
    `enabled` INTEGER NULL DEFAULT 1,
    `description` TEXT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_db_param_curves_device_id` (`device_id`),
    INDEX `idx_db_param_curves_part_number` (`part_number`),
    INDEX `idx_db_param_curves_enabled` (`enabled`),
    CONSTRAINT `fk_db_param_curves_device_id` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 21. 设备状态监控配置表 (device_status_monitor_configs) - 依赖 devices, db_param_curves
-- ============================================================
CREATE TABLE IF NOT EXISTS `device_status_monitor_configs` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `device_id` INTEGER NOT NULL,
    `status_type` VARCHAR(50) NOT NULL,
    `topic_name` VARCHAR(255) NOT NULL,
    `field_path` VARCHAR(255) NOT NULL,
    `match_rule` VARCHAR(50) NOT NULL,
    `match_value` TEXT NULL,
    `extraction_rule` JSON NULL,
    `curve_id` INTEGER NULL,
    `logic_operator` VARCHAR(10) NULL DEFAULT 'AND',
    `conditions` JSON NULL,
    `enabled` BOOL NOT NULL DEFAULT 1,
    `priority` INTEGER NULL DEFAULT 0,
    `description` TEXT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `ix_device_status_monitor_configs_device_id` (`device_id`),
    INDEX `ix_device_status_monitor_configs_curve_id` (`curve_id`),
    CONSTRAINT `fk_dsmc_device_id` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`),
    CONSTRAINT `fk_dsmc_curve_id` FOREIGN KEY (`curve_id`) REFERENCES `db_param_curves` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 22. 当前产品配置表 (current_product_configs) - 依赖 devices
-- ============================================================
CREATE TABLE IF NOT EXISTS `current_product_configs` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `device_id` INTEGER NOT NULL,
    `topic_name` VARCHAR(255) NOT NULL,
    `field_path` VARCHAR(500) NOT NULL,
    `field_description` VARCHAR(200) NULL,
    `extraction_rule` JSON NULL,
    `enabled` BOOL NOT NULL DEFAULT 1,
    `priority` INTEGER NULL DEFAULT 0,
    `description` TEXT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_cpc_device_id` (`device_id`),
    INDEX `idx_cpc_enabled` (`enabled`),
    CONSTRAINT `fk_cpc_device_id` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 23. 订单加工记录表 (order_processing_records) - 依赖 devices
-- ============================================================
CREATE TABLE IF NOT EXISTS `order_processing_records` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `device_id` INTEGER NOT NULL,
    `device_code` VARCHAR(100) NOT NULL,
    `part_number` VARCHAR(100) NULL,
    `u9_material_code` VARCHAR(100) NULL,
    `doc_no` VARCHAR(100) NULL,
    `planned_qty` INTEGER NULL,
    `completed_qty` INTEGER NULL DEFAULT 0,
    `eligible_qty` INTEGER NULL DEFAULT 0,
    `scrap_qty` INTEGER NULL DEFAULT 0,
    `status` VARCHAR(20) NULL DEFAULT 'in_progress',
    `start_time` DATETIME NULL,
    `end_time` DATETIME NULL,
    `record_date` VARCHAR(10) NOT NULL,
    `notes` TEXT NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_device_date_docno` (`device_id`, `record_date`, `doc_no`),
    INDEX `ix_order_processing_records_device_id` (`device_id`),
    INDEX `ix_order_processing_records_part_number` (`part_number`),
    INDEX `ix_order_processing_records_record_date` (`record_date`),
    INDEX `idx_opr_device_date` (`device_id`, `record_date`),
    INDEX `idx_opr_status` (`status`),
    CONSTRAINT `fk_opr_device_id` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 24. 事件-SV 关联表 (event_sv_relations)
-- ============================================================
CREATE TABLE IF NOT EXISTS `event_sv_relations` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `event_id` BIGINT NOT NULL,
    `machine_id` VARCHAR(100) NOT NULL,
    `sv_topic` VARCHAR(200) NOT NULL,
    `sv_record_id` BIGINT NOT NULL,
    `sv_data_snapshot` JSON NULL,
    `sv_timestamp` DATETIME(6) NULL,
    `time_offset_ms` INTEGER NULL,
    `created_at` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    INDEX `idx_event_sv_event_id` (`event_id`),
    INDEX `idx_event_sv_machine_time` (`machine_id`, `sv_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 25. 事件-PV 关联表 (event_pv_relations)
-- ============================================================
CREATE TABLE IF NOT EXISTS `event_pv_relations` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `event_id` BIGINT NOT NULL,
    `machine_id` VARCHAR(100) NOT NULL,
    `pv_topic` VARCHAR(200) NOT NULL,
    `pv_record_id` BIGINT NOT NULL,
    `pv_data_snapshot` JSON NULL,
    `pv_timestamp` DATETIME(6) NULL,
    `time_offset_ms` INTEGER NULL,
    `sv_point_id` VARCHAR(100) NULL,
    `sv_value_range` JSON NULL,
    `created_at` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    INDEX `idx_event_pv_event_id` (`event_id`),
    INDEX `idx_event_pv_machine_time` (`machine_id`, `pv_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 26. 事件-报警关联表 (event_alarm_relations)
-- ============================================================
CREATE TABLE IF NOT EXISTS `event_alarm_relations` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `event_id` BIGINT NOT NULL,
    `machine_id` VARCHAR(100) NOT NULL,
    `alarm_record_id` BIGINT NOT NULL,
    `alarm_code` VARCHAR(100) NULL,
    `alarm_level` VARCHAR(20) NULL,
    `alarm_type` VARCHAR(100) NULL,
    `alarm_title` VARCHAR(255) NULL,
    `alarm_value` VARCHAR(100) NULL,
    `alarm_time` DATETIME(6) NULL,
    `time_offset_from_start_ms` INTEGER NULL,
    `created_at` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    INDEX `idx_event_alarm_event_id` (`event_id`),
    INDEX `idx_event_alarm_machine_time` (`machine_id`, `alarm_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 27. 事件关联汇总表 (event_data_relation_summary)
-- ============================================================
CREATE TABLE IF NOT EXISTS `event_data_relation_summary` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `event_id` BIGINT NOT NULL,
    `machine_id` VARCHAR(100) NOT NULL,
    `event_start_time` BIGINT NULL,
    `event_end_time` BIGINT NULL,
    `sv_count` INTEGER NULL DEFAULT 0,
    `pv_count` INTEGER NULL DEFAULT 0,
    `alarm_count` INTEGER NULL DEFAULT 0,
    `sv_matched` INTEGER NULL DEFAULT 0,
    `pv_matched` INTEGER NULL DEFAULT 0,
    `alarm_matched` INTEGER NULL DEFAULT 0,
    `last_match_time` DATETIME(6) NULL,
    `created_at` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_event_data_relation_summary_event_id` (`event_id`),
    INDEX `idx_relation_summary_event_id` (`event_id`),
    INDEX `idx_relation_summary_machine_id` (`machine_id`),
    INDEX `idx_relation_summary_match_status` (`sv_matched`, `pv_matched`, `alarm_matched`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 插入默认数据
-- ============================================================

-- 默认管理员账户 (admin / admin123)
-- 密码哈希: sha256("admin123" + salt)
INSERT IGNORE INTO `users` (`username`, `email`, `password_hash`, `salt`, `full_name`, `is_active`, `is_superuser`, `role`)
VALUES ('admin', 'admin@webadmin.local', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'default_salt_change_me', '系统管理员', 1, 1, 'admin');

-- 默认设备
INSERT IGNORE INTO `devices` (`device_code`, `device_name`, `device_type`, `model`, `manufacturer`, `line_code`, `factory_code`, `group_code`, `status`, `is_enabled`)
VALUES ('IMG-001', '注塑机-01', '注塑机', 'IMG-200T', '海天', 'LINE-01', 'FAC-01', 'GRP-01', 'active', 1);

INSERT IGNORE INTO `devices` (`device_code`, `device_name`, `device_type`, `model`, `manufacturer`, `line_code`, `factory_code`, `group_code`, `status`, `is_enabled`)
VALUES ('IMG-002', '注塑机-02', '注塑机', 'IMG-300T', '海天', 'LINE-01', 'FAC-01', 'GRP-01', 'active', 1);

-- 默认 MQTT Topic 配置
INSERT IGNORE INTO `mqtt_topic_configs` (`topic_name`, `description`, `topic_type`, `enabled`, `qos`, `storage_policy`)
VALUES ('SHXQ/NO1/KP3/IMG/ProcesEvent', '加工事件数据', 'event', 1, 1, 'save_raw');

INSERT IGNORE INTO `mqtt_topic_configs` (`topic_name`, `description`, `topic_type`, `enabled`, `qos`, `storage_policy`)
VALUES ('SHXQ/NO1/KP3/IMG/Alarm', '报警数据', 'alarm', 1, 1, 'save_raw');

INSERT IGNORE INTO `mqtt_topic_configs` (`topic_name`, `description`, `topic_type`, `enabled`, `qos`, `storage_policy`)
VALUES ('SHXQ/NO1/KP3/IMG/PV', '过程变量数据', 'pv', 1, 1, 'compress');

INSERT IGNORE INTO `mqtt_topic_configs` (`topic_name`, `description`, `topic_type`, `enabled`, `qos`, `storage_policy`)
VALUES ('SHXQ/NO1/KP3/IMG/SV', '设定值数据', 'sv', 1, 1, 'compress');

-- ============================================================
-- 完成
-- ============================================================
SELECT '数据库初始化完成' AS result;
