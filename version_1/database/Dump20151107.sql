CREATE DATABASE  IF NOT EXISTS `bmtools` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `bmtools`;
-- MySQL dump 10.13  Distrib 5.5.46, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: bmtools
-- ------------------------------------------------------
-- Server version	5.5.46-0ubuntu0.14.04.2

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
-- Table structure for table `custom_goals`
--

DROP TABLE IF EXISTS `custom_goals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custom_goals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) DEFAULT NULL,
  `goal_name` varchar(256) DEFAULT NULL,
  `description` text,
  `perspective` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_goals`
--

LOCK TABLES `custom_goals` WRITE;
/*!40000 ALTER TABLE `custom_goals` DISABLE KEYS */;
INSERT INTO `custom_goals` VALUES (1,'g1','Увеличение прибыли','В условиях рыночной экономики значение прибыли огромно. Стремление к ее получению ориентирует товаропроизводителей на увеличение объема производства продукции, нужной потребителю, снижение затрат на производство.',0),(2,'g3','Рост доли рынка','Объемы первичных продаж компании  (данные о собственных продажах) не могут дать точной информации для понимания того, что реально производит с компанией и ее брендами на рынке. Данные о продажах могут расти, но на рынках, которые растут более быстрыми темп',1);
/*!40000 ALTER TABLE `custom_goals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_kpi`
--

DROP TABLE IF EXISTS `custom_kpi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custom_kpi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) DEFAULT NULL,
  `description` text,
  `code` varchar(10) DEFAULT NULL,
  `formula` varchar(256) DEFAULT NULL,
  `link_to_desc` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_kpi`
--

LOCK TABLES `custom_kpi` WRITE;
/*!40000 ALTER TABLE `custom_kpi` DISABLE KEYS */;
INSERT INTO `custom_kpi` VALUES (1,'Экономическая добавленная стоимость','Прирост капитализации.','eva','(NP / IC – WACC) * IC = (ROI – WACC) * IC','http://finanalis.ru/litra/324/2293.html'),(2,'Прибыль до уплаты процентов, налогов и начисленной амортизации','','ebidta','Доход – Расходы (без процентов и налогов) + Амортизация',''),(3,'Доля рынка','','ms','','');
/*!40000 ALTER TABLE `custom_kpi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_linked_goals`
--

DROP TABLE IF EXISTS `custom_linked_goals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custom_linked_goals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_code` varchar(256) DEFAULT NULL,
  `child_code` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_linked_goals`
--

LOCK TABLES `custom_linked_goals` WRITE;
/*!40000 ALTER TABLE `custom_linked_goals` DISABLE KEYS */;
INSERT INTO `custom_linked_goals` VALUES (1,'g1','g3'),(2,'g3','g1');
/*!40000 ALTER TABLE `custom_linked_goals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_linked_kpi_to_goal`
--

DROP TABLE IF EXISTS `custom_linked_kpi_to_goal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custom_linked_kpi_to_goal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `goal_code` varchar(256) DEFAULT NULL,
  `kpi_code` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_linked_kpi_to_goal`
--

LOCK TABLES `custom_linked_kpi_to_goal` WRITE;
/*!40000 ALTER TABLE `custom_linked_kpi_to_goal` DISABLE KEYS */;
INSERT INTO `custom_linked_kpi_to_goal` VALUES (1,'g1','eva'),(2,'g3','ms'),(3,'g1','ebidta');
/*!40000 ALTER TABLE `custom_linked_kpi_to_goal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lib_goals`
--

DROP TABLE IF EXISTS `lib_goals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lib_goals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) DEFAULT NULL,
  `goal_name` varchar(256) DEFAULT NULL,
  `description` text,
  `perspective` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lib_goals`
--

LOCK TABLES `lib_goals` WRITE;
/*!40000 ALTER TABLE `lib_goals` DISABLE KEYS */;
INSERT INTO `lib_goals` VALUES (1,'g1','Увеличение прибыли','В условиях рыночной экономики значение прибыли огромно. Стремление к ее получению ориентирует товаропроизводителей на увеличение объема производства продукции, нужной потребителю, снижение затрат на производство.',0),(2,'g2','Снижение дебиторской задолженности','Дебиторская задолженность - задолженность организаций и физических лиц данной организации (например, задолженность покупателей за приобретенный товар или оказанные услуги, задолженность подотчетных лиц за выданные им денежные суммы) Соответственно, организ',0),(3,'g3','Рост доли рынка','Объемы первичных продаж компании  (данные о собственных продажах) не могут дать точной информации для понимания того, что реально производит с компанией и ее брендами на рынке. Данные о продажах могут расти, но на рынках, которые растут более быстрыми темп',1);
/*!40000 ALTER TABLE `lib_goals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lib_kpi`
--

DROP TABLE IF EXISTS `lib_kpi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lib_kpi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) DEFAULT NULL,
  `name` varchar(256) DEFAULT NULL,
  `description` text,
  `formula` varchar(256) DEFAULT NULL,
  `link_to_desc` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lib_kpi`
--

LOCK TABLES `lib_kpi` WRITE;
/*!40000 ALTER TABLE `lib_kpi` DISABLE KEYS */;
INSERT INTO `lib_kpi` VALUES (1,'eva','Экономическая добавленная стоимость','Прирост капитализации.','(NP / IC – WACC) * IC = (ROI – WACC) * IC','http://finanalis.ru/litra/324/2293.html'),(2,'wacc','Средневзвешенная цена капитала','(Собственный капитал / Инвестированный капитал) * Ожидаемая доходность от собственного капитала + (Заемные средства / Инвестированный капитал) * Ожидаемая доходность от заёмных средств * (1 – Ставка налога на прибыль для компании)','(Собственный капитал / Инвестированный капитал) * Ожидаемая доходность от собственного капитала + (Заемные средства / Инвестированный капитал) * Ожидаемая доходность от заёмных средств * (1 – Ставка налога на прибыль для компании)',NULL),(3,'gp','Валовая прибыль','Валовая прибыль = выручка от продаж – (себестоимость проданной продукции т.е. переменные издержки + прямые издержки на продажу продукции)','Выручка – Себестоимость с учетом амортизации',NULL),(4,'oi','Операционная прибыль','Операционная прибыль = валовая прибыль – (постоянные издержки + непрямые издержки). ','Выручка – Себестоимость – Постоянные и непрямые издержки',NULL),(5,'ebidta','Прибыль до уплаты процентов, налогов и начисленной амортизации','','Доход – Расходы (без процентов и налогов) + Амортизация',NULL),(6,'np','Чистая прибыль','Чистая прибыль = прибыль до налогообложения — налог на прибыль. Доход с учетом всех произведенных затрат. МСФО: валовая прибыль – издержки – проценты к уплате ','Валовая прибыль + Прочая операционная прибыль + Прибыль от финансовых операций – Налоги',NULL),(7,'ms','Доля рынка','','',NULL);
/*!40000 ALTER TABLE `lib_kpi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lib_linked_goals`
--

DROP TABLE IF EXISTS `lib_linked_goals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lib_linked_goals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_code` varchar(256) DEFAULT NULL,
  `child_code` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lib_linked_goals`
--

LOCK TABLES `lib_linked_goals` WRITE;
/*!40000 ALTER TABLE `lib_linked_goals` DISABLE KEYS */;
INSERT INTO `lib_linked_goals` VALUES (1,'g1','g3'),(2,'g3','g1'),(3,'g3','g2'),(4,'g2','g3');
/*!40000 ALTER TABLE `lib_linked_goals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lib_linked_kpi_to_goal`
--

DROP TABLE IF EXISTS `lib_linked_kpi_to_goal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lib_linked_kpi_to_goal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `goal_code` varchar(256) DEFAULT NULL,
  `kpi_code` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lib_linked_kpi_to_goal`
--

LOCK TABLES `lib_linked_kpi_to_goal` WRITE;
/*!40000 ALTER TABLE `lib_linked_kpi_to_goal` DISABLE KEYS */;
INSERT INTO `lib_linked_kpi_to_goal` VALUES (1,'g1','eva'),(2,'g1','wacc'),(3,'g1','gp'),(4,'g3','ms'),(5,'g1','np'),(6,'g1','oi'),(7,'g1','ebidta');
/*!40000 ALTER TABLE `lib_linked_kpi_to_goal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `org_structure`
--

DROP TABLE IF EXISTS `org_structure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `org_structure` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parentid` int(11) DEFAULT NULL,
  `org_name` varchar(256) DEFAULT NULL,
  `director` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `org_structure`
--

LOCK TABLES `org_structure` WRITE;
/*!40000 ALTER TABLE `org_structure` DISABLE KEYS */;
INSERT INTO `org_structure` VALUES (3,0,'Director',1),(5,3,'Операционный отдел',2),(6,3,'Маркетинг',2),(7,5,'Производство',2),(9,5,'Логистика',2),(10,6,'PR',1);
/*!40000 ALTER TABLE `org_structure` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `strategic_maps`
--

DROP TABLE IF EXISTS `strategic_maps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `strategic_maps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_code` varchar(10) DEFAULT NULL,
  `goal_code` varchar(10) DEFAULT NULL,
  `kpi_code` varchar(10) DEFAULT NULL,
  `metric_code` varchar(10) DEFAULT NULL,
  `event_code` varchar(10) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategic_maps`
--

LOCK TABLES `strategic_maps` WRITE;
/*!40000 ALTER TABLE `strategic_maps` DISABLE KEYS */;
INSERT INTO `strategic_maps` VALUES (1,'ent0','g1','','','',0,'2015-11-07 01:02:51'),(2,'ent0','g3','','','',0,'2015-11-07 01:02:55'),(3,'ent0','','eva','','',0,'2015-11-07 01:03:06'),(4,'ent0','','ebidta','','',0,'2015-11-07 01:03:06'),(5,'ent0','','ms','','',0,'2015-11-07 01:03:06');
/*!40000 ALTER TABLE `strategic_maps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `strategic_maps_desc`
--

DROP TABLE IF EXISTS `strategic_maps_desc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `strategic_maps_desc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) DEFAULT NULL,
  `name` varchar(256) DEFAULT NULL,
  `description` text,
  `owner` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategic_maps_desc`
--

LOCK TABLES `strategic_maps_desc` WRITE;
/*!40000 ALTER TABLE `strategic_maps_desc` DISABLE KEYS */;
INSERT INTO `strategic_maps_desc` VALUES (1,'ent0','Стратегическая карта компании','Стратегическая карта компании верхнего уровня.',0,0,'2015-11-07 00:52:39');
/*!40000 ALTER TABLE `strategic_maps_desc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `text_messages`
--

DROP TABLE IF EXISTS `text_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `text_messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(256) DEFAULT NULL,
  `text` text,
  `place` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `text_messages`
--

LOCK TABLES `text_messages` WRITE;
/*!40000 ALTER TABLE `text_messages` DISABLE KEYS */;
INSERT INTO `text_messages` VALUES (1,'step1_full_description','<p>Выберите отрасль в которой работает компания.</p>\n<p>Выбор влияет на формирование списков перспектив, целей, подцелей, показателей и мероприятий.\n</p>','Первая страница мастера. Полное описание.'),(2,'step1_name','Отрасль работы компании.','Первый шаг мастера'),(3,'step2_full_description','<p>\nДерево отражающее организационную структуру компании, в которое можно добавлять подчиненные единицы.\n</p>\n<p>\nКаждая ветка означает организационную единицу. </p>\n<p>\nПереход на следующий шаг, после составления структуры. Должна быть создана хотя бы одна организационная единица. \n</p>','Второй шаг мастера'),(4,'step2_name','Оганизационная структура компании.','Второй шаг мастера'),(5,'step3_full_description','<p>Выбрать из списка целей наиболее подходящие для компании.</p>\n<p>Сразу во время выбора, предлагаются цели которые связаны с выбранными.</p>','Третья страница мастера. Полное описание.'),(6,'step3_name','Формирование стратегической карты компании.','Третий шаг мастера'),(7,'step3_stage1_description','<p>Добавьте цели которые вам подходят. Поставьте галочки и нажмите \"Добавить\" </p>','Добавление новых целей и показателей.'),(8,'step3_subheader','<p>\nдля выбранных целей существуют связанные цели. Рекомендуем добавить их в стратегическую карту\n</p>',''),(9,'step3_stage3_description','<p>Для каждой цели подобраны показатели по которым можно измерять прогресс. </p> <p> Вы можете не использовать их, для этого снимите галочки напротив.</p>',''),(10,'step3_stage3_subheader','Добавьте к целям показатели',NULL);
/*!40000 ALTER TABLE `text_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) DEFAULT NULL,
  `name` varchar(256) DEFAULT NULL,
  `surname` varchar(256) DEFAULT NULL,
  `login` varchar(256) DEFAULT NULL,
  `password` varchar(256) DEFAULT NULL,
  `access_groups` varchar(256) DEFAULT NULL,
  `disabled` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'e0408fae-7c97-11e5-b5f1-f46d04d35cbd','Сергей','Фомин','test','Cthutq123','users,admin',0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wizard_configuration`
--

DROP TABLE IF EXISTS `wizard_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wizard_configuration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `industry` varchar(256) DEFAULT NULL,
  `cur_step` varchar(256) DEFAULT NULL,
  `status` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wizard_configuration`
--

LOCK TABLES `wizard_configuration` WRITE;
/*!40000 ALTER TABLE `wizard_configuration` DISABLE KEYS */;
INSERT INTO `wizard_configuration` VALUES (4,'1','','');
/*!40000 ALTER TABLE `wizard_configuration` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-07  2:30:15
