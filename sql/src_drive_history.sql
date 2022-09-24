-- MySQL dump 10.13  Distrib 8.0.25, for macos11 (x86_64)
--
-- Host: localhost    Database: src
-- ------------------------------------------------------
-- Server version	8.0.25

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `drive_history`
--

DROP TABLE IF EXISTS `drive_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drive_history` (
  `idx` int NOT NULL AUTO_INCREMENT,
  `user` varchar(44) NOT NULL,
  `start_at` int NOT NULL,
  `end_at` int DEFAULT NULL,
  `driving_distance` float(8,3) NOT NULL,
  `safe_driving_distance` float(8,3) NOT NULL,
  `mining_distance` float(8,3) NOT NULL,
  `total_mining` float(6,3) NOT NULL,
  `running_time` int NOT NULL,
  `nft_rarity` varchar(30) NOT NULL,
  `nft_usage` float(6,3) NOT NULL,
  PRIMARY KEY (`idx`),
  KEY `user` (`user`),
  CONSTRAINT `drive_history_ibfk_1` FOREIGN KEY (`user`) REFERENCES `user_info` (`wallet`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drive_history`
--

LOCK TABLES `drive_history` WRITE;
/*!40000 ALTER TABLE `drive_history` DISABLE KEYS */;
INSERT INTO `drive_history` VALUES (1,'BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa',1663996666,1663999010,0.444,0.444,0.444,0.444,2344,'common',0.048),(2,'BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa',1663999573,1663999742,0.333,0.333,0.333,0.333,169,'common',0.054);
/*!40000 ALTER TABLE `drive_history` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-09-24 15:48:55
