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
  `measure` int(11) DEFAULT '0',
  `target_responsible` int(11) DEFAULT '0',
  `fact_responsible` int(11) DEFAULT '0',
  `cycle` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_kpi`
--

LOCK TABLES `custom_kpi` WRITE;
/*!40000 ALTER TABLE `custom_kpi` DISABLE KEYS */;
INSERT INTO `custom_kpi` VALUES (1,'Прибыль до уплаты процентов, налогов и начисленной амортизации','','ebidta','Доход – Расходы (без процентов и налогов) + Амортизация','',0,0,0,0),(2,'Доля рынка','','ms','','',2,1,2,3);
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_linked_kpi_to_goal`
--

LOCK TABLES `custom_linked_kpi_to_goal` WRITE;
/*!40000 ALTER TABLE `custom_linked_kpi_to_goal` DISABLE KEYS */;
INSERT INTO `custom_linked_kpi_to_goal` VALUES (1,'g3','ms'),(2,'g1','ebidta');
/*!40000 ALTER TABLE `custom_linked_kpi_to_goal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_code` varchar(10) DEFAULT NULL,
  `linked_goal_code` varchar(10) DEFAULT NULL,
  `name` varchar(256) DEFAULT NULL,
  `description` text,
  `plan_result` text,
  `fact_result` text,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `responsible` int(11) DEFAULT NULL,
  `actors` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,'b7aced','g1','Делаем  все возможное','Надо длелать раз и два.','Сделали раз -два.\r\n                    \r\n                    ','','2015-11-14 00:00:00','2015-11-26 00:00:00',2,'1');
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fact_value`
--

DROP TABLE IF EXISTS `fact_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fact_value` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kpi_code` varchar(10) DEFAULT NULL,
  `metric_code` varchar(10) DEFAULT NULL,
  `fact_value` float DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fact_value`
--

LOCK TABLES `fact_value` WRITE;
/*!40000 ALTER TABLE `fact_value` DISABLE KEYS */;
/*!40000 ALTER TABLE `fact_value` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kpi_target_values`
--

DROP TABLE IF EXISTS `kpi_target_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kpi_target_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kpi_code` varchar(10) DEFAULT NULL,
  `first_value` float DEFAULT NULL,
  `second_value` float DEFAULT NULL,
  `kpi_scale_type` int(11) DEFAULT NULL,
  `data_source` varchar(255) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kpi_target_values`
--

LOCK TABLES `kpi_target_values` WRITE;
/*!40000 ALTER TABLE `kpi_target_values` DISABLE KEYS */;
INSERT INTO `kpi_target_values` VALUES (1,'ms',100,200,1,'1С8.3',0,'2015-11-12 18:33:14');
/*!40000 ALTER TABLE `kpi_target_values` ENABLE KEYS */;
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
  `measure` int(11) DEFAULT '0',
  `target_responsible` int(11) DEFAULT '0',
  `fact_responsible` int(11) DEFAULT '0',
  `cycle` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lib_kpi`
--

LOCK TABLES `lib_kpi` WRITE;
/*!40000 ALTER TABLE `lib_kpi` DISABLE KEYS */;
INSERT INTO `lib_kpi` VALUES (1,'eva','Экономическая добавленная стоимость','Прирост капитализации.','(NP / IC – WACC) * IC = (ROI – WACC) * IC','http://finanalis.ru/litra/324/2293.html',0,0,0,0),(2,'wacc','Средневзвешенная цена капитала','(Собственный капитал / Инвестированный капитал) * Ожидаемая доходность от собственного капитала + (Заемные средства / Инвестированный капитал) * Ожидаемая доходность от заёмных средств * (1 – Ставка налога на прибыль для компании)','(Собственный капитал / Инвестированный капитал) * Ожидаемая доходность от собственного капитала + (Заемные средства / Инвестированный капитал) * Ожидаемая доходность от заёмных средств * (1 – Ставка налога на прибыль для компании)',NULL,0,0,0,0),(3,'gp','Валовая прибыль','Валовая прибыль = выручка от продаж – (себестоимость проданной продукции т.е. переменные издержки + прямые издержки на продажу продукции)','Выручка – Себестоимость с учетом амортизации',NULL,0,0,0,0),(4,'oi','Операционная прибыль','Операционная прибыль = валовая прибыль – (постоянные издержки + непрямые издержки). ','Выручка – Себестоимость – Постоянные и непрямые издержки',NULL,0,0,0,0),(5,'ebidta','Прибыль до уплаты процентов, налогов и начисленной амортизации','','Доход – Расходы (без процентов и налогов) + Амортизация',NULL,0,0,0,0),(6,'np','Чистая прибыль','Чистая прибыль = прибыль до налогообложения — налог на прибыль. Доход с учетом всех произведенных затрат. МСФО: валовая прибыль – издержки – проценты к уплате ','Валовая прибыль + Прочая операционная прибыль + Прибыль от финансовых операций – Налоги',NULL,0,0,0,0),(7,'ms','Доля рынка','','',NULL,0,0,0,0);
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `org_structure`
--

LOCK TABLES `org_structure` WRITE;
/*!40000 ALTER TABLE `org_structure` DISABLE KEYS */;
INSERT INTO `org_structure` VALUES (3,0,'Director',1),(5,3,'Операционный отдел',2),(6,3,'Маркетинг',2),(7,3,'Производство',2),(9,5,'Логистика',2),(10,6,'PR',1),(11,5,'Уборщики',2);
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
INSERT INTO `strategic_maps` VALUES (1,'ent0','g1','','','',0,'2015-11-12 16:40:19'),(2,'ent0','g3','','','',0,'2015-11-12 16:40:24'),(3,'ent0','','ebidta','','',0,'2015-11-12 16:40:35'),(4,'ent0','','ms','','',0,'2015-11-12 16:40:36'),(5,'ent0','','','','b7aced',0,'2015-11-14 23:53:39');
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
  `owner` int(11) DEFAULT '0',
  `status` int(11) DEFAULT '0',
  `date` datetime DEFAULT NULL,
  `department` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategic_maps_desc`
