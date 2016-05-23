import sys
import os
import datetime
import psycopg2
import pandas
from subprocess import call, Popen

conn_string = "dbname='hamlethurricane' user=postgres port='5432' host='127.0.0.1' password='password'"

os.system("exit")
os.system("exit")

print "Connecting to database..."

try:
	conn = psycopg2.connect(conn_string)
except Exception as e:
	print str(e)
	sys.exit()

print "Connected!\n"

hurricane_name = 'ARTHUR'

dataframe_cur = conn.cursor()

dataframe_sql = """Select * from hurricane_{}""".format(hurricane_name)

dataframe_cur.execute(dataframe_sql)

data = dataframe_cur.fetchall()

colnames = [desc[0] for desc in dataframe_cur.description]

dataframe = pandas.DataFrame(data)

dataframe.columns = colnames

conn.commit()

range_feat =  range(len(dataframe)-1)

range_feat_strp = str(range_feat).strip('[]')

range_feat_strp_v2 = range_feat_strp.split(',')
print range_feat_strp_v2

drop_if_sql = """drop table if exists hurricane_{}_parcels, exposed_parcels""".format(hurricane_name)

drop_if_cur = conn.cursor()

drop_if_cur.execute(drop_if_sql)

creation_cur = conn.cursor()

creation_sql = """create table hurricane_{}_parcels as 
				  select  * from dare_4326""".format(hurricane_name,hurricane_name)

creation_cur.execute(creation_sql)

conn.commit()

add_cur = conn.cursor()

add_sql = """alter table hurricane_{}_parcels
			 add column andrew_impact character varying(50),
			 add column iso_time character varying (19)
			 """.format(hurricane_name)

add_cur.execute(add_sql)

conn.commit()

buffer_cur = conn.cursor() 


intersect_cur = conn.cursor()

for key in range(1,len(dataframe)-1):
	
	sql = """create or replace view vw_parcels_impact_{} as
	select a.nparno, b.iso_time, b.ogc_fid, a.geom as geom 
	from dare_4326 as a 
	inner join vw_rmw_{} as b 
	on st_intersects(b.geom,a.geom)
	group by a.nparno, b.iso_time, b.ogc_fid, a.geom;""".format(key, key)

	print sql 

	intersect_cur.execute(sql)
	conn.commit()


update_cur = conn.cursor() 

for key in range(1, len(dataframe)-1):
	
  	sql = """update hurricane_{}_parcels as a
  	set iso_time = b.iso_time 
  	from vw_parcels_impact_{} as b
 	where a.nparno = b.nparno""".format(hurricane_name, key) 

 	print sql 

 	update_cur.execute(sql)
 	conn.commit()


exposed_cur = conn.cursor()
	
exposed_sql = """create table exposed_parcels as 
  				select  * from hurricane_{}_parcels where iso_time is not null""".format(hurricane_name, hurricane_name) 

exposed_cur.execute(exposed_sql)

exposed_cur = conn.cursor()

conn.commit()