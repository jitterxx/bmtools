CREATE DATABASE  IF NOT EXISTS `bmtools` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `bmtools`;
-- MySQL dump 10.13  Distrib 5.5.46, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: bmtools
-- ------------------------------------------------------
-- Server version	5.5.44-0ubuntu0.14.04.1

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
  `type` int(11) NOT NULL DEFAULT '0',
  `edit` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_goals`
--

LOCK TABLES `custom_goals` WRITE;
/*!40000 ALTER TABLE `custom_goals` DISABLE KEYS */;
INSERT INTO `custom_goals` VALUES (1,'g1','Увеличение выручки','В условиях рыночной экономики значение прибыли огромно. Стремление к ее получению ориентирует товаропроизводителей на увеличение объема производства продукции, нужной потребителю, снижение затрат на производство.',0,0,0),(2,'g3','Рост доли рынка','Объемы первичных продаж компании  (данные о собственных продажах) не могут дать точной информации для понимания того, что реально производит с компанией и ее брендами на рынке. Данные о продажах могут расти, но на рынках, которые растут более быстрыми темп',1,0,0),(3,'g2','Снижение дебиторской задолженности','Дебиторская задолженность - задолженность организаций и физических лиц данной организации (например, задолженность покупателей за приобретенный товар или оказанные услуги, задолженность подотчетных лиц за выданные им денежные суммы) Соответственно, организ',0,0,0),(11,'dg0a4d','Цель для подразделения 1','session.add(link)',1,1,1),(13,'hg66gf','Связанная цель для цели подразделения 1','исходящей и входящей точки соответствующих блоков. Прорисовка стрелок происходит на холсте (canvas) расположенном над общим родителем. ',2,1,1),(14,'dg7c44','Рост дохода от абонентской платы','',0,0,0),(15,'dge813','Рост дохода от аб. платы','',0,0,0),(16,'dg3463','Увеличение выручки от абонентской платы','',0,0,0),(17,'dg3ab2','Увеличение выручки от технического обслуживания','',0,0,0),(18,'dg4ce9','Увеличение выручки от продажи оборудования','',0,0,0),(19,'dg7cd3','Стабилизация расходов','',0,0,0),(20,'dg5703','Рост абонентской базы','',0,0,0),(21,'dgc9a2','Рост абонентской базы','',1,0,0),(22,'dg9fdb','Рост партнерской сети (страховщиков)','',0,0,0),(23,'dg80e4','Рост партнерской сети (страховщики)','',1,0,0),(24,'dg1f44','Рост партнерской сети (установщики)','',1,0,0),(25,'dg2f2c','Развитие продаж через лизинговые компании','',1,0,0),(26,'dg4acb','Развитие продаж через интернет','',1,0,0),(27,'dg08db','Рост среднего чека через продажи доп. услуг','',0,0,0),(28,'dg23b0','Рост среднего чека через продажи доп. услуг','',1,0,0),(29,'dg3ee7','Рост среднего чека через продажи доп. услуг','',1,0,0),(30,'dg4a64','Рост среднего чека через продаж доп. услуг','',1,0,0),(31,'dgb154','Расширение перечня оборудования','',2,0,0),(32,'dg4fd6','Сокращение сроков постановки на обслуживание ','',2,0,0),(33,'dgce95','Вознаграждение агентов через НПС','',2,0,0),(34,'dg02e4','Построение системы продаж Мониторинга','',0,0,0),(35,'dg448b','Построение системы продаж Мониторинга','',2,0,0),(36,'dg4f4c','Создание процесса \"Вызов на ТО\"','',2,0,0),(37,'dgf9c1','Сделать прозрачным процесс сбора ДЗ ','',2,0,0),(38,'dg48c7','Наити человека для работы с установочными центрами','',3,0,0),(39,'dgbf2e','Прием на работу сотрудника для работы с установочными центрами','',0,0,0),(40,'dg462d','Прием на работу человека для работы с установочными центрами','',3,0,0),(41,'dg56a7','Оптимизация процесса сбора ДЗ (ЛК + упрощение)','',2,0,0),(42,'dg9d4b','Оптимизация бизнес-процессов','постановка на обслуживание\r\nуправление сим картами\r\nсбор дебиторе автоматизация, уведомления клиентам, личный кабинет\r\nэлектронный документооборот\r\nзаявления от клиентов в электронном виде\r\nСокращение сроков постановки на обслуживание ',2,0,0),(43,'dgf52d','Вознаграждение агентов через НПС','',2,0,0),(44,'dgc59b','Повышение надежности защиты автомобиля','',1,0,0),(45,'dg21cd','Создание процесса \"Вызов на регламентное и не регламентное ТО\"','',2,0,0),(46,'dg164f','Прием на работу человека для работы с установочными центрами','',3,0,0),(47,'dg8f33','Постановка учета затрат','',2,0,0),(48,'dg5129','Рост лояльности клиентов','',1,0,0);
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
  `data_source` varchar(256) DEFAULT NULL,
  `kpi_scale_type` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_kpi`
