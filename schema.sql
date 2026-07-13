-- ============================================================
-- 游戏数据自动化搜集与分析平台 — 数据库建表脚本
-- 适用于 MySQL 5.7+ / 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS dify_test
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE dify_test;

-- -----------------------------------------------------------
-- 游戏基础信息表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS games (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(500)  NOT NULL,
    appid       INT           NOT NULL DEFAULT 0,
    release_date VARCHAR(50)  DEFAULT '',
    developer   VARCHAR(500)  DEFAULT '',
    publisher   VARCHAR(500)  DEFAULT '',
    genres      VARCHAR(500)  DEFAULT '',
    summary     TEXT,
    source      VARCHAR(50)   DEFAULT 'steam',
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_name_appid (name, appid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 游戏价格追踪表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS game_prices (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    appid            INT            NOT NULL DEFAULT 0,
    name             VARCHAR(500)   DEFAULT '',
    currency         VARCHAR(10)    DEFAULT 'CNY',
    initial_price    DECIMAL(10,2)  DEFAULT 0.00,
    final_price      DECIMAL(10,2)  DEFAULT 0.00,
    discount_percent INT            DEFAULT 0,
    recorded_at      DATE           NOT NULL,

    UNIQUE KEY uk_appid_name_date (appid, name, recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 同步日志表 (用于追踪每次同步执行情况)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS sync_logs (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    run_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    source        VARCHAR(50)  DEFAULT '',
    games_found   INT          DEFAULT 0,
    games_inserted INT         DEFAULT 0,
    prices_inserted INT        DEFAULT 0,
    status        VARCHAR(20)  DEFAULT 'success',
    error_msg     TEXT,
    duration_sec  DECIMAL(8,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------
-- 索引建议
-- -----------------------------------------------------------
-- 按日期查询价格
-- ALTER TABLE game_prices ADD INDEX idx_recorded_at (recorded_at);
-- 按来源筛选游戏
-- ALTER TABLE games ADD INDEX idx_source (source);
-- 按同步时间查询日志
-- ALTER TABLE sync_logs ADD INDEX idx_run_at (run_at);
