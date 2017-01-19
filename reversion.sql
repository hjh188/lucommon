BEGIN;
CREATE TABLE `reversion_revision` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `manager_slug` varchar(200) NOT NULL, `date_created` datetime NOT NULL, `comment` longtext NOT NULL, `user_id` integer NULL);
CREATE TABLE `reversion_version` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `object_id` longtext NOT NULL, `object_id_int` integer NULL, `format` varchar(255) NOT NULL, `serialized_data` longtext NOT NULL, `object_repr` longtext NOT NULL, `content_type_id` integer NOT NULL, `revision_id` integer NOT NULL);
ALTER TABLE `reversion_revision` ADD CONSTRAINT `reversion_revision_user_id_53d027e45b2ec55e_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `reversion_revision_b16b0f06` ON `reversion_revision` (`manager_slug`);
CREATE INDEX `reversion_revision_c69e55a4` ON `reversion_revision` (`date_created`);
ALTER TABLE `reversion_version` ADD CONSTRAINT `revers_content_type_id_c01a11926d4c4a9_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
ALTER TABLE `reversion_version` ADD CONSTRAINT `reversion_v_revision_id_48ec3744916a950_fk_reversion_revision_id` FOREIGN KEY (`revision_id`) REFERENCES `reversion_revision` (`id`);
CREATE INDEX `reversion_version_0c9ba3a3` ON `reversion_version` (`object_id_int`);

COMMIT;
