//创建数据库sc
create database sc;

//使用数据库sc
use sc;

//创建切尔西后卫补强表
drop table if exists cs_d;
create table cs_d(
    name string comment "球员名",
    psr double comment "传球成功率",
    skyW int comment "挣顶成功次数",
    intercept int comment "拦截",
    wealth int comment "身价（万）"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/CS.csv' into table cs_d;

select *from cs_d;

//创建阿森纳中锋补强表
drop table if exists a_s;
create table a_s(
    name string comment "球员名",
    goals int comment "进球",
    pat int comment "禁区触球次数",
    gcr double comment "进球转化率",
    wealth int comment "身价（万）"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/AS.csv' into table a_s;

select *from a_s;

//创建曼城中场补强表
drop table if exists mc;
create table mc(
    name string comment "球员名",
    steal int comment "抢断次数",
    keyPass int comment "关键传球次数",
    assist int comment "助攻次数",
    wealth int comment "身价（万）"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/MC.csv' into table mc;

select *from mc;

//创建切尔西门将补强表
drop table if exists cs_g;
create table cs_g(
    name string comment "球员名",
    rsr double comment "扑救成功率",
    pisR double comment "传中拦截成功率",
    psr double comment "传球成功率",
    wealth int comment "身价（万）"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/CSG.csv' into table cs_g;

select *from cs_g;

//创建球员能力值表
drop table if exists player_ab;
create table player_ab(
    name string comment "球员名",
    ovr int comment "综合",
    pac int comment "速度",
    sho int comment "射门",
    pas int comment "传球",
    dri int comment "盘带",
    def int comment "防守",
    phy int comment "力量"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/playerAb.csv' into table player_ab;

select *from player_ab;

//创建门将能力值表
drop table if exists goalkeeper_ab;
create table goalkeeper_ab(
    name string comment "球员名",
    ovr int comment "综合",
    `div` int comment "扑救",
    han int comment "手型",
    kic int comment "开球",
    ref int comment "反应",
    spd int comment "速度",
    pos int comment "位置"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/gkAb.csv' into table goalkeeper_ab;

select *from goalkeeper_ab;

//创建英超现阶段排名和胜负表
drop table if exists premier_league_stats;
create table premier_league_stats(
    rank int comment "排名",
    squad string comment "俱乐部",
    win int comment "赢的场次",
    draw int comment "平局场次",
    lose int comment "输的场次"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/cleaned_premier_league_stats.csv' into table premier_league_stats;

select *from premier_league_stats;


//创建英超各球队数据表
drop table if exists squadData;
create table squadData(
    squad string comment "俱乐部",
    goals int comment "进球数",
    shoot int comment "射门次数",
    gcr double comment "进球转化率",
    keyPass int comment "关键传球次数",
    loseGoals int comment "失球数"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/SquadInfo.CSV' into table squadData;

select *from squadData;


//进行雷达图数据格式转换-怀森，用mapreduce创建新表速度太慢了，可以换spark，我这里是直接下载csv文件重导
SELECT
  name AS player_name,
  ability_type,
  ability_value
FROM player_ab
LATERAL VIEW EXPLODE(
  MAP(
    '综合', ovr,
    '速度', pac,
    '射门', sho,
    '传球', pas,
    '盘带', dri,
    '防守', def,
    '力量', phy
  )
) t AS ability_type, ability_value
WHERE ability_value IS NOT NULL and name='怀森';

//创建怀森能力值表
drop table if exists HS_ab;
create table HS_ab(
    player_name string comment "球员名",
    ability_type string comment "能力值类型",
    ability_value int comment "能力值"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/Hive_0_HS.csv' into table HS_ab;

select *from HS_ab;

SELECT
  name AS player_name,
  ability_type,
  ability_value
FROM player_ab
LATERAL VIEW EXPLODE(
  MAP(
    '综合', ovr,
    '速度', pac,
    '射门', sho,
    '传球', pas,
    '盘带', dri,
    '防守', def,
    '力量', phy
  )
) t AS ability_type, ability_value
WHERE ability_value IS NOT NULL and name='孔德';

//创建孔德能力值表
drop table if exists KD_ab;
create table KD_ab(
    player_name string comment "球员名",
    ability_type string comment "能力值类型",
    ability_value int comment "能力值"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/Hive_0_KD.csv' into table KD_ab;

select *from KD_ab;

SELECT
  name AS player_name,
  ability_type,
  ability_value
FROM player_ab
LATERAL VIEW EXPLODE(
  MAP(
    '综合', ovr,
    '速度', pac,
    '射门', sho,
    '传球', pas,
    '盘带', dri,
    '防守', def,
    '力量', phy
  )
) t AS ability_type, ability_value
WHERE ability_value IS NOT NULL and name='哲凯赖什';

//创建哲凯赖什能力值表
drop table if exists ZKLS_ab;
create table ZKLS_ab(
    player_name string comment "球员名",
    ability_type string comment "能力值类型",
    ability_value int comment "能力值"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/Hive_0_ZKLS.csv' into table ZKLS_ab;

select *from ZKLS_ab;

SELECT
  name AS player_name,
  ability_type,
  ability_value
FROM player_ab
LATERAL VIEW EXPLODE(
  MAP(
    '综合', ovr,
    '速度', pac,
    '射门', sho,
    '传球', pas,
    '盘带', dri,
    '防守', def,
    '力量', phy
  )
) t AS ability_type, ability_value
WHERE ability_value IS NOT NULL and name='伊萨克';

//创建伊萨克能力值表
drop table if exists YSK_ab;
create table YSK_ab(
    player_name string comment "球员名",
    ability_type string comment "能力值类型",
    ability_value int comment "能力值"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/Hive_0_YSK.csv' into table YSK_ab;

select *from YSK_ab;

SELECT
  name AS player_name,
  ability_type,
  ability_value
FROM player_ab
LATERAL VIEW EXPLODE(
  MAP(
    '综合', ovr,
    '速度', pac,
    '射门', sho,
    '传球', pas,
    '盘带', dri,
    '防守', def,
    '力量', phy
  )
) t AS ability_type, ability_value
WHERE ability_value IS NOT NULL and name='吉马良斯';

//创建吉马良斯能力值表
drop table if exists JMLS_ab;
create table JMLS_ab(
    player_name string comment "球员名",
    ability_type string comment "能力值类型",
    ability_value int comment "能力值"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/Hive_0_JMLS.csv' into table JMLS_ab;

select *from JMLS_ab;

SELECT
  name AS player_name,
  ability_type,
  ability_value
FROM player_ab
LATERAL VIEW EXPLODE(
  MAP(
    '综合', ovr,
    '速度', pac,
    '射门', sho,
    '传球', pas,
    '盘带', dri,
    '防守', def,
    '力量', phy
  )
) t AS ability_type, ability_value
WHERE ability_value IS NOT NULL and name='维尔茨';

//创建维尔茨能力值表
drop table if exists WEC_ab;
create table WEC_ab(
    player_name string comment "球员名",
    ability_type string comment "能力值类型",
    ability_value int comment "能力值"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/Hive_0_WEC.csv' into table WEC_ab;

select *from WEC_ab;

SELECT
  name AS goalkeeper_name,
  ability_type,
  ability_value
FROM goalkeeper_ab
LATERAL VIEW EXPLODE(
  MAP(
    '综合', ovr,
    '扑救', `div`,
    '手型', han,
    '开球', kic,
    '反应', ref,
    '速度', spd,
    '位置', pos
  )
) t AS ability_type, ability_value
WHERE ability_value IS NOT NULL and name='凯莱赫';

//创建凯莱赫能力值表
drop table if exists KLH_ab;
create table KLH_ab(
    goalkeeper_name string comment "球员名",
    ability_type string comment "能力值类型",
    ability_value int comment "能力值"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/Hive_0_KLH.csv' into table KLH_ab;

select *from KLH_ab;


SELECT
  name AS goalkeeper_name,
  ability_type,
  ability_value
FROM goalkeeper_ab
LATERAL VIEW EXPLODE(
  MAP(
    '综合', ovr,
    '扑救', `div`,
    '手型', han,
    '开球', kic,
    '反应', ref,
    '速度', spd,
    '位置', pos
  )
) t AS ability_type, ability_value
WHERE ability_value IS NOT NULL and name='科贝尔';

//创建科贝尔能力值表
drop table if exists KBE_ab;
create table KBE_ab(
    goalkeeper_name string comment "球员名",
    ability_type string comment "能力值类型",
    ability_value int comment "能力值"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/Hive_0_KBE.csv' into table KBE_ab;

select *from KBE_ab;

//创建前6球队中场平均年纪数据表
drop table if exists Age_Cm;
create table Age_Cm(
    club_name string comment "球队名",
    age int comment "年龄"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/cm_compare.csv' into table Age_Cm;

select *from Age_Cm;

//创建球队后防失误数据表
drop table if exists Err_CS;
create table Err_CS(
    club_name string comment "球队名",
    err int comment "致命失误次数"
)
row format delimited fields terminated by ',';

load data local inpath '/root/hivedata/err.csv' into table Err_CS;

select *from Err_CS;

CREATE TABLE football_players (
  player_name STRING comment '球员',
  club_name STRING comment '俱乐部',
  age INT comment '年龄',
  position STRING comment '位置',
  matches_played STRING comment '出场', -- 建议拆分为单独字段
  minutes_played INT comment '上场时间',
  goals INT comment '进球',
  assists INT comment '助攻',
  yellow_cards INT comment '黄牌',
  red_cards INT comment '红牌',
  pass_success_rate DOUBLE comment '传球成功率',
  chances_created INT comment '创造机会',
  headers_won INT comment '争顶成功',
  rating DOUBLE comment '评分',
  market_value DOUBLE comment '身价（万）'
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar" = "\"",
  "escapeChar" = "\\"
)
STORED AS TEXTFILE;

//加载数据
LOAD DATA LOCAL INPATH '/root/hivedata/web.csv' OVERWRITE INTO TABLE football_players;

SELECT * FROM football_players LIMIT 5;

SELECT player_name, rating FROM football_players WHERE regexp_replace(rating, '[0-9.]', '') <> '';

 SELECT player_name, rating FROM football_players WHERE rating NOT RLIKE '^[0-9.]+$';