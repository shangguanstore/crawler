

DROP TABLE IF EXISTS `jobs`;
CREATE TABLE `jobs` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `jobid` int(11) NOT NULL DEFAULT 0 COMMENT '职位id',
  `title` varchar(255) NOT NULL DEFAULT '' COMMENT '职位名称',
  `salary_low` int(11) NOT NULL COMMENT '最低薪资',
  `salary_high` int(11) NOT NULL COMMENT '最高薪资',
  `salary_avg` int(11) NOT NULL COMMENT '平均薪资',
  `source_url` varchar(255) NOT NULL DEFAULT '' COMMENT '抓取地址',
  `href` varchar(255) NOT NULL DEFAULT '' COMMENT '访问地址',
  `tags` varchar(255) NOT NULL DEFAULT '' COMMENT '职位标签',
  `des` varchar(255) NOT NULL DEFAULT '' COMMENT '职位描述',
  `stars` tinyint(1) NOT NULL DEFAULT 0 COMMENT '标记状态，星级越高，价值越高  0 默认 1 一星  2 二星  3 三星  4 四星  5 五星',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态  1 正常  -1 删除',
  `company` varchar(255) NOT NULL DEFAULT '' COMMENT '公司名称',
  `from_plat` varchar(255) NOT NULL DEFAULT '' COMMENT '数据来源',
  `comment` varchar(250) DEFAULT '' COMMENT '备注',
  `publishTime` int(10) NOT NULL DEFAULT '0' COMMENT '发布时间',
  `create_time` int(10) NOT NULL DEFAULT '0' COMMENT '添加时间',
  `update_time` int(10) NOT NULL DEFAULT '0' COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8 COMMENT='职位表';