--

LOCK TABLES `custom_kpi` WRITE;
/*!40000 ALTER TABLE `custom_kpi` DISABLE KEYS */;
INSERT INTO `custom_kpi` VALUES (1,'Прибыль до уплаты процентов, налогов и начисленной амортизации','','ebidta','Доход – Расходы (без процентов и налогов) + Амортизация','',0,0,0,0,NULL,0),(2,'Доля рынка','','ms','','',2,1,2,3,NULL,0),(3,'Показатель для подразделения 1','Создан самостоятельно','5fg045','not defined','',0,0,0,0,NULL,0),(6,'Экономическая добавленная стоимость','Прирост капитализации.','eva','(NP / IC – WACC) * IC = (ROI – WACC) * IC','http://finanalis.ru/litra/324/2293.html',0,0,0,0,NULL,0),(7,'Средневзвешенная цена капитала','(Собственный капитал / Инвестированный капитал) * Ожидаемая доходность от собственного капитала + (Заемные средства / Инвестированный капитал) * Ожидаемая доходность от заёмных средств * (1 – Ставка налога на прибыль для компании)','wacc','(Собственный капитал / Инвестированный капитал) * Ожидаемая доходность от собственного капитала + (Заемные средства / Инвестированный капитал) * Ожидаемая доходность от заёмных средств * (1 – Ставка налога на прибыль для компании)','',0,0,0,0,NULL,0),(8,'Сумма затрат','','kp2f13','','',2,3,1,0,'1С',0),(9,'Сумма выручки','','kp50f5','Сумма выручки БП + Сумма выручки М + Сумма выручки Закладки','',2,0,0,0,'1С',0),(10,'Сумма выручки от абонентской платы','','kpe5f4','','',2,0,0,0,'',0),(11,'Сумма выручки от продажи оборудования','','kp5214','','',2,0,0,0,'',0),(12,'Сумма выручки от технического обслуживания','','kpffdc','','',2,0,0,0,'1С',0),(13,'Сумма затрат','','kp8c06','','',2,0,0,0,'1С',0),(14,'Количество новых ТС БП','','kpb924','','',0,0,0,0,'Ежемесячный расчет ОРК',0),(15,'Количество новых ТС Мониторинг','','kpbcda','','',0,0,0,0,'Ежемесячный отчет ОРК',0),(16,'Количество новых ТС Закладки','','kp7231','','',0,0,0,0,'Ежемесячный отчет ОРК',0),(17,'Общее количество ТС БП','','kpae9f','','',0,0,0,0,'',0),(18,'Общее количество ТС Мониторинг','','kpad69','','',0,0,0,0,'Ежемесячный отчет ОРК',0),(19,'Общее количество ТС Закладки','','kp0bf4','','',0,0,0,0,'',0),(20,'Количество отключившихся по всем причинам, кроме продажи ТС (БП + Мониторинг)','','kp09b9','','',0,0,0,0,'',0),(21,'Доля надежно предотвращенных угонов','','kpd679','','',1,0,0,0,'',0),(22,'Доля успешных возвратов угнанных ТС','','kp5107','','',1,0,0,0,'',0),(23,'Количество ТС, переведенных на более безопасный тариф','','kp2d88','','',0,0,0,0,'',0),(24,'Количество агенств, которые работают с Легионом','','kp1cec','','',0,0,0,0,'Отчет по партнерам',0),(25,'Доля агентов, которые начали работать с Легионом','','kp3d57','','',1,0,0,0,'Отчет по партнерам',0),(26,'Доля агентов, которые начали работать с Легионом','','kp920c','Кол-во агентов, которые начали работать / Количество агентов, которые получили информацию','',0,0,0,0,'Отчет по партнерам',0),(27,'Количество клиентов, которых привели установщики','','kp33bb','','',0,0,0,0,'Отчет по партнерам',0),(28,'Количество ТС, подключенных через лизинговые компании','','kpf47f','','',0,0,0,0,'Отче по партнерам',0),(29,'Количество ТС, подключенных через интернет','','kp4e21','','',0,0,0,0,'',0),(30,'Сумма выручки от продаж дополнительного оборудования','','kp8fb9','','',0,0,0,0,'',0);
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
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_linked_goals`
--

LOCK TABLES `custom_linked_goals` WRITE;
/*!40000 ALTER TABLE `custom_linked_goals` DISABLE KEYS */;
INSERT INTO `custom_linked_goals` VALUES (1,'g1','g3'),(2,'g3','g1'),(3,'g3','g2'),(4,'g2','g3'),(9,'dg0a4d','g3'),(10,'g3','dg0a4d'),(11,'dg0a4d','g2'),(12,'g2','dg0a4d'),(13,'hg66gf','dg0a4d'),(14,'dg0a4d','hg66gf'),(15,'dg7c44','g1'),(16,'g1','dg7c44'),(17,'dge813','g1'),(18,'g1','dge813'),(19,'dg3463','g1'),(20,'g1','dg3463'),(21,'dg3ab2','g1'),(22,'g1','dg3ab2'),(23,'dg4ce9','g1'),(24,'g1','dg4ce9'),(29,'dgc9a2','dg3463'),(30,'dg3463','dgc9a2'),(31,'dg9fdb','dgc9a2'),(32,'dgc9a2','dg9fdb'),(33,'dg80e4','dgc9a2'),(34,'dgc9a2','dg80e4'),(35,'dg1f44','dgc9a2'),(36,'dgc9a2','dg1f44'),(37,'dg2f2c','dgc9a2'),(38,'dgc9a2','dg2f2c'),(39,'dg4acb','dgc9a2'),(40,'dgc9a2','dg4acb'),(41,'dg08db','dgc9a2'),(42,'dgc9a2','dg08db'),(43,'dg23b0','dgc9a2'),(44,'dgc9a2','dg23b0'),(47,'dg4a64','dg3463'),(48,'dg3463','dg4a64'),(49,'dgb154','dg4ce9'),(50,'dg4ce9','dgb154'),(53,'dgc9a2','dg3ab2'),(54,'dg3ab2','dgc9a2'),(55,'dgc9a2','dg4ce9'),(56,'dg4ce9','dgc9a2'),(57,'dg9d4b','dg7cd3'),(58,'dg7cd3','dg9d4b'),(59,'dgf52d','dg1f44'),(60,'dg1f44','dgf52d'),(61,'dgc59b','dg7cd3'),(62,'dg7cd3','dgc59b'),(63,'dgc59b','g1'),(64,'g1','dgc59b'),(65,'dg21cd','dgc59b'),(66,'dgc59b','dg21cd'),(67,'dg164f','dg1f44'),(68,'dg1f44','dg164f'),(69,'dg8f33','dg7cd3'),(70,'dg7cd3','dg8f33'),(71,'dg5129','dg3463'),(72,'dg3463','dg5129');
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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_linked_kpi_to_goal`
--

