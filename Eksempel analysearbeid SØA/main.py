# -*- coding: utf-8 -*-
"""
Spyder Editor
Forfatter: Johan Rønbeck
Dette er et internt eksempel ark for bruk av lagde funksjoner for analysearbeid i SØA.
"""
#******************************************************************************
#Importerer eksterne biblioteker
#******************************************************************************
import geopandas as gpd
import pandas as pd
from shapely.wkt import loads as wkt_loads
from shapely.geometry import Point, LineString

#Importerer internt lagede moduler og klasser
from functions import bounding_box, expand_box, make_line, distance_points, lag_haler
from DataBase import DataBase
from Passeringslinje import Passeringslinje

#******************************************************************************
# #Styrer hvor mye som trunkeres av tabell i kernel/console.
# #******************************************************************************
# pd.set_option('display.max_rows', 50)
# pd.set_option('display.max_columns', 25)
# pd.set_option('display.max_colwidth', 25)

# #******************************************************************************
# #Innlesing av csv med geometrikolonne
# #******************************************************************************
# ##sti til mappe hvor du lagrer data til bruk i/fra skriptet##
# folderpath = "C:/Users/5492/Johan_TPU/test_mappe"

# ##Navnet på ønsket avlest fil##
# filename = "tiltakspunkter.xlsx"

# ##Setter sammen navnene, gjør at folderpath kan gjenbrukes til andre formål
# excel_path = folderpath + filename

# ##Navnet på arkfanen i .xlsx filen ønsket avlest. Må skrives  likt som i excel
# arkfane = "Bergen_Floro" 	

# ##Definerer navnet på geometrikolonnen i tabellen som skal jobbes med
# geometry_col = 'punkt_geom_wkt'

# ##Oppretter pandas DataFrame fra csv, dropper rader uten verdi i geometrikolonnen
# punkter = pd.read_excel(excel_path,sheet_name=arkfane).dropna(subset=[geometry_col])

# ##Definerer de kolonnene som ønskes lest ut til tabellen det skal jobbes med
# punkter = punkter[['omraade', 'pakke_nr', 'punkt_navn', 'kategori', 'kommentar_region', 'tiltakspakke', geometry_col]]

# ##Fjerner alle mellomrom/"blank spaces" fra alle valgte kolonner
# #punkter.columns = [col.strip() for col in list(punkter)]

# ##Definerer at geometrien er oppgitt i WellKnownText(wkt)##
# punkter[geometry_col] = punkter[geometry_col].apply(wkt_loads)

# ##gjør DataFrame til GeoDataFrame##
# punkter = gpd.GeoDataFrame(punkter, geometry=geometry_col)	

# ##Definerer projeksjonen til epsg4326##
# punkter.crs = {'init': 'epsg:4326'} 	

# #******************************************************************************
# #Lager avgrensingsbokser basert på innleste tiltakspunkter fra csv
# #******************************************************************************
# ##Minste rektangulære avgrensing som vil omfatte alle punkter. 
# #Kan benyttes på punktsett.
# boks_tiltak = bounding_box(punkter)

# ##Heltallet er områdeøkning i prosent
# utvidet_boks_tiltak = expand_box(boks_tiltak, 50) 

##Manuelt laget boks, uttrykkes i formen (xmin, ymin, xmax, ymax)):
egendefinert_boks = (9.42, 58.8, 9.5, 58.91)

#******************************************************************************
#Lager egendefinert linje(LineString som GeoSeries) (også kalt passeringslinje)
#******************************************************************************
punkt1 = Point(9.45584,58.8388)
punkt2 = Point(9.46928,58.8445)

# passeringslinje = make_line(punkt1, punkt2).iloc[0]

#******************************************************************************
#Avstanden mellom to punkter i meter
#******************************************************************************
# avstand = distance_points(punkt1, punkt2)

#******************************************************************************
#Avlesning av database
#******************************************************************************
#Format: 'yyyy-mm-dd'
start_date = '2019-01-01'
end_date = '2019-03-31'

##Instantierer databaseobjekt avgrenset i tid og av en bounding boks:
# database = DataBase(start_date, end_date, utvidet_boks_tiltak)
database = DataBase(start_date, end_date, egendefinert_boks)
gdf = database.ais_raw_punkter()



##Leser rådata til csv. Tar også argumentet time= hvor default er 180(tre min) og arguentet limit= hvor default er ''##
#database.ais_raw_to_csv(path)
#database.ais_raw_to_csv(path, time=60, limit=None)

