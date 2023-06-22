CREATE TABLE `logtable` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `UserId` int(11) DEFAULT NULL COMMENT 'Номер пользователя',
  `LocalName` varchar(255) DEFAULT NULL COMMENT 'Имя компьютера',
  `SessionId` varchar(20) DEFAULT NULL COMMENT 'Уникальный номер пакета',
  `LineNum` int(11) DEFAULT NULL COMMENT 'Номер строки',
  `Component` varchar(255) DEFAULT NULL COMMENT 'Название компонента',
  `Querytext` mediumtext DEFAULT NULL COMMENT 'Текст запроса',
  `Datetimesave` datetime DEFAULT NULL COMMENT 'Датавремя сохранения',
  PRIMARY KEY (`Id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
