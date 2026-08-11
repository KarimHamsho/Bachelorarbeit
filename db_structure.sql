-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server-Version:               11.8.3-MariaDB - mariadb.org binary distribution
-- Server-Betriebssystem:        Win64
-- HeidiSQL Version:             12.11.0.7065
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Exportiere Struktur von Tabelle sobotify_data.human_speak
CREATE TABLE IF NOT EXISTS `human_speak` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ts` datetime(6) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `message` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_human_speak_ts` (`ts`),
  KEY `idx_human_speak_topic` (`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=27208 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle sobotify_data.logging_meta
CREATE TABLE IF NOT EXISTS `logging_meta` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ts` datetime(6) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `message` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_logging_meta_ts` (`ts`),
  KEY `idx_logging_meta_topic` (`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=9402 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle sobotify_data.log_raw
CREATE TABLE IF NOT EXISTS `log_raw` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ts` datetime(6) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `message` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ts` (`ts`),
  KEY `idx_topic` (`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=740 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle sobotify_data.quiz_interactions
CREATE TABLE IF NOT EXISTS `quiz_interactions` (
  `question_time` datetime(6) DEFAULT NULL,
  `question_text` text DEFAULT NULL,
  `answer_time` datetime(6) DEFAULT NULL,
  `answer_text` text DEFAULT NULL,
  `latency_ms` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle sobotify_data.robot_reaction
CREATE TABLE IF NOT EXISTS `robot_reaction` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ts` datetime(6) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `message` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_robot_reaction_ts` (`ts`),
  KEY `idx_robot_reaction_topic` (`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=703522 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle sobotify_data.robot_speak
CREATE TABLE IF NOT EXISTS `robot_speak` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ts` datetime(6) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `message` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_robot_speak_ts` (`ts`),
  KEY `idx_robot_speak_topic` (`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=13651 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle sobotify_data.settings_human
CREATE TABLE IF NOT EXISTS `settings_human` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ts` datetime(6) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `message` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_settings_human_ts` (`ts`),
  KEY `idx_settings_human_topic` (`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=7138 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle sobotify_data.settings_robot
CREATE TABLE IF NOT EXISTS `settings_robot` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ts` datetime(6) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `message` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_settings_robot_ts` (`ts`),
  KEY `idx_settings_robot_topic` (`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=35923 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Daten-Export vom Benutzer nicht ausgewählt

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
