USE `bmtools`;
ALTER TABLE `bmtools`.`wizard_configuration` ADD COLUMN `object_code` VARCHAR(10) NULL AFTER `cur_step`;