LOCK TABLES `custom_linked_kpi_to_goal` WRITE;
/*!40000 ALTER TABLE `custom_linked_kpi_to_goal` DISABLE KEYS */;
INSERT INTO `custom_linked_kpi_to_goal` VALUES (1,'g3','ms'),(2,'g1','ebidta'),(3,'dg0a4d','5fg045'),(4,'g1','eva'),(5,'g1','wacc'),(6,'dg7cd3','kp2f13'),(7,'g1','kp50f5'),(8,'dg3463','kpe5f4'),(9,'dg4ce9','kp5214'),(10,'dg3ab2','kpffdc'),(11,'dg7cd3','kp8c06'),(12,'dgc9a2','kpb924'),(13,'dgc9a2','kpbcda'),(14,'dgc9a2','kp7231'),(15,'dgc9a2','kpae9f'),(16,'dgc9a2','kpad69'),(17,'dgc9a2','kp0bf4'),(18,'dg5129','kp09b9'),(19,'dgc59b','kpd679'),(20,'dgc59b','kp5107'),(21,'dgc59b','kp2d88'),(22,'dg80e4','kp1cec'),(23,'dg7cd3','kp3d57'),(24,'dg80e4','kp920c'),(25,'dg1f44','kp33bb'),(26,'dg2f2c','kpf47f'),(27,'dg4acb','kp4e21'),(28,'dg4a64','kp8fb9');
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,'b7aced','g1','Делаем  все возможное','Надо длелать раз и два.','Сделали раз -два.\r\n                    \r\n                    ','','2015-11-14 00:00:00','2015-11-26 00:00:00',2,'1'),(2,'b550bc','dg0a4d','Мероприятие для цели подразделения 1','цваца','цсмфвсфывсфс\r\nывмцымывмывм\r\nывмыфвмывмым\r\n                    \r\n                    ','','2015-11-27 00:00:00','2015-11-29 00:00:00',1,'3,4'),(3,'883b88','g3','Удали меня','ывмы','ым','','2015-11-27 00:00:00','2015-11-29 00:00:00',4,'3');
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
  `version` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `period_code` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kpi_target_values`
--

LOCK TABLES `kpi_target_values` WRITE;
/*!40000 ALTER TABLE `kpi_target_values` DISABLE KEYS */;
INSERT INTO `kpi_target_values` VALUES (1,'ms',100,200,0,'2015-11-12 18:33:14',NULL),(2,'kp2f13',0,0,0,'2016-01-01 00:00:00',1),(3,'kp50f5',1800000,0,0,'2016-01-01 00:00:00',1),(4,'kp50f5',1800000,0,0,'2016-02-01 00:00:00',2),(5,'kp50f5',1800000,0,0,'2016-03-01 00:00:00',3),(6,'kpe5f4',1000000,0,0,'2016-01-01 00:00:00',1),(7,'kpe5f4',1000000,0,0,'2016-02-01 00:00:00',2),(8,'kpe5f4',1000000,0,0,'2016-03-01 00:00:00',3),(9,'kp5214',600000,0,0,'2016-01-01 00:00:00',1),(10,'kp5214',600000,0,0,'2016-02-01 00:00:00',2),(11,'kp5214',600000,0,0,'2016-03-01 00:00:00',3),(12,'kpffdc',200000,0,0,'2016-01-01 00:00:00',1),(13,'kpffdc',200000,0,0,'2016-02-01 00:00:00',2),(14,'kpffdc',200000,0,0,'2016-03-01 00:00:00',3),(15,'kp8c06',0,0,0,'2016-01-01 00:00:00',1),(16,'kp8c06',0,0,0,'2016-02-01 00:00:00',2),(17,'kp8c06',0,0,0,'2016-03-01 00:00:00',3),(18,'kpb924',10,0,0,'2016-01-01 00:00:00',1),(19,'kpb924',5,0,0,'2016-02-01 00:00:00',2),(20,'kpb924',7,0,0,'2016-03-01 00:00:00',3),(21,'kpbcda',5,0,0,'2016-01-01 00:00:00',1),(22,'kpbcda',0,0,0,'2016-02-01 00:00:00',2),(23,'kpbcda',0,0,0,'2016-03-01 00:00:00',3),(24,'kp7231',25,0,0,'2016-01-01 00:00:00',1),(25,'kp7231',15,0,0,'2016-02-01 00:00:00',2),(26,'kp7231',20,0,0,'2016-03-01 00:00:00',3),(27,'kpae9f',0,0,0,'2016-01-01 00:00:00',1),(28,'kpae9f',0,0,0,'2016-02-01 00:00:00',2),(29,'kpae9f',0,0,0,'2016-03-01 00:00:00',3),(30,'kpad69',0,0,0,'2016-01-01 00:00:00',1),(31,'kpad69',0,0,0,'2016-02-01 00:00:00',2),(32,'kpad69',0,0,0,'2016-03-01 00:00:00',3),(33,'kp0bf4',0,0,0,'2016-01-01 00:00:00',1),(34,'kp0bf4',0,0,0,'2016-02-01 00:00:00',2),(35,'kp0bf4',0,0,0,'2016-03-01 00:00:00',3),(36,'kp09b9',0,0,0,'2016-01-01 00:00:00',1),(37,'kp09b9',0,0,0,'2016-02-01 00:00:00',2),(38,'kp09b9',0,0,0,'2016-03-01 00:00:00',3),(39,'kpd679',100,0,0,'2016-01-01 00:00:00',1),(40,'kpd679',100,0,0,'2016-02-01 00:00:00',2),(41,'kpd679',100,0,0,'2016-03-01 00:00:00',3),(42,'kp5107',0,0,0,'2016-01-01 00:00:00',1),(43,'kp5107',0,0,0,'2016-02-01 00:00:00',2),(44,'kp5107',0,0,0,'2016-03-01 00:00:00',3),(45,'kp2d88',0,0,0,'2016-01-01 00:00:00',1),(46,'kp2d88',0,0,0,'2016-02-01 00:00:00',2),(47,'kp2d88',0,0,0,'2016-03-01 00:00:00',3),(48,'kp1cec',0,0,0,'2016-01-01 00:00:00',1),(49,'kp1cec',0,0,0,'2016-02-01 00:00:00',2),(50,'kp1cec',0,0,0,'2016-03-01 00:00:00',3),(51,'kp3d57',0,0,0,'2016-01-01 00:00:00',1),(52,'kp3d57',0,0,0,'2016-02-01 00:00:00',2),(53,'kp3d57',0,0,0,'2016-03-01 00:00:00',3),(54,'kp920c',0,0,0,'2016-01-01 00:00:00',1),(55,'kp920c',0,0,0,'2016-02-01 00:00:00',2),(56,'kp920c',0,0,0,'2016-03-01 00:00:00',3),(57,'kp33bb',0,0,0,'2016-01-01 00:00:00',1),(58,'kp33bb',0,0,0,'2016-02-01 00:00:00',2),(59,'kp33bb',0,0,0,'2016-03-01 00:00:00',3),(60,'kpf47f',0,0,0,'2016-01-01 00:00:00',1),(61,'kpf47f',0,0,0,'2016-02-01 00:00:00',2),(62,'kpf47f',0,0,0,'2016-03-01 00:00:00',3),(63,'kp4e21',0,0,0,'2016-01-01 00:00:00',1),(64,'kp4e21',0,0,0,'2016-02-01 00:00:00',2),(65,'kp4e21',0,0,0,'2016-03-01 00:00:00',3);
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
  `type` int(11) NOT NULL DEFAULT '0',
  `edit` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lib_goals`
