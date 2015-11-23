USE `bmtools`;
ALTER TABLE `bmtools`.`wizard_configuration` ADD COLUMN `object_code` VARCHAR(10) NULL AFTER `cur_step`;

ALTER TABLE `bmtools`.`lib_goals`
ADD COLUMN `type` INT(11) NOT NULL DEFAULT 0 AFTER `perspective`,
ADD COLUMN `edit` INT(11) NOT NULL DEFAULT 0 AFTER `type`;

ALTER TABLE `bmtools`.`custom_goals`
ADD COLUMN `type` INT(11) NOT NULL DEFAULT 0 AFTER `perspective`,
ADD COLUMN `edit` INT(11) NOT NULL DEFAULT 0 AFTER `type`;