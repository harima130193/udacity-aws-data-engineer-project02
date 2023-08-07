import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
    load data to staging tables by copy_table_queries 
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
    insert data to dimension tables and a fact table by insert_table_queries
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
    Get redshift credentials, redshfit role arn and s3 information from dwh.cfg
    Connect to redshift cluster with for loading data to staging tables and insert data to dimension and fact tables
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()