##Om argumentet filepath blir gitt en gyldig mappesti vil det skrives en csv dit##
##Argumentet limit kan fjernes og defaulter da til å bli borte fra sql-syntax##
#ais_tpu_punkter = database.tpu_aispunkter() #Arver dato og området fra instantieringen av klassen

#ais_tpu_punkter = database.tpu_aispunkter(limit=10000, filepath=path) 	#Eksempel på begrenset utvalg og skriving av csv

##Rådata kan hentes ut med ønsket ønsket tidsoppløsning. Benytter områdetavgrensing fra instantiering av klassen##
##Argumentet time kan fjernes og defaulter da til tre min==180sekunder##
##Argumentet limit vil begrense uttak per dag, ikke total begrensing. Dette skyldes uttrekk fra databasen per dag.##

##Leser av hele året med tre minutters oppløsning, tidsoppløsning kan som nevnt endres ved behov##
#ais_raw_punkter = database.ais_raw_punkter()    

##Leser av metadata for skip i valgt periode:##
##Metadata som DataFrame med år fra instantiering av databaseklassen##
metadata = database.metadata()

##Leser ut havne_polygoner##
#havner = database.havne_polygoner()

#******************************************************************************
#Lager/henter skipshaler og beriker dem med metadata
#******************************************************************************
##Havbasedata med 6min oppløsning tilgjengelig fra database med tidsseriene 2015,2016,2017##
##Kan trekke ut punkter å benytte lag_haler funksjonen som forventer en GeoDataFrame##

##Funksjon som lager skipshaler som defineres klippet etter hale_evaluering() som finnes i functions.py##
skipshaler = lag_haler(gdf)
#print(skipshaler)
##Beriker skipshaler####Merging av metadata på GeoDataFrame med punkter: God dokumentasjon på concat, append og merge: https://pandas.pydata.org/pandas-docs/version/0.20/merging.html##
skipshaler = skipshaler.merge(metadata, how='left', on='mmsi')

skipshaler.to_csv("C:/Users/33849/Documents/Python/Testkrageroe_haler.csv",sep=';')

# ##Leser av skipshaler fra havbase-løsningen basert på tiden fra instantieringen av databaseklassen##
# #havbase_skipshaler = database.havbase()

# #******************************************************************************
# #unødvendig liten funksjon for skriving til csv
# #******************************************************************************
# ##Funksjon som skriver GeoDataFrame til csv##
# #write_csv(skipshaler, path)

# #******************************************************************************
# #Lager og plotter kart
# #******************************************************************************
# ##Instantierer kartobjektet##
# #kart = Kart(egendefinert_boks)

# ##Fargeverdiene er i hexadecimal gjengivelse av bits. Etter firkanten er det tre fargepar(RGB, Red Green Blue)##
# ##'#FF0000' vil bli rød siden det er maks på det røde paret og null på de andre. '#000000' vil bli svart##
# ##'#FFFFFF' gir hvitt. Man kan blande farger, '#FF00FF' gir lilla.##

# #kart.punkt_plot(gdf.geom, alpha = 0.05, color='#0000FF')   
# #kart.punkt_plot(punkter.punkt_geom_wkt, alpha = 0.5, color='#FF0000')
# #kart.linje_plot(skipshaler.geometry, alpha = 1.0, color='#00FF00')
# #kart.area_plot(havner.geom)

# #******************************************************************************
# ##leser inn passeringslinjer fra shapefil, kan også benytte egenlaget linje ved make_line()
# #******************************************************************************
# ##Leser inn shapefil med to passeringslinjer laget på forhånd og lagret som ESRI .shp / "shapefil"##
# ##Passeringslinjene er laget i kystinfo OBS!! pass på projeksjon(epsg4326/geografisk)##

# shp_file_new = 'oystein_sognefjord_nordfjord/digi_objects_linestring.shp'
# path_shp_new = folderpath+shp_file_new
# passlines_new = gpd.read_file(path_shp_new, driver='ESRI Shapefile', crs='EPSG:4326')
# passlines_new.drop('category', axis=1, inplace=True)

# passlines_sogn = passlines_new.loc[passlines_new.name.isin(['Tollesundet', 'Utvær', 'Lavik','Kvannhovden','Husevågøy','Askgrova'])].reset_index().drop('index', axis=1)  

# bounds = tuple(passlines_new.geometry.total_bounds)

# # passeringer = Passeringslinje(skipshaler, passlines_sogn)

