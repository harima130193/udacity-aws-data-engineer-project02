import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay_fact"
user_table_drop = "DROP TABLE IF EXISTS user_dim"
song_table_drop = "DROP TABLE IF EXISTS song_dim"
artist_table_drop = "DROP TABLE IF EXISTS artist_dim"
time_table_drop = "DROP TABLE IF EXISTS time_dim"


# CREATE TABLES

staging_events_table_create= (
"""
CREATE TABLE staging_events(
	artist varchar,
    auth varchar,
    firstName varchar,
    gender char(1),
    itemInSession int,
    lastName varchar,
    length decimal(12,5),
    level varchar,
    location varchar,
    method varchar,
    page varchar,
    registration bigint,
    sessionId int,
    song varchar,
    status int,
    ts bigint,
    userAgent varchar,
    userId int
)
"""
)

staging_songs_table_create = (
"""
CREATE TABLE staging_songs(                              
num_songs int,
artist_id varchar,
artist_latitude decimal(8,5),
artist_longitude decimal(8,5),
artist_location varchar,
artist_name varchar,
song_id varchar,
title varchar,
duration decimal(12,5),
year int                       
)                              
""")

songplay_table_create = (
"""
CREATE TABLE songplay_fact(
songplay_id int IDENTITY(0,1),
start_time timestamp,
user_id int,
level varchar,
song_id varchar,
artist_id varchar,
session_id int,
location varchar,
user_agent varchar,
PRIMARY KEY(songplay_id),
FOREIGN KEY(user_id) REFERENCES user_dim(user_id),
FOREIGN KEY(song_id) REFERENCES song_dim(song_id),
FOREIGN KEY(artist_id) REFERENCES artist_dim(artist_id),
FOREIGN KEY(start_time) REFERENCES time_dim(start_time)
)
""")

user_table_create = (
"""
CREATE TABLE user_dim(
user_id int,
first_name varchar,
last_name varchar,
gender char(1),
level varchar,
PRIMARY KEY(user_id)
)
""")

song_table_create = (
"""
CREATE TABLE song_dim(
song_id varchar, 
title varchar,
artist_id varchar,
year int,
duration decimal(12,5),
PRIMARY KEY(song_id),
FOREIGN KEY(artist_id) REFERENCES artist_dim(artist_id)
)
""")

artist_table_create = (
"""
CREATE TABLE artist_dim(
artist_id varchar,
name varchar,
location varchar,
latitude decimal(8,5),
longitude decimal(8,5),
PRIMARY KEY(artist_id)
)
""")

time_table_create = (
"""
CREATE TABLE time_dim(
start_time timestamp,
hour int,
day int,
week int,
month int,
year int,
weekday int,
PRIMARY KEY(start_time)
)
""")

# STAGING TABLES

staging_events_copy = (
f"""
COPY staging_events FROM '{config["S3"]["LOG_DATA"]}' IAM_ROLE '{config["IAM_ROLE"]["ARN"]}' FORMAT AS JSON '{config["S3"]["LOG_JSONPATH"]}'
""").format()

staging_songs_copy = (
f"""
COPY staging_songs FROM '{config["S3"]["SONG_DATA"]}' IAM_ROLE '{config["IAM_ROLE"]["ARN"]}' FORMAT AS JSON 'auto ignorecase'
""").format()

# FINAL TABLES

songplay_table_insert = ("""
insert into songplay_fact(start_time,user_id,level,song_id,artist_id,session_id,location,user_agent)
select 
	(TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 Second ')as start_time,
	se.userid  as user_id,
	se.level  as level,
	ss.song_id as song_id,
	ss.artist_id as artist_id,
	se.sessionId as session_id,
	se.location as location,
	se.userAgent as user_agent
from staging_events se
left join staging_songs ss
on 
    ss.song_id is not null 
	and 
	ss.artist_id is not null 
	and
    se.artist = ss.artist_name 
	and 
	se.song = ss.title 
	and 
	se.length = ss.duration
where se.page = 'NextSong'
""")

user_table_insert = ("""
insert into user_dim 
select distinct 
    se.userid as user_id,
    se.firstname as first_name ,
    se.lastname as last_name ,
    se.gender as gender ,
    se.level as level
from staging_events se
where userid is not null
""")

song_table_insert = ("""
insert into song_dim 
select 
	ss.song_id as song_id,
	ss.title as title ,
	ss.artist_id as artist_id ,
	ss.year as year ,
	ss.duration as duration 
from staging_songs ss
where song_id is not null
""")

artist_table_insert = ("""
insert into artist_dim  
select distinct
    ss.artist_id as artist_id ,
    ss.artist_name as name ,
    ss.artist_location as location,
    ss.artist_latitude as latitude ,
    ss.artist_longitude as longitude
from staging_songs ss 
where artist_id is not null
""")

time_table_insert = ("""
insert into time_dim  
select distinct
    (TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 Second ')as start_time,
    extract(hour from start_time) as "hour",
    extract(day from start_time) as "day",
    extract(week from start_time) as "week",
    extract(month from start_time) as "month",
    extract(year from start_time) as "year",
    extract(weekday from start_time) as "weekday" from staging_events se
where ts is not null
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create,artist_table_create, song_table_create,time_table_create,songplay_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert,user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