--

LOCK TABLES `strategic_maps_desc` WRITE;
/*!40000 ALTER TABLE `strategic_maps_desc` DISABLE KEYS */;
INSERT INTO `strategic_maps_desc` VALUES (1,'ent0','Стратегическая карта компании','Стратегическая карта компании верхнего уровня.',0,0,'2015-11-07 00:52:39',0),(5,'dep7','Стратегическая карта: Производство','',2,0,'2015-11-18 18:23:58',7),(6,'dep9','Стратегическая карта: Логистика','',2,0,'2015-11-18 18:24:20',9);
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
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `text_messages`
--

LOCK TABLES `text_messages` WRITE;
/*!40000 ALTER TABLE `text_messages` DISABLE KEYS */;
INSERT INTO `text_messages` VALUES (1,'step1_full_description','<p>Выберите отрасль в которой работает компания.</p>\n<p>Выбор влияет на формирование списков перспектив, целей, подцелей, показателей и мероприятий.\n</p>','Первая страница мастера. Полное описание.'),(2,'step1_name','Отрасль работы компании.','Первый шаг мастера'),(3,'step2_full_description','<p>\nДерево отражающее организационную структуру компании, в которое можно добавлять подчиненные единицы.\n</p>\n<p>\nКаждая ветка означает организационную единицу. </p>\n<p>\nПереход на следующий шаг, после составления структуры. Должна быть создана хотя бы одна организационная единица. \n</p>','Второй шаг мастера'),(4,'step2_name','Оганизационная структура компании.','Второй шаг мастера'),(5,'step3_full_description','<p>Выбрать из списка целей наиболее подходящие для компании.</p>\n<p>Сразу во время выбора, предлагаются цели которые связаны с выбранными.</p>','Третья страница мастера. Полное описание.'),(6,'step3_name','Формирование стратегической карты компании.','Третий шаг мастера'),(7,'step3_stage1_description','<p>Добавьте цели которые вам подходят. Поставьте галочки и нажмите \"Добавить\" </p>','Добавление новых целей и показателей.'),(8,'step3_subheader','<p>\nдля выбранных целей существуют связанные цели. Рекомендуем добавить их в стратегическую карту\n</p>',''),(9,'step3_stage3_description','<p>Для каждой цели подобраны показатели по которым можно измерять прогресс. </p> <p> Вы можете не использовать их, для этого снимите галочки напротив.</p>',''),(10,'step3_stage3_subheader','Добавьте к целям показатели',NULL),(11,'step5_name','Выбор целевых значений',NULL),(12,'step5_full_description','<p>Для каждого показателя необходимо определить:  ответственного за достижение целевого значения, единицу измерения, периодичность сбора данных, шкалу оценки целевого значения.</p>\n<p>\nШкала оценки может быть выбрана из пяти разных видов.\n</p>\n',NULL),(13,'step5_subheader','',NULL),(14,'step6_full_description','<p>Действия по достижению целей описываются в формате мероприятий.</p>\n<p>Это действия надо выполнить, чтобы цели были достигнуты.</p>\n<p>Для каждой цели в стратегической карте выбирается набор мероприятий из списка или добавляются новые. </p>\n<p>Каждое мероприятие может быть связано с одной целью.</p>\n<p>Цель может быть связана с несколькими мероприятиями, если необходима последоватьельность действий.</p>',NULL),(15,'step6_name','План достижения целей',NULL),(16,'step6_subheader','Мероприятия',NULL),(17,'step7_full_description','<p>Выберите подразделения компании для которых необходимо составить счетные/стратегические карты</p>\n<p>Если карта подразделения уже создана, она будет доступна для просмотра. </p>',NULL),(18,'step7_name','Счетные/стратегические карты подразделений',NULL),(19,'step7_subheader','Подразделения',NULL);
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

-- Dump completed on 2015-11-18 18:38:41
