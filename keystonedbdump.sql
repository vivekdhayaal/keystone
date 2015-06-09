-- MySQL dump 10.13  Distrib 5.5.43, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: keystone
-- ------------------------------------------------------
-- Server version	5.5.43-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `access_token`
--

DROP TABLE IF EXISTS `access_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `access_token` (
  `id` varchar(64) NOT NULL,
  `access_secret` varchar(64) NOT NULL,
  `authorizing_user_id` varchar(64) NOT NULL,
  `project_id` varchar(64) NOT NULL,
  `role_ids` text NOT NULL,
  `consumer_id` varchar(64) NOT NULL,
  `expires_at` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_access_token_authorizing_user_id` (`authorizing_user_id`),
  KEY `consumer_id` (`consumer_id`),
  CONSTRAINT `access_token_consumer_id_fkey` FOREIGN KEY (`consumer_id`) REFERENCES `consumer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access_token`
--

LOCK TABLES `access_token` WRITE;
/*!40000 ALTER TABLE `access_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `access_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assignment`
--

DROP TABLE IF EXISTS `assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assignment` (
  `type` enum('UserProject','GroupProject','UserDomain','GroupDomain') NOT NULL,
  `actor_id` varchar(64) NOT NULL,
  `target_id` varchar(64) NOT NULL,
  `role_id` varchar(64) NOT NULL,
  `inherited` tinyint(1) NOT NULL,
  PRIMARY KEY (`type`,`actor_id`,`target_id`,`role_id`,`inherited`),
  KEY `ix_actor_id` (`actor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assignment`
--

LOCK TABLES `assignment` WRITE;
/*!40000 ALTER TABLE `assignment` DISABLE KEYS */;
INSERT INTO `assignment` VALUES ('UserProject','90f0471df5a749e59e997f772b146b07','03a5bd375fbc415a9be7f280e6191b29','a4f4de83ad05477d98a271ec79e44ad2',0),('UserProject','90f0471df5a749e59e997f772b146b07','2438933b3e0f4420b099209d55ced8bc','a4f4de83ad05477d98a271ec79e44ad2',0),('UserProject','90f0471df5a749e59e997f772b146b07','2438933b3e0f4420b099209d55ced8bc','b76f278949b84582a89cd979223d936a',0),('UserProject','cf1f87101f8d4e8a92dc8a5a7cfa319e','2438933b3e0f4420b099209d55ced8bc','345e4b74170f4d889275880a9cfcccd2',0),('UserProject','cf1f87101f8d4e8a92dc8a5a7cfa319e','5488164611064755a49ff7b9d456bc49','345e4b74170f4d889275880a9cfcccd2',0);
/*!40000 ALTER TABLE `assignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consumer`
--

DROP TABLE IF EXISTS `consumer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `consumer` (
  `id` varchar(64) NOT NULL,
  `description` varchar(64) DEFAULT NULL,
  `secret` varchar(64) NOT NULL,
  `extra` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consumer`
--

LOCK TABLES `consumer` WRITE;
/*!40000 ALTER TABLE `consumer` DISABLE KEYS */;
/*!40000 ALTER TABLE `consumer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credential`
--

DROP TABLE IF EXISTS `credential`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `credential` (
  `id` varchar(64) NOT NULL,
  `user_id` varchar(64) NOT NULL,
  `project_id` varchar(64) DEFAULT NULL,
  `blob` text NOT NULL,
  `type` varchar(255) NOT NULL,
  `extra` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credential`
--

LOCK TABLES `credential` WRITE;
/*!40000 ALTER TABLE `credential` DISABLE KEYS */;
/*!40000 ALTER TABLE `credential` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `domain`
--

DROP TABLE IF EXISTS `domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `extra` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ixu_domain_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `domain`
--

LOCK TABLES `domain` WRITE;
/*!40000 ALTER TABLE `domain` DISABLE KEYS */;
INSERT INTO `domain` VALUES ('default','Default',1,'{\"description\": \"Owns users and tenants (i.e. projects) available on Identity API v2.\"}');
/*!40000 ALTER TABLE `domain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `endpoint`
--

DROP TABLE IF EXISTS `endpoint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `endpoint` (
  `id` varchar(64) NOT NULL,
  `legacy_endpoint_id` varchar(64) DEFAULT NULL,
  `interface` varchar(8) NOT NULL,
  `service_id` varchar(64) NOT NULL,
  `url` text NOT NULL,
  `extra` text,
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `region_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `service_id` (`service_id`),
  KEY `fk_endpoint_region_id` (`region_id`),
  CONSTRAINT `endpoint_service_id_fkey` FOREIGN KEY (`service_id`) REFERENCES `service` (`id`),
  CONSTRAINT `fk_endpoint_region_id` FOREIGN KEY (`region_id`) REFERENCES `region` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `endpoint`
--

LOCK TABLES `endpoint` WRITE;
/*!40000 ALTER TABLE `endpoint` DISABLE KEYS */;
INSERT INTO `endpoint` VALUES ('01092d12a8064c7caccba2b5b9e5f24f','59fdfb5a5c884451afe2e520f8020785','public','58138146b86b4627bd6500856826a5d8','http://10.0.2.15:5000/v2.0','{}',1,'RegionOne'),('7b5fa9a506824b8a8970720ab126e198','59fdfb5a5c884451afe2e520f8020785','admin','58138146b86b4627bd6500856826a5d8','http://10.0.2.15:35357/v2.0','{}',1,'RegionOne'),('c4b8ecbc073e47e6b194552754e1e575','59fdfb5a5c884451afe2e520f8020785','internal','58138146b86b4627bd6500856826a5d8','http://10.0.2.15:5000/v2.0','{}',1,'RegionOne');
/*!40000 ALTER TABLE `endpoint` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `endpoint_group`
--

DROP TABLE IF EXISTS `endpoint_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `endpoint_group` (
  `id` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text,
  `filters` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `endpoint_group`
--

LOCK TABLES `endpoint_group` WRITE;
/*!40000 ALTER TABLE `endpoint_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `endpoint_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `federation_protocol`
--

DROP TABLE IF EXISTS `federation_protocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `federation_protocol` (
  `id` varchar(64) NOT NULL,
  `idp_id` varchar(64) NOT NULL,
  `mapping_id` varchar(64) NOT NULL,
  PRIMARY KEY (`id`,`idp_id`),
  KEY `idp_id` (`idp_id`),
  CONSTRAINT `federation_protocol_ibfk_1` FOREIGN KEY (`idp_id`) REFERENCES `identity_provider` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `federation_protocol`
--

LOCK TABLES `federation_protocol` WRITE;
/*!40000 ALTER TABLE `federation_protocol` DISABLE KEYS */;
/*!40000 ALTER TABLE `federation_protocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group` (
  `id` varchar(64) NOT NULL,
  `domain_id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `description` text,
  `extra` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ixu_group_name_domain_id` (`domain_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group`
--

LOCK TABLES `group` WRITE;
/*!40000 ALTER TABLE `group` DISABLE KEYS */;
INSERT INTO `group` VALUES ('c330e009e6674b479544cab7feef17ef','default','admins','openstack admin group','{}'),('d32b0f69face4b42a7c482b8cac447e6','default','nonadmins','non-admin group','{}');
/*!40000 ALTER TABLE `group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `id_mapping`
--

DROP TABLE IF EXISTS `id_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `id_mapping` (
  `public_id` varchar(64) NOT NULL,
  `domain_id` varchar(64) NOT NULL,
  `local_id` varchar(64) NOT NULL,
  `entity_type` enum('user','group') NOT NULL,
  PRIMARY KEY (`public_id`),
  UNIQUE KEY `domain_id` (`domain_id`,`local_id`,`entity_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `id_mapping`
--

LOCK TABLES `id_mapping` WRITE;
/*!40000 ALTER TABLE `id_mapping` DISABLE KEYS */;
/*!40000 ALTER TABLE `id_mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `identity_provider`
--

DROP TABLE IF EXISTS `identity_provider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `identity_provider` (
  `id` varchar(64) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `identity_provider`
--

LOCK TABLES `identity_provider` WRITE;
/*!40000 ALTER TABLE `identity_provider` DISABLE KEYS */;
/*!40000 ALTER TABLE `identity_provider` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `idp_remote_ids`
--

DROP TABLE IF EXISTS `idp_remote_ids`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idp_remote_ids` (
  `idp_id` varchar(64) DEFAULT NULL,
  `remote_id` varchar(255) NOT NULL,
  PRIMARY KEY (`remote_id`),
  KEY `idp_id` (`idp_id`),
  CONSTRAINT `idp_remote_ids_ibfk_1` FOREIGN KEY (`idp_id`) REFERENCES `identity_provider` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `idp_remote_ids`
--

LOCK TABLES `idp_remote_ids` WRITE;
/*!40000 ALTER TABLE `idp_remote_ids` DISABLE KEYS */;
/*!40000 ALTER TABLE `idp_remote_ids` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mapping`
--

DROP TABLE IF EXISTS `mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mapping` (
  `id` varchar(64) NOT NULL,
  `rules` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mapping`
--

LOCK TABLES `mapping` WRITE;
/*!40000 ALTER TABLE `mapping` DISABLE KEYS */;
/*!40000 ALTER TABLE `mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `migrate_version`
--

DROP TABLE IF EXISTS `migrate_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `migrate_version` (
  `repository_id` varchar(250) NOT NULL,
  `repository_path` text,
  `version` int(11) DEFAULT NULL,
  PRIMARY KEY (`repository_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `migrate_version`
--

LOCK TABLES `migrate_version` WRITE;
/*!40000 ALTER TABLE `migrate_version` DISABLE KEYS */;
INSERT INTO `migrate_version` VALUES ('endpoint_filter','/opt/stack/keystone/keystone/contrib/endpoint_filter/migrate_repo',2),('endpoint_policy','/opt/stack/keystone/keystone/contrib/endpoint_policy/migrate_repo',1),('federation','/opt/stack/keystone/keystone/contrib/federation/migrate_repo',8),('keystone','/opt/stack/keystone/keystone/common/sql/migrate_repo',73),('oauth1','/opt/stack/keystone/keystone/contrib/oauth1/migrate_repo',5),('revoke','/opt/stack/keystone/keystone/contrib/revoke/migrate_repo',2);
/*!40000 ALTER TABLE `migrate_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policy`
--

DROP TABLE IF EXISTS `policy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `policy` (
  `id` varchar(64) NOT NULL,
  `type` varchar(255) NOT NULL,
  `blob` text NOT NULL,
  `extra` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policy`
--

LOCK TABLES `policy` WRITE;
/*!40000 ALTER TABLE `policy` DISABLE KEYS */;
/*!40000 ALTER TABLE `policy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policy_association`
--

DROP TABLE IF EXISTS `policy_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `policy_association` (
  `id` varchar(64) NOT NULL,
  `policy_id` varchar(64) NOT NULL,
  `endpoint_id` varchar(64) DEFAULT NULL,
  `service_id` varchar(64) DEFAULT NULL,
  `region_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `endpoint_id` (`endpoint_id`,`service_id`,`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policy_association`
--

LOCK TABLES `policy_association` WRITE;
/*!40000 ALTER TABLE `policy_association` DISABLE KEYS */;
/*!40000 ALTER TABLE `policy_association` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `extra` text,
  `description` text,
  `enabled` tinyint(1) DEFAULT NULL,
  `domain_id` varchar(64) NOT NULL,
  `parent_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ixu_project_name_domain_id` (`domain_id`,`name`),
  KEY `project_parent_id_fkey` (`parent_id`),
  CONSTRAINT `fk_project_domain_id` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`),
  CONSTRAINT `project_parent_id_fkey` FOREIGN KEY (`parent_id`) REFERENCES `project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
INSERT INTO `project` VALUES ('03a5bd375fbc415a9be7f280e6191b29','invisible_to_admin','{}',NULL,1,'default',NULL),('2438933b3e0f4420b099209d55ced8bc','demo','{}',NULL,1,'default',NULL),('5488164611064755a49ff7b9d456bc49','admin','{}',NULL,1,'default',NULL),('fc1e56d8c6b746ba9e0ef2810e84acbd','service','{}',NULL,1,'default',NULL);
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_endpoint`
--

DROP TABLE IF EXISTS `project_endpoint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_endpoint` (
  `endpoint_id` varchar(64) NOT NULL,
  `project_id` varchar(64) NOT NULL,
  PRIMARY KEY (`endpoint_id`,`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_endpoint`
--

LOCK TABLES `project_endpoint` WRITE;
/*!40000 ALTER TABLE `project_endpoint` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_endpoint` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_endpoint_group`
--

DROP TABLE IF EXISTS `project_endpoint_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_endpoint_group` (
  `endpoint_group_id` varchar(64) NOT NULL,
  `project_id` varchar(64) NOT NULL,
  PRIMARY KEY (`endpoint_group_id`,`project_id`),
  CONSTRAINT `project_endpoint_group_ibfk_1` FOREIGN KEY (`endpoint_group_id`) REFERENCES `endpoint_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_endpoint_group`
--

LOCK TABLES `project_endpoint_group` WRITE;
/*!40000 ALTER TABLE `project_endpoint_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_endpoint_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `region`
--

DROP TABLE IF EXISTS `region`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region` (
  `id` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `parent_region_id` varchar(255) DEFAULT NULL,
  `extra` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `region`
--

LOCK TABLES `region` WRITE;
/*!40000 ALTER TABLE `region` DISABLE KEYS */;
INSERT INTO `region` VALUES ('RegionOne','',NULL,'{}');
/*!40000 ALTER TABLE `region` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `request_token`
--

DROP TABLE IF EXISTS `request_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `request_token` (
  `id` varchar(64) NOT NULL,
  `request_secret` varchar(64) NOT NULL,
  `verifier` varchar(64) DEFAULT NULL,
  `authorizing_user_id` varchar(64) DEFAULT NULL,
  `requested_project_id` varchar(64) NOT NULL,
  `role_ids` text,
  `consumer_id` varchar(64) NOT NULL,
  `expires_at` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_request_token_consumer_id` (`consumer_id`),
  CONSTRAINT `request_token_consumer_id_fkey` FOREIGN KEY (`consumer_id`) REFERENCES `consumer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `request_token`
--

LOCK TABLES `request_token` WRITE;
/*!40000 ALTER TABLE `request_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `request_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `revocation_event`
--

DROP TABLE IF EXISTS `revocation_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `revocation_event` (
  `id` varchar(64) NOT NULL,
  `domain_id` varchar(64) DEFAULT NULL,
  `project_id` varchar(64) DEFAULT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `role_id` varchar(64) DEFAULT NULL,
  `trust_id` varchar(64) DEFAULT NULL,
  `consumer_id` varchar(64) DEFAULT NULL,
  `access_token_id` varchar(64) DEFAULT NULL,
  `issued_before` datetime NOT NULL,
  `expires_at` datetime DEFAULT NULL,
  `revoked_at` datetime NOT NULL,
  `audit_id` varchar(32) DEFAULT NULL,
  `audit_chain_id` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_revocation_event_revoked_at` (`revoked_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `revocation_event`
--

LOCK TABLES `revocation_event` WRITE;
/*!40000 ALTER TABLE `revocation_event` DISABLE KEYS */;
/*!40000 ALTER TABLE `revocation_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `extra` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ixu_role_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES ('345e4b74170f4d889275880a9cfcccd2','admin','{}'),('8075c321b72c4a4b985c2ebc51aba96a','service','{}'),('a4f4de83ad05477d98a271ec79e44ad2','Member','{}'),('b76f278949b84582a89cd979223d936a','anotherrole','{}'),('c6a53c98412643e6972e759d140570de','ResellerAdmin','{}');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensitive_config`
--

DROP TABLE IF EXISTS `sensitive_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sensitive_config` (
  `domain_id` varchar(64) NOT NULL,
  `group` varchar(255) NOT NULL,
  `option` varchar(255) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY (`domain_id`,`group`,`option`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensitive_config`
--

LOCK TABLES `sensitive_config` WRITE;
/*!40000 ALTER TABLE `sensitive_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `sensitive_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service`
--

DROP TABLE IF EXISTS `service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service` (
  `id` varchar(64) NOT NULL,
  `type` varchar(255) DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `extra` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service`
--

LOCK TABLES `service` WRITE;
/*!40000 ALTER TABLE `service` DISABLE KEYS */;
INSERT INTO `service` VALUES ('58138146b86b4627bd6500856826a5d8','identity',1,'{\"name\": \"keystone\", \"description\": \"Keystone Identity Service\"}');
/*!40000 ALTER TABLE `service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_provider`
--

DROP TABLE IF EXISTS `service_provider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_provider` (
  `auth_url` varchar(256) NOT NULL,
  `id` varchar(64) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `description` text,
  `sp_url` varchar(256) NOT NULL,
  `relay_state_prefix` varchar(256) NOT NULL DEFAULT 'ss:mem:',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_provider`
--

LOCK TABLES `service_provider` WRITE;
/*!40000 ALTER TABLE `service_provider` DISABLE KEYS */;
/*!40000 ALTER TABLE `service_provider` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token`
--

DROP TABLE IF EXISTS `token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `token` (
  `id` varchar(64) NOT NULL,
  `expires` datetime DEFAULT NULL,
  `extra` text,
  `valid` tinyint(1) NOT NULL,
  `trust_id` varchar(64) DEFAULT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_token_expires` (`expires`),
  KEY `ix_token_expires_valid` (`expires`,`valid`),
  KEY `ix_token_user_id` (`user_id`),
  KEY `ix_token_trust_id` (`trust_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token`
--

LOCK TABLES `token` WRITE;
/*!40000 ALTER TABLE `token` DISABLE KEYS */;
INSERT INTO `token` VALUES ('08ad5f593c4c456985fecaf013d01faf','2015-06-05 10:05:37','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:05:37.738142\", \"expires\": \"2015-06-05T10:05:37Z\", \"id\": \"08ad5f593c4c456985fecaf013d01faf\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"4drk-lqdRz2Z3minkS0dTQ\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"08ad5f593c4c456985fecaf013d01faf\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('0efed5ec4e3c4cd192d3e5e7e79a114b','2015-06-05 07:44:34','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:44:34.191133\", \"expires\": \"2015-06-05T07:44:34Z\", \"id\": \"0efed5ec4e3c4cd192d3e5e7e79a114b\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"BtHgHcDcTnK8pKq37wMBuA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"0efed5ec4e3c4cd192d3e5e7e79a114b\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('18507431f97949f59fd2a9b44638f05f','2015-06-05 08:24:38','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T07:24:38.084387\", \"expires\": \"2015-06-05T08:24:38Z\", \"id\": \"18507431f97949f59fd2a9b44638f05f\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"BVM7Jgs9TiOhisagXKGXuA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"18507431f97949f59fd2a9b44638f05f\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('1a37d9b5e0a94e4bb358b00be9668bb4','2015-06-05 10:04:42','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:04:42.614085\", \"expires\": \"2015-06-05T10:04:42Z\", \"id\": \"1a37d9b5e0a94e4bb358b00be9668bb4\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"z8jV-FOnTSKcOS5cOS_WdQ\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"1a37d9b5e0a94e4bb358b00be9668bb4\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('27abac4cde1245f5addd9fce95511ec7','2015-06-05 07:41:22','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:41:22.817926\", \"expires\": \"2015-06-05T07:41:22Z\", \"id\": \"27abac4cde1245f5addd9fce95511ec7\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"HXTCAlyDSlOj4HzW56OrNg\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"27abac4cde1245f5addd9fce95511ec7\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('2b7b8cda72264cc08b5c5a7452b7ee9a','2015-06-08 07:06:19','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-08T06:06:19.020266\", \"expires\": \"2015-06-08T07:06:19Z\", \"id\": \"2b7b8cda72264cc08b5c5a7452b7ee9a\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"7o3VjSmZTO2Sl9S_sO6MGA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"name\": \"admin\", \"extra\": {\"email\": null}, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"email\": null}, \"key\": \"2b7b8cda72264cc08b5c5a7452b7ee9a\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('2cf9b70500a44fb5b9724f8e52273213','2015-06-05 07:44:39','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:44:39.184992\", \"expires\": \"2015-06-05T07:44:39Z\", \"id\": \"2cf9b70500a44fb5b9724f8e52273213\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"ytrp6VGeT4Gg7n0ljQIO3A\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"2cf9b70500a44fb5b9724f8e52273213\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('39aa7eac1c5e486093e4ec54f6a7e459','2015-06-05 10:04:59','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:04:59.667083\", \"expires\": \"2015-06-05T10:04:59Z\", \"id\": \"39aa7eac1c5e486093e4ec54f6a7e459\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"UD0FDADMSIWULnjRBVlBEA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"39aa7eac1c5e486093e4ec54f6a7e459\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('4b6259786177416097cd0b9ce32640a3','2015-06-05 10:04:53','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:04:53.220115\", \"expires\": \"2015-06-05T10:04:53Z\", \"id\": \"4b6259786177416097cd0b9ce32640a3\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"SQFuSYVER56W6Ga2Euzs_g\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"4b6259786177416097cd0b9ce32640a3\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('4ce001a047174bca9a14c2c63328a3cc','2015-06-05 07:41:17','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:41:17.365495\", \"expires\": \"2015-06-05T07:41:17Z\", \"id\": \"4ce001a047174bca9a14c2c63328a3cc\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"3JV8aljJTmeuPxgh66MFjQ\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"4ce001a047174bca9a14c2c63328a3cc\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('5b1315c195784300b400f97f6ae8cf7a','2015-06-05 10:04:42','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:04:42.502089\", \"expires\": \"2015-06-05T10:04:42Z\", \"id\": \"5b1315c195784300b400f97f6ae8cf7a\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"HEsjIWijRQm53izL1bvnJQ\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"5b1315c195784300b400f97f6ae8cf7a\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('63bd64b1e1a54fe2bae54c4cc835b9ec','2015-06-05 07:41:17','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:41:17.290536\", \"expires\": \"2015-06-05T07:41:17Z\", \"id\": \"63bd64b1e1a54fe2bae54c4cc835b9ec\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"e5wC4X5KSNKAVQ2JGPtD_g\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"63bd64b1e1a54fe2bae54c4cc835b9ec\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('64bba50641f440378d9b1b85114b8727','2015-06-05 10:05:33','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:05:33.459323\", \"expires\": \"2015-06-05T10:05:33Z\", \"id\": \"64bba50641f440378d9b1b85114b8727\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"zfnZ1nUBR0i9avi2V0gfmQ\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"64bba50641f440378d9b1b85114b8727\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('6d08dbdfceef4bda907bc3509d5e2e77','2015-06-05 10:05:37','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:05:37.668260\", \"expires\": \"2015-06-05T10:05:37Z\", \"id\": \"6d08dbdfceef4bda907bc3509d5e2e77\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"dtk7tqpUQVyPQ7vMaTl4jA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"6d08dbdfceef4bda907bc3509d5e2e77\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('79cb442d0485463caee23ccc5851cd82','2015-06-05 07:44:45','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:44:45.894256\", \"expires\": \"2015-06-05T07:44:45Z\", \"id\": \"79cb442d0485463caee23ccc5851cd82\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"cLwY371dSiG-YBPPiXDLzg\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"79cb442d0485463caee23ccc5851cd82\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('7e93ab541b8c49839dfc3625c42046f2','2015-06-05 10:05:18','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:05:18.545772\", \"expires\": \"2015-06-05T10:05:18Z\", \"id\": \"7e93ab541b8c49839dfc3625c42046f2\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"9RScrjSxQ26DhIi9hB_flA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"7e93ab541b8c49839dfc3625c42046f2\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('9014eeb6e8cf4a8dbd43e609f0f0db53','2015-06-05 10:05:18','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:05:18.606924\", \"expires\": \"2015-06-05T10:05:18Z\", \"id\": \"9014eeb6e8cf4a8dbd43e609f0f0db53\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"BjSdXn06ScarMSKzCcKyYA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"9014eeb6e8cf4a8dbd43e609f0f0db53\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('9970b63854cf4f6783455dfadabf84a7','2015-06-08 07:06:30','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-08T06:06:30.072504\", \"expires\": \"2015-06-08T07:06:30Z\", \"id\": \"9970b63854cf4f6783455dfadabf84a7\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"FLUE8BgZQjufObjxeOkAJA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"name\": \"admin\", \"extra\": {\"email\": null}, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"email\": null}, \"key\": \"9970b63854cf4f6783455dfadabf84a7\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('9c24cde4042348419bd138152bc93933','2015-06-08 07:06:29','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-08T06:06:29.981995\", \"expires\": \"2015-06-08T07:06:29Z\", \"id\": \"9c24cde4042348419bd138152bc93933\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"pad3WlxgSr2i03z6ON0F4A\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"name\": \"admin\", \"extra\": {\"email\": null}, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"email\": null}, \"key\": \"9c24cde4042348419bd138152bc93933\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('b9ed241254a341cc94c98dacd38704e9','2015-06-05 10:04:53','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:04:53.156528\", \"expires\": \"2015-06-05T10:04:53Z\", \"id\": \"b9ed241254a341cc94c98dacd38704e9\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"NbhRxtFCRfmDl5f4pzb6gA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"b9ed241254a341cc94c98dacd38704e9\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('bd9347f3eb0e487c827848e21a4438d8','2015-06-05 10:04:59','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:04:59.730842\", \"expires\": \"2015-06-05T10:04:59Z\", \"id\": \"bd9347f3eb0e487c827848e21a4438d8\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"Hxn7J1InRKKH00YyL1i1xw\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"bd9347f3eb0e487c827848e21a4438d8\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('be81449c631d43049af37ecf21ba731d','2015-06-08 07:06:18','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-08T06:06:18.926570\", \"expires\": \"2015-06-08T07:06:18Z\", \"id\": \"be81449c631d43049af37ecf21ba731d\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"HQg8BfMtQkinFzWJPe9GNw\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"name\": \"admin\", \"extra\": {\"email\": null}, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"email\": null}, \"key\": \"be81449c631d43049af37ecf21ba731d\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('c98ec8bb6fcf4d02aebdea03996752ff','2015-06-05 07:41:22','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:41:22.970881\", \"expires\": \"2015-06-05T07:41:22Z\", \"id\": \"c98ec8bb6fcf4d02aebdea03996752ff\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"hPrv0f4NSbSo4cdRhmF1TA\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"c98ec8bb6fcf4d02aebdea03996752ff\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('c9ab79288aca429483efeb9d525e755c','2015-06-05 07:44:45','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:44:45.953144\", \"expires\": \"2015-06-05T07:44:45Z\", \"id\": \"c9ab79288aca429483efeb9d525e755c\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"hS0e1z0wR4mUrqHQfFEdcQ\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"c9ab79288aca429483efeb9d525e755c\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('cfa89951e7334327a455aafb886d8677','2015-06-05 07:44:39','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:44:39.114019\", \"expires\": \"2015-06-05T07:44:39Z\", \"id\": \"cfa89951e7334327a455aafb886d8677\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"r7S7vIofTtmysq8gT87PXQ\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"cfa89951e7334327a455aafb886d8677\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('d02509152f2141a09b7f4a67cd6da1e9','2015-06-05 07:44:34','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T06:44:34.078783\", \"expires\": \"2015-06-05T07:44:34Z\", \"id\": \"d02509152f2141a09b7f4a67cd6da1e9\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"c-KPX7oXStaSWefQOM9IXg\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"d02509152f2141a09b7f4a67cd6da1e9\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('d3fd713350bf400ebb518f4a39ed4179','2015-06-05 08:24:37','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T07:24:37.238112\", \"expires\": \"2015-06-05T08:24:37Z\", \"id\": \"d3fd713350bf400ebb518f4a39ed4179\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"_LSEBeh1TEKWlLMzPD_-pw\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"d3fd713350bf400ebb518f4a39ed4179\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e'),('e88704c34b0f45ff87ddb54e101f3699','2015-06-05 10:05:33','{\"bind\": null, \"token_data\": {\"access\": {\"token\": {\"issued_at\": \"2015-06-05T09:05:33.521815\", \"expires\": \"2015-06-05T10:05:33Z\", \"id\": \"e88704c34b0f45ff87ddb54e101f3699\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"audit_ids\": [\"A01qfOEKTV-b00QYaUh5YQ\"]}, \"serviceCatalog\": [{\"endpoints\": [{\"adminURL\": \"http://10.0.2.15:35357/v2.0\", \"region\": \"RegionOne\", \"id\": \"01092d12a8064c7caccba2b5b9e5f24f\", \"internalURL\": \"http://10.0.2.15:5000/v2.0\", \"publicURL\": \"http://10.0.2.15:5000/v2.0\"}], \"endpoints_links\": [], \"type\": \"identity\", \"name\": \"keystone\"}], \"user\": {\"username\": \"admin\", \"roles_links\": [], \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"roles\": [{\"name\": \"admin\"}], \"name\": \"admin\"}, \"metadata\": {\"is_admin\": 0, \"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}}, \"user\": {\"username\": \"admin\", \"email\": null, \"enabled\": true, \"id\": \"cf1f87101f8d4e8a92dc8a5a7cfa319e\", \"name\": \"admin\"}, \"key\": \"e88704c34b0f45ff87ddb54e101f3699\", \"token_version\": \"v2.0\", \"tenant\": {\"id\": \"5488164611064755a49ff7b9d456bc49\", \"enabled\": true, \"description\": null, \"name\": \"admin\"}, \"metadata\": {\"roles\": [\"345e4b74170f4d889275880a9cfcccd2\"]}}',1,NULL,'cf1f87101f8d4e8a92dc8a5a7cfa319e');
/*!40000 ALTER TABLE `token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trust`
--

DROP TABLE IF EXISTS `trust`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trust` (
  `id` varchar(64) NOT NULL,
  `trustor_user_id` varchar(64) NOT NULL,
  `trustee_user_id` varchar(64) NOT NULL,
  `project_id` varchar(64) DEFAULT NULL,
  `impersonation` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  `remaining_uses` int(11) DEFAULT NULL,
  `extra` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trust`
--

LOCK TABLES `trust` WRITE;
/*!40000 ALTER TABLE `trust` DISABLE KEYS */;
/*!40000 ALTER TABLE `trust` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trust_role`
--

DROP TABLE IF EXISTS `trust_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trust_role` (
  `trust_id` varchar(64) NOT NULL,
  `role_id` varchar(64) NOT NULL,
  PRIMARY KEY (`trust_id`,`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trust_role`
--

LOCK TABLES `trust_role` WRITE;
/*!40000 ALTER TABLE `trust_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `trust_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `extra` text,
  `password` varchar(128) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `domain_id` varchar(64) NOT NULL,
  `default_project_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ixu_user_name_domain_id` (`domain_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('90f0471df5a749e59e997f772b146b07','demo','{\"email\": \"demo@example.com\"}','$6$rounds=40000$5Y2F4aQVM9I6N0xX$GcgsL3QoZG8MkPCngRyU6mykw.SeF3IqCmAU4TUA.QkzNiq9SihYQSDXVPY1TEFvcGhadL2JG1Dmz6OGxEIKA/',1,'default',NULL),('cf1f87101f8d4e8a92dc8a5a7cfa319e','admin','{\"email\": null}','$6$rounds=40000$mYA6Iwpl6dm.ijML$swgnT0JM/lLoagtwnY.JL/e24TRh97koMIO/Gx9tDHajzeZpuEXQKLcYJ0.DQoVxIpCCPV0xKME6llo73oqhz/',1,'default',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_membership`
--

DROP TABLE IF EXISTS `user_group_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_membership` (
  `user_id` varchar(64) NOT NULL,
  `group_id` varchar(64) NOT NULL,
  PRIMARY KEY (`user_id`,`group_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `fk_user_group_membership_group_id` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`),
  CONSTRAINT `fk_user_group_membership_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_membership`
--

LOCK TABLES `user_group_membership` WRITE;
/*!40000 ALTER TABLE `user_group_membership` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_group_membership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `whitelisted_config`
--

DROP TABLE IF EXISTS `whitelisted_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `whitelisted_config` (
  `domain_id` varchar(64) NOT NULL,
  `group` varchar(255) NOT NULL,
  `option` varchar(255) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY (`domain_id`,`group`,`option`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `whitelisted_config`
--

LOCK TABLES `whitelisted_config` WRITE;
/*!40000 ALTER TABLE `whitelisted_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `whitelisted_config` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-06-08  6:08:29
