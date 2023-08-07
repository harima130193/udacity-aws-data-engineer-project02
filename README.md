# UDACITY AWS DATA ENGINEERING PORJECT 02
## 1. ETL pipeline
Contain python code for:
- Copy data from s3 to staging table in redshift
- Transform data from staging table and load to fact and dimesion table
### 1.1 Purpose of database and data pipeline
- OLAP database is used to extract fact information from log event(level, location, UserAgent, SessionId) with dimesion(user, song, artist, time).
- Data pipeline extract from log event and song data to load to Star Schema database.
### 1.2 Dicuss about database schema design and ETL pipeline
 With the requirement that create star schema for song analysis, I create 4 dimension table with those primary key: user_dim(user_id), song_dim(song_id), artist_dim(artist_id), time_dim(start_time) and a fact table songplay_fact(songplay_id), because user can play diffrent song at the same start time so I use songplay_id(a auto increment integer) as a primary key. About time_dim table, current design use to record start time of song play, but only required to hourly granularity, that make the repeated at columns in time_dim table, for below example:

| start_time              | hour | day | week | month | year | weekday |
|:-----------------------:|:----:|:---:|:----:|:-----:|:----:|:-------:|
| 2018-11-01 21:02:12.000 | 21   | 1   | 44   | 11    | 2018 | 4       |
| 2018-11-01 21:08:16.000 | 21   | 1   | 44   | 11    | 2018 | 4       |
| 2018-11-01 21:17:33.000 | 21   | 1   | 44   | 11    | 2018 | 4       |
| 2018-11-01 21:24:53.000 | 21   | 1   | 44   | 11    | 2018 | 4       |
---
I think we can use calendar table with hourly granularity to replace timestamps of records in songplays is better. Because of project  requirement, I still keep use time_dim as timestamps of records in songplays.<br>
About ETL pipeline, I use COPY command to load data from s3 to staging table. For loading data to dimension and fact table, I load data to songplay_fact by left join staging_song and staging_event on song title, artist name and song length; Because A event can have song title, artist name and song length not in staging_song list, then I choose left join.For dimension table, time_dim and user_dim is load from staging_event; song_dim and artist_dim is load from staging_song and eliminate record that do not have primary key.
## 2. Infrastructure
IoC terrform for create redshift cluster
## 3. How to use
### 3.1 Infrastructure
- Go to `infrastructure` folder
- Fill `rs_master_username`, `rs_master_pass`, `my_ip_address_cidr` in `terraform.tfvars` is required.
- Run terraform apply to run and get redshift credentials from output
- Run ```terrform destroy``` to remove infrastructure after finish
### 3.2 ETL Pipeline code
- Install poetry
- Go to folder `etl-pipeline`
- Run ```poetry env info``` to detect virtualenv, and run command poetry shell to create virtualenv if your don't have one.
- Use virtualenv by run command: ```poetry env use <python version>```
- Fill information to `dwh.cfg`
- Run poetry install to install dependencies
- Go to etl-pipeline folder
- Run command ```python create_table.py``` for create tables
- Run command ```python elt.py``` for running the ETL pipeline