--

LOCK TABLES `lib_goals` WRITE;
/*!40000 ALTER TABLE `lib_goals` DISABLE KEYS */;
INSERT INTO `lib_goals` VALUES (1,'g1','Увеличение прибыли','В условиях рыночной экономики значение прибыли огромно. Стремление к ее получению ориентирует товаропроизводителей на увеличение объема производства продукции, нужной потребителю, снижение затрат на производство.',0,0,0),(2,'g2','Снижение дебиторской задолженности','Дебиторская задолженность - задолженность организаций и физических лиц данной организации (например, задолженность покупателей за приобретенный товар или оказанные услуги, задолженность подотчетных лиц за выданные им денежные суммы) Соответственно, организ',0,0,0),(3,'g3','Рост доли рынка','Объемы первичных продаж компании  (данные о собственных продажах) не могут дать точной информации для понимания того, что реально производит с компанией и ее брендами на рынке. Данные о продажах могут расти, но на рынках, которые растут более быстрыми темп',1,0,0);
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
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategic_maps`
--

LOCK TABLES `strategic_maps` WRITE;
/*!40000 ALTER TABLE `strategic_maps` DISABLE KEYS */;
INSERT INTO `strategic_maps` VALUES (1,'ent0','g1','','','',0,'2015-11-12 16:40:19'),(4,'ent0','','ms','','',0,'2015-11-12 16:40:36'),(5,'ent0','','','','b7aced',0,'2015-11-14 23:53:39'),(34,'dep7','g3','','','',0,'2015-11-25 19:07:11'),(35,'dep7','','ms','','',0,'2015-11-25 19:07:11'),(37,'dep7','dg0a4d','','','',0,'2015-11-25 19:49:35'),(39,'dep7','g1','','','',0,'2015-11-26 17:35:44'),(40,'dep7','','ebidta','','',0,'2015-11-26 18:49:04'),(41,'dep7','','eva','','',0,'2015-11-26 18:50:23'),(43,'dep7','','wacc','','',0,'2015-11-26 18:54:27'),(44,'dep7','','5fg045','','',0,'2015-11-26 18:54:27'),(45,'dep7','','','','b550bc',0,'2015-11-26 19:31:10'),(46,'dep7','','','','883b88',0,'2015-11-26 19:34:21'),(49,'ent0','dg3463','','','',0,'2015-11-29 23:32:21'),(50,'ent0','dg3ab2','','','',0,'2015-11-29 23:32:52'),(51,'ent0','dg4ce9','','','',0,'2015-11-29 23:33:47'),(52,'ent0','dg7cd3','','','',0,'2015-11-29 23:34:26'),(54,'ent0','dgc9a2','','','',0,'2015-11-29 23:36:38'),(56,'ent0','dg80e4','','','',0,'2015-11-29 23:39:28'),(57,'ent0','dg1f44','','','',0,'2015-11-29 23:40:49'),(58,'ent0','dg2f2c','','','',0,'2015-11-29 23:41:41'),(59,'ent0','dg4acb','','','',0,'2015-11-29 23:43:32'),(63,'ent0','dg4a64','','','',0,'2015-11-29 23:48:20'),(64,'ent0','dgb154','','','',0,'2015-11-29 23:50:31'),(75,'ent0','dg9d4b','','','',0,'2015-12-01 13:52:33'),(76,'ent0','dgf52d','','','',0,'2015-12-01 13:58:25'),(77,'ent0','dgc59b','','','',0,'2015-12-01 14:12:39'),(78,'ent0','dg21cd','','','',0,'2015-12-01 14:13:33'),(79,'ent0','dg164f','','','',0,'2015-12-01 14:16:29'),(80,'ent0','dg8f33','','','',0,'2015-12-04 11:41:02'),(82,'ent0','','kp50f5','','',0,'2015-12-05 10:20:06'),(83,'ent0','','kpe5f4','','',0,'2015-12-05 10:23:33'),(84,'ent0','','kp5214','','',0,'2015-12-05 10:48:14'),(85,'ent0','','kpffdc','','',0,'2015-12-05 10:50:46'),(86,'ent0','','kp8c06','','',0,'2015-12-05 10:52:16'),(87,'ent0','','kpb924','','',0,'2015-12-05 10:54:06'),(88,'ent0','','kpbcda','','',0,'2015-12-05 10:55:33'),(89,'ent0','','kp7231','','',0,'2015-12-05 10:57:25'),(90,'ent0','','kpae9f','','',0,'2015-12-05 10:59:10'),(91,'ent0','','kpad69','','',0,'2015-12-05 10:59:50'),(92,'ent0','','kp0bf4','','',0,'2015-12-05 11:00:21'),(93,'ent0','dg5129','','','',0,'2015-12-05 11:03:33'),(94,'ent0','','kp09b9','','',0,'2015-12-05 11:07:38'),(95,'ent0','','kpd679','','',0,'2015-12-05 11:09:00'),(96,'ent0','','kp5107','','',0,'2015-12-05 11:10:49'),(97,'ent0','','kp2d88','','',0,'2015-12-05 11:11:29'),(98,'ent0','','kp1cec','','',0,'2015-12-05 11:12:27'),(99,'ent0','','kp3d57','','',0,'2015-12-05 11:13:50'),(100,'ent0','','kp920c','','',0,'2015-12-05 11:15:22'),(101,'ent0','','kp33bb','','',0,'2015-12-05 11:16:11'),(102,'ent0','','kpf47f','','',0,'2015-12-05 11:17:06'),(103,'ent0','','kp4e21','','',0,'2015-12-05 11:17:56'),(104,'ent0','','kp8fb9','','',0,'2015-12-05 11:18:56');
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
  `draw_data` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategic_maps_desc`
