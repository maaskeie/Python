# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 11:05:56 2019

@author: 5240
"""

import pandas as pd
import geopandas as gpd
from pandas import DataFrame
from geopandas import GeoDataFrame
from datetime import datetime
from datetime import timedelta
import psycopg2 as pg
import psycopg2.extras
from shapely.geometry import Point
from functions import get_lengdegruppe
import numpy as np

class DataBase(object):
    
    def __init__(self, start_date, end_date, area=None, filepath=None):
        
        self.start_date = start_date        
        start_str = start_date.split('-')   #Splitter string ved bindestreker
        self.start_year = int(start_str[0])
        self.start_month = int(start_str[1])
        self.start_day = int(start_str[2])
        
        self.end_date = end_date
        end_str = end_date.split('-')       #Splitter string ved bindestreker
        self.end_year = int(end_str[0])
        self.end_month = int(end_str[1])
        self.end_day = int(end_str[2])
    
        self.date_start = datetime(self.start_year, self.start_month, self.start_day)
        self.date_end = datetime(self.end_year, self.end_month, self.end_day)
        
        self.date_diff = self.date_end - self.date_start   #dato-string
        self.day_diff = (self.date_diff.days)        #Typecast antall dager til integer
        
        self.num_months = abs((self.end_month - self.start_month)+1) #Antallet måneder i perioden som skal leses av'
        
        #Ble nødvendig når jeg bruker timestamp to str fra andre funksjoner
        if ' ' in self.start_date or ' ' in self.end_date:
            start_date_str = start_date.split(' ')
            start_date = start_date_str[0]
            
            end_date_str = end_date.split(' ')
            end_date = end_date_str[0]
        else:
            pass
        
        if area==None:
            print('Norge innenfor NØS initiert')                
            self.area=None
        
        elif type(area) == tuple:
            print('Tuple initiert')
            self.area = area
            self.bottom_left = str(area[0])+','+ str(area[1])
            self.bottom_right = str(area[2])+', '+ str(area[1])
            self.top_left = str(area[0])+', '+ str(area[3])
            self.top_right = str(area[2])+', '+ str(area[3])
            self.geom_string = '[' + self.bottom_left + '],[' + self.bottom_right + '],[' + self.top_left + '],[' + self.top_right + ']'

        elif area.geom_type == 'Polygon':
            print('Polygon initiert')
            self.area = area
            tmp_list = list(self.area.exterior.coords)
            self.geom_string = '['
            for point in tmp_list:
                tmp_point = str(point)
                tmp_point = tmp_point[1:-1]
                tmp_point = tmp_point.replace(" ", "")
                self.geom_string += tmp_point
                self.geom_string += '],['
            self.geom_string = self.geom_string[:-2]       
        
        else:
            print('Omraadet er ikke av typen tuple, bruk bounding_boks for å få ut koordinater eller lag din egen av typen lat/lon, EPSG:4326, [xmin,ymin,xmax,ymax]')
        
                
        self.filepath = filepath       
        
    
    def ais_raw_punkter(self, statcode5=str(), time=None):
        
        if time == None:
            time = 60
        else:
            time = time
        
        if len(statcode5)<1:
            statcode_statement = ''
        else:
            statcode_statement = " WHERE statcode5_fp in " + statcode5 + " "
        
        if self.area == None:
            aoi_statement = ''
        else:
            aoi_statement = ' AND ST_Within(geom,st_setsrid(ST_GeomFromGeoJSON(\'{"type": "Polygon","coordinates": [['+self.geom_string+']]}\'),4326))'
        
        
        host_adress = ''
        db = ''
        username =''
        dbkey = ''
        
        if self.start_year == 2020:
            host_adress = '153.44.0.220'
            db = 'ais2020'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB10
            
        if self.start_year == 2019:
            host_adress = '153.44.0.220'
            db = 'ais2019'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB10
            
        elif self.start_year == 2018:
            host_adress = '153.44.0.225'
            db = 'ais2018'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB09
            
        elif self.start_year == 2017:
            host_adress = '153.44.0.194'
            db = 'ais2017'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB08            
            
        elif self.start_year == 2016:
            host_adress = '153.44.0.185'
            db = 'ais2016'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB07
            
        elif self.start_year == 2015:
            host_adress = '153.44.1.129'
            db = 'ais2015'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB01
            
        elif self.start_year == 2014:
            host_adress = '153.44.0.172'
            db = 'ais2014'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB02
            
        elif self.start_year == 2013:
            host_adress = '153.44.0.173'
            db = 'ais2013'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB03
            
        elif self.start_year == 2012:
            host_adress = '153.44.0.174'
            db = 'ais2012'
            username = 'postgres'
            dbkey = 'postgres'
            #GeoAISDB03
            
        else:
            print('Error, sjekk datoformat, og format på areavariabel om benyttet')
        
        login = [host_adress, db, username, dbkey]
                
        distinct_statement = "DISTINCT ON(mmsi, to_timestamp(floor((extract('epoch' from date_time_utc) / "+str(time)+" )) * "+str(time)+") at time zone 'UTC') "
               
        table_coloumns = """
        table_data.mmsi,
        CAST(table_reg.imo_num_fp as text) imo,
        table_reg.name_ais as vessel_name,
        table_reg.callsign_ais as callsign,        
        table_data.date_time_utc,                
        table_reg.statcode5_fp,        
        table_data.message_nr,
        table_data.sog,
        table_data.true_heading,
        table_data.geom  
        """
#Sjekk db for mulige kolonner, bare husk siste føring er uten komma
        
        select_statement= "SELECT " + distinct_statement + table_coloumns
        
        order_by_statement= " ORDER BY mmsi, to_timestamp(floor((extract('epoch' from date_time_utc) / "+str(time)+" )) * "+str(time)+") at time zone 'UTC'"
        
        #Timestamper start av script for tidtagning av prosess:
        ScriptStart = datetime.now()
        
        #lagringsliste for appending av dagsiterasjoner
        rows = []
        
        #Iterasjonsløkke for dagstabeller:
        for i in range(1,(self.day_diff+2),1):
            #Timestamper starten av hver tabellbehandling
            tabell_start = datetime.now()
            
            #Tellevariabel for hvilken dag som det omhandler
            day_adder = i - 1
            
            #Adderer antall dager siden den første
            if self.day_diff == 1:
                calDate = self.date_start
            else:
                calDate = self.date_start + timedelta(day_adder)
                
            #Generer navn til schema.database for bruk til kobling mot aisdatabase
            table = 'ais'+calDate.strftime('%Y%m')+'.ais_'+calDate.strftime('%Y%m%d')
            
            #string som skrives til konsoll for hver dag som
            print('\nLeser inn dag '+str(i)+'.\n')
            print('Beregner dag: '+str(calDate)+'\n')
            print('Tabell: '+str(table)+'\n')         
            
            from_statement = ' FROM '+table+' table_data'
            reg_table = table+'_unique_info table_reg'
            inner_join_statement = ' INNER JOIN '+reg_table+' ON table_data.mmsi = table_reg.mmsi'
            sql_syntax = select_statement + from_statement + inner_join_statement + aoi_statement + statcode_statement + order_by_statement
            
            
            if i == 1:
                #Kjekk til å se hva som kommer ut av sql-syntaxen
                print('\nFølgende SQL syntax er benyttet i spørringen:\n'+sql_syntax+'\n')
            else:
                pass
            
            try:
                connection = psycopg2.connect('host='+str(login[0])+' dbname='+str(login[1])+' user ='+str(login[2])+' password='+str(login[3]))
                print('\nVellykket tilkobling mot databasen for rådata ais\n')
            except: 
                print ('Klarte ikke koble til db. Sjekk tilkoblingsinformasjon som befinner seg i DataBase.ais_raw_punkter()')    
            
            rows.append(gpd.GeoDataFrame.from_postgis(sql_syntax, connection, geom_col='geom', crs={'init': 'epsg:4326'}))
    
            end_tid_tabell = datetime.now()
            total_tid = end_tid_tabell - ScriptStart
            tabell_tid = end_tid_tabell - tabell_start
            
            print('\nFerdig med loop nummer '+str(i)+' av '+str(self.day_diff +1)+'.\n')
            print('Skrevet tabell '+str(table)+'.\n')
            print('Tid brukt på denne tabellen: '+str(tabell_tid)+'\n')
            print('Tid brukt på scriptet så langt: '+str(total_tid)+'\n')
        
        ais_data = gpd.GeoDataFrame(pd.concat(rows, ignore_index=True), crs={'init': 'epsg:4326'}).set_geometry('geom')
        
        try:
            ais_data.imo = pd.to_numeric(ais_data.imo, errors='coerce').fillna(0).astype(np.int64)
        except:
            print('IMO lager')
        
        if self.filepath == None:
            pass
        else:
            ais_data.to_csv(self.filepath, sep=';', index=False, mode='w')
        
        return ais_data    
    
    
    def metadata(self):
            
            host_adress = '153.44.18.151'
            db = 'postgres'
            username ='postgres'
            dbkey = 'postgres'
            login = [host_adress, db, username, dbkey]
            
            try:
                connection = pg.connect('host='+str(login[0])+' dbname='+str(login[1])+' user ='+str(login[2])+' password='+str(login[3]))
                print('\nTilkobling mot database postgres på SØA-server lyktes\n')
            except:
                print('\nTilkobling mot db mislyktes\n')

            table_name = "ais_data.populasjon_"+str(self.start_year)            
            
            select_statement = "SELECT CAST(mmsi as int), CAST(imo as text), vessel_name, callsign, statcode5, CAST(skipstype as int), skipstype_label, CAST(draught as text), CAST(gt as text), CAST(length as text), CAST(width as text), CAST(depth as text), passengercapacity as paxcap "
            from_statement = "FROM "+table_name
            
            sql_syntax = select_statement + from_statement
            
            print('\nHenter metadata fra populasjon_'+str(self.start_year)+'...\n')
            print('Benytter Følgende SQL-Syntax: '+sql_syntax+'\n')
            
            cursor = connection.cursor()
            cursor.execute(sql_syntax)
            
            metadata = DataFrame(cursor.fetchall(), columns=['mmsi', 'imo', 'vessel_name', 'callsign', 'statcode5', 'skipstype', 'skipstype_label', 'draught', 'gt', 'length', 'depth', 'width', 'paxcap'])
            cursor.close()
            metadata['length'] = metadata['length'].str.replace(',', '.')
            metadata['width'] = metadata['width'].str.replace(',', '.')
            metadata['gt'] = metadata['gt'].str.replace(',', '.')
            metadata['depth'] = metadata['depth'].str.replace(',', '.')
            metadata['draught'] = metadata['draught'].str.replace(',', '.')
            
            metadata = metadata.assign(lengdegruppe = lambda df: df['length'].map(get_lengdegruppe))
            
            return metadata
        
    
    def havne_polygoner(self):
        
        host_adress = '153.44.18.151'
        db = 'postgres'
        username ='postgres'
        dbkey = 'postgres'
        login = [host_adress, db, username, dbkey]
        
        try:
            connection = pg.connect('host='+str(login[0])+' dbname='+str(login[1])+' user ='+str(login[2])+' password='+str(login[3]))
            print('\nKobling mot postgres database på SØA-server var en suksess\n')
        except:
            print('Tilkobling mislyktes\n')
        
        schema = 'public.'
        table_name = 'havne_polygoner'
        
        table_coloumns ="location_name, uuid, type, google_address, street, source, offshore_name, offshore_kind, offshore_facilityfunctions, offshore_belongstoname, farm_id, farm_owner, farm_locationnumber, farm_locationname, geom "
        select_statement = "SELECT " + table_coloumns
        
        from_statement = "FROM " + schema + table_name
        
        sql_syntax = select_statement + from_statement
        print(sql_syntax)
        
        print('\nHenter havnepolygoner fra public.havne_polygoner...\n')
        print('Benytter Følgende SQL-Syntax: '+sql_syntax+'\n')
                
        havnepolygoner = GeoDataFrame.from_postgis(sql_syntax, connection, geom_col='geom')
        
        return havnepolygoner

    def world_ports(self):
        
        host_adress = '153.44.18.151'
        db = 'postgres'
        username ='postgres'
        dbkey = 'postgres'
        login = [host_adress, db, username, dbkey]
        
        try:
            connection = pg.connect('host='+str(login[0])+' dbname='+str(login[1])+' user ='+str(login[2])+' password='+str(login[3]))
            print('\nKobling mot postgres database på SØA-server var en suksess\n')
        except:
            print('Tilkobling mislyktes\n')
        
        schema = 'public.'
        table_name = 'world_ports'
        
        table_coloumns ="""
        id,
        name,
        a3,
        url,
        authority,
        location,
        lat,
        lng,
        zoom,
        wpi,
        size,
        thumb,
        review,
        uri 
        """
        select_statement = "SELECT " + table_coloumns
        
        from_statement = "FROM " + schema + table_name
        
        sql_syntax = select_statement + from_statement
        
        print('\nHenter skipsdata fra World_ports ut fra public.world_ports...\n')
                
        frames = pd.read_sql(sql_syntax, connection)
        point_list = list()
        
        for idx, row in frames.iterrows():
            tmp_lng = float(row['lng'])
            tmp_lat = float(row['lat'])
                        
            tmp_point = Point(tmp_lng, tmp_lat)
            point_list.append(tmp_point)
                
        frames['geometry'] = point_list

        crs={'init':'epsg:4326'}
        
        geoframe = GeoDataFrame(frames, geometry='geometry', crs=crs)
        
        return geoframe
        
    
    def skipskategorier(self):
        
        host_adress = '153.44.18.151'
        db = 'postgres'
        username ='postgres'
        dbkey = 'postgres'
        login = [host_adress, db, username, dbkey]
        
        try:
            connection = pg.connect('host='+str(login[0])+' dbname='+str(login[1])+' user ='+str(login[2])+' password='+str(login[3]))
            print('\nKobling mot postgres database på SØA-server var en suksess\n')
        except:
            print('Tilkobling mislyktes\n')
        
        schema = 'public.'
        table_name = 'skipskategorier'
        
        table_coloumns ="""
        skipstype,
        statcode5,
        skipstype_label
        """
        select_statement = "SELECT " + table_coloumns
        
        from_statement = "FROM " + schema + table_name
        
        sql_syntax = select_statement + from_statement
        
        
        
        print('\nHenter lookup-tabell for skipskategorier\n')
        print('Benytter Følgende SQL-Syntax: \n'+sql_syntax+'\n')
                
        frame = pd.read_sql(sql_syntax, connection)        
        
        return frame
    
    
    def havbase(self, svalbard=False):
        
        host_adress = '153.44.0.168'
        db = 'sandbox_johan'
        username ='kyv_admin'
        dbkey = 'fuckup=003'
        login = [host_adress, db, username, dbkey]
        
        try:
            connection = pg.connect('host='+str(login[0])+' dbname='+str(login[1])+' user ='+str(login[2])+' password='+str(login[3]))
            print('\nTilkobling til havbase db ble opprettet\n')
        except:
            print('Tilkobling til db mislyktes\n')
        
        if self.start_year == 2012:
            if svalbard == True:
                table_year = '2012_svalbard'
            else:
                table_year = '2012'
                
        elif self.start_year == 2013:
            if svalbard == True:
                table_year = '2013_svalbard'
            else:
                table_year = '2013'
                
        elif self.start_year == 2014:
            if svalbard == True:
                table_year = '2014_svalbard'
            else:
                table_year = '2014'
                
        elif self.start_year == 2015:
            if svalbard == True:
                table_year = '2015_svalbard'
            else:
                table_year = '2015'
                
        elif self.start_year == 2016:
            if svalbard == True:
                table_year = '2016_svalbard'
            else:
                table_year = '2016'
                
        elif self.start_year == 2017:
            if svalbard == True:
                table_year = '2017_svalbard'
            else:
                table_year = '2017'
                
        elif self.start_year == 2018:
            if svalbard == True:
                table_year = '2018_svalbard'
            else:
                table_year = '2018'
                
        elif self.start_year == 2019:
            if svalbard == True:
                table_year = '2019_svalbard'
            else:
                table_year = '2019'
                
        elif self.start_year == 2020:
            if svalbard == True:
                table_year = '2020_svalbard'
            else:
                table_year = '2020'
        
        select_statement = "SELECT mmsi, skipskategori, date, period, fk_vessellloydstype, vesselsizegroupgrosston, geom "
        from_statement = "FROM havbasetails"+".tails_"+str(table_year)
        
        sql_syntax = select_statement + from_statement
        
        crs = {'init': 'epsg:4326'}
        ais_haler = gpd.GeoDataFrame.from_postgis(sql_syntax, connection, geom_col='geom', crs=crs)
        print("\nHavbasehaler for "+str(table_year)+" er returnert")
        
        if self.filepath == None:
            pass
        else:
            ais_haler.to_csv(self.filepath, sep=';', index=False, mode='w')
        
        return ais_haler
    
    
#    def fairplay(self):
#        
#        host_adress = '153.44.1.24'
#        db = 'processed_data'
#        username ='postgres'
#        dbkey = 'postgres'
#        login = [host_adress, db, username, dbkey]
#        
#        try:
#            connection = pg.connect('host='+str(login[0])+' dbname='+str(login[1])+' user ='+str(login[2])+' password='+str(login[3]))
#            print('\nTilkobling til db med dagsaktuell Fairplaytabell ble opprettet\n')
#        except:
#            print('Tilkobling til db mislyktes\n')
#        
#        sql_syntax = "SELECT * FROM fairplay.shipdata t1 LEFT JOIN fairplay.tblauxengines t2 ON t1.id = t2.id LEFT JOIN fairplay.tblcargopumps t3 ON t2.id = t3.id LEFT JOIN fairplay.tblclasscodes t4 on t3.id = t4.id LEFT JOIN fairplay.tblenginebuildercodes t5 on t4.id = t5.id LEFT JOIN fairplay.tblflagcodes t6 ON t5.id = t6.id LEFT JOIN fairplay.tbliceclass t7 ON t6.id = t7.id LEFT JOIN fairplay.tblmainengines t8 ON t7.id = t8.id LEFT JOIN fairplay.tblpandicodes t9 ON t8.id = t9.id LEFT JOIN fairplay.tbltowncodes t10 ON t9.id = t10.id;"
#        
#        frame = pd.read_sql(sql_syntax, connection)
#        
#        return frame
#    
#    
#    def fairplay_light(self):
#        
#        host_adress = '153.44.1.24'
#        db = 'processed_data'
#        username ='postgres'
#        dbkey = 'postgres'
#        login = [host_adress, db, username, dbkey]
#        
#        try:
#            connection = pg.connect('host='+str(login[0])+' dbname='+str(login[1])+' user ='+str(login[2])+' password='+str(login[3]))
#            print('\nTilkobling til db med dagsaktuell Fairplaytabell ble opprettet\n')
#        except:
#            print('Tilkobling til db mislyktes\n')
#        
#        col_names = "t1.maritimemobileserviceidentitymmsinumber as mmsi, t1.lrimoshipno as imo, t1.shipname, t1.flagname, t1.flagcode, t1.callsign, t1.fishingnumber, t1.fairplayid, t1.statcode5, t1.shiptypelevel2, t1.shiptypelevel3, t1.shiptypelevel4, t1.shiptypelevel5, t1.classificationsocietycode, t1.dateofbuild, t1.hulltype, t1.yearofbuild, t1.breadth as width, t1.deadweight as dwt, t1.depth, t1.displacement, t1.draught, t1.formuladwt, t1.length, t1.lightdisplacementtonnage, t1.nettonnage, t1.grosstonnage as gt, t1.bollardpull, t1.liquidcapacity, t1.passengercapacity, t1.numberoftanks, t1.teu, t1.registeredowner, t1.registeredownercode, t1.registeredownercountryofdomicilecode, t1.registeredownercountryofcontrol, t1.operatorcompanycode, t1.operatorcountryofregistration, t1.shipmanagercompanycode, t1.shipmanagercoutryofdomicilecode, t1.technicalmanager, t1.mainenginebuildercode, t1.gascapacity, t1.numberofholds, t1.sloptankcapacity, t1.totalpowerofallengines, t1.totalhorsepowerofmainengines, t1.totalkilowattsofmainengine, t1.powerkwservice, t1.powerkwmax, t1.fueltype1capacity, t1.fueltypecode, t1.fueltype2capacity, t1.fueltype2second, t1.numberofallengines, t1.numberofauxiliaryengines, t1.powerbhpihpshpmax, t1.powerbhpihpshpservice, t1.speed, t1.speedmax, t2.enginesequence, t2.enginebuilder, t2.enginedesigner, t2.enginemodel, t2.numberofcylinders, t2.bore, t2.stroke, t2.stroketype, t2.maxpower, t3.sequence as cargopump_sequence, t3.numberofpumps, t3.cubicmeterscapacity, t3.cubictonscapacity, t4.classcode, t4.class, t5.enginebuilderlargestcode, t5.enginebuilderlargest, t7.iceclasscode, t7.iceclass, t8.position, t8.enginetype, t8.enginedesigner, t8.enginebuilder, t8.enginemodel, t8.numberofcylinders, t8.powerbhp, t8.powerkw, t8.rpm, t8.bhpofmainoilengines"
#        
#        sql_syntax = "SELECT "+col_names+" * FROM fairplay.shipdata t1 LEFT JOIN fairplay.tblauxengines t2 ON t1.lrimoshipno = t2.lrno LEFT JOIN fairplay.tblcargopumps t3 ON t1.lrimoshipno = t3.lrno LEFT JOIN fairplay.tblclasscodes t4 on t1.classificationsocietycode = t4.classcode LEFT JOIN fairplay.tblenginebuildercodes t5 on t4.mainenginebuildercode = t5.enginebuilderlargestcode LEFT JOIN fairplay.tbliceclass t7 ON t1.lrimoshipno = t7.lrno LEFT JOIN fairplay.tblmainengines t8 ON t1.mainenginebuildercode = t8.enginemakercode LEFT JOIN fairplay.tblpandicodes t9 ON t1.pandiclubcode = t9.pandiclubcode LEFT JOIN fairplay.tbltowncodes t10 ON t9.id = t10.id;"
#        
#        frame = pd.read_sql(sql_syntax, connection)
#        
#        return frame
#    """
#    SELECT t1.maritimemobileserviceidentitymmsinumber as mmsi, 
#t1.lrimoshipno as imo, 
#t1.shipname, 
#t1.flagname, 
#t1.flagcode, 
#t1.callsign, 
#t1.fishingnumber, 
#t1.fairplayid, 
#t1.statcode5, 
#t1.shiptypelevel2, 
#t1.shiptypelevel3, 
#t1.shiptypelevel4, 
#t1.shiptypelevel5, 
#t1.classificationsocietycode, 
#t1.dateofbuild, 
#t1.hulltype, 
#t1.yearofbuild, 
#t1.breadth as width, 
#t1.deadweight as dwt, 
#t1.depth, t1.displacement, 
#t1.draught, 
#t1.formuladwt, 
#t1.length, 
#t1.lightdisplacementtonnage, 
#t1.nettonnage, 
#t1.grosstonnage as gt, 
#t1.bollardpull, 
#t1.liquidcapacity, 
#t1.passengercapacity, 
#t1.numberoftanks, 
#t1.teu, 
#t1.registeredowner, 
#t1.registeredownercode, 
#t1.registeredownercountryofdomicilecode, 
#t1.registeredownercountryofcontrol, 
#t1.operatorcompanycode, 
#t1.operatorcountryofregistration, 
#t1.shipmanagercompanycode, 
#t1.shipmanagercoutryofdomicilecode, 
#t1.technicalmanager, 
#t1.mainenginebuildercode, 
#t1.gascapacity, 
#t1.numberofholds, 
#t1.sloptankcapacity, 
#t1.totalpowerofallengines, 
#t1.totalhorsepowerofmainengines, 
#t1.totalkilowattsofmainengines, 
#t1.powerkwservice, 
#t1.powerkwmax, 
#t1.fueltype1capacity, 
#t1.fueltype1code, 
#t1.fueltype2capacity, 
#t1.fueltype2second, 
#t1.numberofallengines, 
#t1.numberofauxiliaryengines, 
#t1.powerbhpihpshpmax, 
#t1.powerbhpihpshpservice, 
#t1.speed, 
#t1.speedmax, 
#
#t2.enginesequence, 
#t2.enginebuilder, 
#t2.enginedesigner, 
#t2.enginemodel, 
#t2.numberofcylinders, 
#t2.bore, 
#t2.stroke, 
#t2.stroketype, 
#t2.maxpower, 
#
#t3.sequence as cargopump_sequence, 
#t3.numberofpumps, 
#t3.cubicmeterscapacity, 
#t3.cubictonscapacity, 
#
#t4.classcode, 
#t4.class, 
#
#t5.enginebuilderlargestcode, 
#t5.enginebuilderlargest, 
#
#t7.iceclasscode, 
#t7.iceclass, 
#
#t8.position, 
#t8.enginetype, 
#t8.enginedesigner, 
#t8.enginebuilder, 
#t8.enginemodel, 
#t8.numberofcylinders, 
#t8.powerbhp, 
#t8.powerkw, 
#t8.rpm, 
#t8.bhpofmainoilengines
#
#FROM fairplay.shipdata t1 LEFT JOIN fairplay.tblauxengines t2 ON t1.lrimoshipno = CAST(t2.lrno as text) LEFT JOIN fairplay.tblcargopumps t3 ON t1.lrimoshipno = CAST(t3.lrno as text) LEFT JOIN fairplay.tblclasscodes t4 on t1.classificationsocietycode = t4.classcode LEFT JOIN fairplay.tblenginebuildercodes t5 on t1.mainenginebuildercode = t5.enginebuilderlargestcode LEFT JOIN fairplay.tbliceclass t7 ON t1.lrimoshipno = CAST(t7.lrno as text) LEFT JOIN fairplay.tblmainengines t8 ON t1.mainenginebuildercode = t8.enginemakercode LEFT JOIN fairplay.tblpandicodes t9 ON t1.pandiclubcode = t9.pandiclubcode
#    """