# skipshaler=pd.read_pickle("C:/Users/5492/Johan_TPU/test_mappe/krageroe.pkl")
# test= LineString([(9.45584, 58.8388),(9.469279, 58.8445)])
test= LineString([punkt1,punkt2])
passeringer = Passeringslinje(skipshaler, test)

passeringer.populasjon.head(5)

df_passeringer=passeringer.populasjon
passline_passeringer=passeringer.passline
# poppisen = passeringer.populasjon_dict

# cruise_passeringer = Passeringslinje(cruisehaler, passlines_sogn)
# print(cruise_passeringer.populasjon_dict.keys())

# cruiseframe = pd.concat(cruise_passeringer.populasjon_dict, ignore_index=True)

# cruiseframe.sort_values(['tail_id', 'crossing_time'])
# gruppert_haleruter = cruiseframe.groupby(['tail_id'])

# #.agg({'ant_passeringer':{'Antall Passeringer': 'sum'}, 'mmsi':{'Antall skip': 'count'}})



# shp_file = 'oystein_linjer/digi_objects_linestring.shp'
# path_shp = folderpath+shp_file
# shp_file2 = "tiltakspunkter_svt/Tiltakspunkt _SVT_.shp"
# path2="C:/Work_Space/Strekningsvise analyser/python/Grunnlagsdata/tiltakspunkter_svt/Tiltakspunkt _SVT_.shp"
# path3 = "C:/Work_Space/Strekningsvise analyser/python/Grunnlagsdata/tiltakspunkter_svt/ny_test.html"

# path4 = folderpath+"oystein_shapes/digi_objects_polygon.shp"

# passeringslinjer = gpd.read_file(path_shp, driver='ESRI Shapefile', crs='EPSG:4326')

# passeringslinje1 = passeringslinjer.loc[8, 'geometry']

# passeringer_to = passeringslinjer[passeringslinjer['name'].isin(['Passline_Sotrabroa', 'Passline_Askøybroa'])]



# #Gir avlesning av utgangspunktsgeometri, her Dokken i Bergen
# shp_polys = gpd.read_file(path4, driver='ESRI Shapefile', crs='EPSG:4326')

# gpd_poly_dokken = shp_polys.loc[shp_polys.name == 'Dokken', 'geometry'].values[0]



#passeringslinje2 = passeringslinjer_gdf.loc[1, 'geometry']
#******************************************************************************
#Beregner seilingstider. Funksjonen er blåkopi av menon sin.
#******************************************************************************
##lengde er oppgitt i meter##
##obs_speed er gjennomsnittsfart for skipet mellom linjene##

#seilingstider = seilingstid(skipshaler, passeringslinje1, passeringslinje2, returner_hale_index=False)


# database = DataBase(start_date,end_date, bounds)

# gdf = database.ais_raw_punkter()

# metadata = database.metadata()

# #******************************************************************************
# #Teller passeringer over en passeringlinje(r)
# #******************************************************************************
# ##Instantierer med første argument en GeoDataFrame(skipshaler) og en GeoDataFrame med passeringslinjer eller et shapely-objekt.
# #passeringslinjer = Passeringslinje(skipshaler, passeringslinjer)
# #passeringslinjen = Passeringslinje(skipshaler, passeringslinje1)

# key1 = 'Askøybroa'
# key2 = 'Sotrabroa'

# passeringslinjene = Passeringslinje(skipshaler, passeringslinjer)

# test_table1 = passeringslinjene.linjekalkulasjon(key1, key2)

# pass_test = passeringslinjene.passline


# print(passeringslinjene.populasjon_dict)


# test_dict = passeringslinjene.populasjon_dict


# passeringslinjene2 = Passeringslinje(skipshaler, passeringer_to)



# passeringslinjene = Passeringslinje(skipshaler, passeringslinje1)
# test_gdf = passeringslinjene.rutefordeling(gpd_poly_dokken)
# tester = passeringslinjene.populasjon_dict
# testers = passeringslinjene.populasjon
# passeringslinjene.map_html(punkter, path3 )

# #test_gdf = passeringslinjen.populasjon_dict
# #print(test_gdf)
# #passeringslinjer.antall_skipstype()
# #passeringslinjer.hierchical()
# #print(passeringslinjen.populasjon)
# #passeringslinjen.linjekalkulasjon()



# #kart = Kart(egendefinert_boks)
# #kart.punkt_plot(gdf.geom, alpha = 0.05, color='#0000FF') 
# #kart.linje_plot(skipshaler.geometry, alpha = 1.0, color='#00FF00')