--

LOCK TABLES `strategic_maps_desc` WRITE;
/*!40000 ALTER TABLE `strategic_maps_desc` DISABLE KEYS */;
INSERT INTO `strategic_maps_desc` VALUES (1,'ent0','Стратегическая карта компании','Стратегическая карта компании верхнего уровня.',0,0,'2015-11-07 00:52:39',0,'{\"g3\":{\"left\":52,\"top\":137},\"g1\":{\"left\":144,\"top\":26},\"dg3ab2\":{\"left\":257,\"top\":124},\"dg4ce9\":{\"left\":575,\"top\":31},\"dg3463\":{\"left\":414,\"top\":83},\"dg7cd3\":{\"left\":34,\"top\":122},\"dg2f2c\":{\"left\":263,\"top\":222},\"dg80e4\":{\"left\":224,\"top\":323},\"dg1f44\":{\"left\":362,\"top\":322},\"dgc9a2\":{\"left\":411,\"top\":212},\"dg4acb\":{\"left\":501,\"top\":329},\"dgce95\":{\"left\":78,\"top\":477},\"dg56a7\":{\"left\":232,\"top\":481},\"dg448b\":{\"left\":375,\"top\":478},\"dg4a64\":{\"left\":546,\"top\":256},\"dg4f4c\":{\"left\":342,\"top\":475},\"dg462d\":{\"left\":71,\"top\":651},\"dg4fd6\":{\"left\":670,\"top\":471},\"dgb154\":{\"left\":645,\"top\":518},\"dg9d4b\":{\"left\":18,\"top\":529},\"dgf52d\":{\"left\":278,\"top\":437},\"dgc59b\":{\"left\":123,\"top\":211},\"dg21cd\":{\"left\":187,\"top\":516},\"dg164f\":{\"left\":365,\"top\":629},\"dg8f33\":{\"left\":90,\"top\":455},\"dg5129\":{\"left\":681,\"top\":208}}'),(5,'dep7','Стратегическая карта: Производство','',2,0,'2015-11-18 18:23:58',7,'{\"g3\":{\"left\":59,\"top\":150},\"dg0a4d\":{\"left\":213,\"top\":158},\"g1\":{\"left\":68,\"top\":28}}'),(6,'dep9','Стратегическая карта: Логистика','',2,0,'2015-11-18 18:24:20',9,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `text_messages`
--

LOCK TABLES `text_messages` WRITE;
/*!40000 ALTER TABLE `text_messages` DISABLE KEYS */;
INSERT INTO `text_messages` VALUES (1,'step1_full_description','<p>Выберите отрасль в которой работает компания.</p>\n<p>Выбор влияет на формирование списков перспектив, целей, подцелей, показателей и мероприятий.\n</p>','Первая страница мастера. Полное описание.'),(2,'step1_name','Отрасль работы компании.','Первый шаг мастера'),(3,'step2_full_description','<p>\nДерево отражающее организационную структуру компании, в которое можно добавлять подчиненные единицы.\n</p>\n<p>\nКаждая ветка означает организационную единицу. </p>\n<p>\nПереход на следующий шаг, после составления структуры. Должна быть создана хотя бы одна организационная единица. \n</p>','Второй шаг мастера'),(4,'step2_name','Оганизационная структура компании.','Второй шаг мастера'),(5,'step3_full_description','<p>Выбрать из списка целей наиболее подходящие для компании.</p>\n<p>Сразу во время выбора, предлагаются цели которые связаны с выбранными.</p>','Третья страница мастера. Полное описание.'),(6,'step3_name','Формирование стратегической карты компании.','Третий шаг мастера'),(7,'step3_stage1_description','<p>Добавьте цели которые вам подходят. Поставьте галочки и нажмите \"Добавить\" </p>','Добавление новых целей и показателей.'),(8,'step3_subheader','<p>\nдля выбранных целей существуют связанные цели. Рекомендуем добавить их в стратегическую карту\n</p>',''),(9,'step3_stage3_description','<p>Для каждой цели подобраны показатели по которым можно измерять прогресс. </p> <p> Вы можете не использовать их, для этого снимите галочки напротив.</p>',''),(10,'step3_stage3_subheader','Добавьте к целям показатели',NULL),(11,'step5_name','Выбор целевых значений',NULL),(12,'step5_full_description','<p>Для каждого показателя необходимо определить:  ответственного за достижение целевого значения, единицу измерения, периодичность сбора данных, шкалу оценки целевого значения.</p>\n<p>\nШкала оценки может быть выбрана из пяти разных видов.\n</p>\n',NULL),(13,'step5_subheader','',NULL),(14,'step6_full_description','<p>Действия по достижению целей описываются в формате мероприятий.</p>\n<p>Это действия надо выполнить, чтобы цели были достигнуты.</p>\n<p>Для каждой цели в стратегической карте выбирается набор мероприятий из списка или добавляются новые. </p>\n<p>Каждое мероприятие может быть связано с одной целью.</p>\n<p>Цель может быть связана с несколькими мероприятиями, если необходима последоватьельность действий.</p>',NULL),(15,'step6_name','План достижения целей',NULL),(16,'step6_subheader','Мероприятия',NULL),(17,'step7_full_description','<p>Выберите подразделения компании для которых необходимо составить счетные/стратегические карты</p>\n<p>Если карта подразделения уже создана, она будет доступна для просмотра. </p>',NULL),(18,'step7_name','Счетные/стратегические карты подразделений',NULL),(19,'step7_subheader','Подразделения',NULL),(20,'depwiz_start_full_description','<p>Выберите карту подразделения для работы.</p>',NULL),(21,'depwiz_start_name','Доступные карты подразделений',NULL),(22,'depwiz_step1_full_description','<p>Добавить цели из Стратегической карты компании.</p>\n<p>Добавить собственые цели и связать их.</p>\n<p>Добавить KPI для целей.</p>\n<p>Настроить KPI, указать целевые значения.</p>\n<p>Добавить мероприятия.</p>',NULL),(23,'depwiz_step1_name','Шаг 1. Мастер по настройке карты департамента',NULL),(24,'depwiz_step2_full_description','<p>Чтобы добавить цели и показатель нажмите на соответствущие кнопки.</p>\n<p>Вместе с выбранными целями в карту подразделения будут добавлены их показатели.</p>\n',NULL),(25,'depwiz_step2_name','Шаг 2. Добавьте цели из стратегичекой карты.',NULL),(26,'depwiz_step2new_full_description','<p>Добавьте в карту подразделения дополнительные цели, которые не вошли в карту компании.</p>\n<p>Вы можете связать их между собой и обозначить взаимное влияние.</p>\n<p></p>',NULL),(27,'depwiz_step2new_name','Добавьте новую цель в карту подразделения',NULL),(28,'depwiz_step3_full_description','Добавьте показатели',NULL),(29,'depwiz_step3_name','Добавьте показатели в карту подразделения',NULL),(30,'depwiz_step3new_full_description','<p>Введите данные нового показателя.</p>\n<p>Вы сможете привязать его только к целям подразделения.</p>',NULL),(31,'depwiz_step3new_name','Добавить новый показатель',NULL),(32,'depwiz_step4_full_description','desc',NULL),(33,'depwiz_step4_name','name',NULL),(34,'depwiz_step4_subheader','subheader',NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'e0408fae-7c97-11e5-b5f1-f46d04d35cbd','Иван','Шишкин','sergey','Cthutq123','users,admin',0),(2,'e0408fae-7c97-11e5-b5f1-f46d04d38866','Лев','Толстой','test','Qazcde123','users,admin',0);
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
  `object_code` varchar(10) DEFAULT NULL,
  `status` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wizard_configuration`
--

LOCK TABLES `wizard_configuration` WRITE;
/*!40000 ALTER TABLE `wizard_configuration` DISABLE KEYS */;
INSERT INTO `wizard_configuration` VALUES (4,'1','step7','ent0','new');
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

-- Dump completed on 2015-12-05 22:22:35
