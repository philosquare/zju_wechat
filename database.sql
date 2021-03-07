create database wechat_tem default character set utf8mb4 collate utf8mb4_unicode_ci;

use wechat_tem;

CREATE TABLE `user_account` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `is_followed` tinyint(4) DEFAULT NULL,
  `openid` varchar(255) DEFAULT NULL,
  `tem_username` varchar(255) DEFAULT NULL,
  `tem_password` varchar(255) DEFAULT NULL,
  `account_verified` tinyint(4) DEFAULT NULL,
  `account_update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
