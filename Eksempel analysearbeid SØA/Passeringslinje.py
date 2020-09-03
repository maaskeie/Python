# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 10:35:41 2019

@author: 5240
"""

from functools import partial
import pyproj
import numpy as np
import pandas as pd
import folium
from folium import FeatureGroup, Marker, plugins
from shapely.ops import transform
from shapely.geometry import LineString
from geopandas import GeoDataFrame

from functions import line_bearing, bounding_box, passline_limits



class Passeringslinje(object):
    """
    En klasse for å håndtere passeringslinjer og funksjoner knyttet til dette.
    """

    def __init__(self, gdf, passline):

        #Gjøres tilgjengelig grunnet bruk i klassefunksjoner
        self.gdf = gdf
        self.passline = passline

        #Gjøres tilgjengelig grunnet intern og ekstern bruk
        self.populasjon = GeoDataFrame()
        self.unique_mmsi_dict = {}
        self.populasjon_dict = {}
        self.grupperte_passeringer_dict = {}


#==============================================================================
#Her behandles analysen av en enkelt trafikklinje gitt som LineString
#==============================================================================

        #Sjekker om vi jobber med en eller fler passeringslinjer
        if type(self.passline)==LineString:

            #Lager en serie med True/False basert på om krysser eller ikke
            passeringer = self.gdf.intersects(self.passline)

            #Legger til kolonne med summering av passeringer. 
            #Gjengir antall involverte objekter, ikke antallet krysninger
            self.antall_haler = self.gdf.assign(passeringer=passeringer).query('passeringer != 0')['passeringer'].sum(axis=0)

            #begrenser populasjon til skipshaler som har passert linjen
            self.populasjon = self.gdf.assign(passeringer=passeringer).query('passeringer != 0')

            #Lager en liste over unike mmsi`er i populasjonen
            self.unique_mmsi_list = self.populasjon.mmsi.unique()

            #Finner antallet unike skip ved summering av unike mmsi`er
            self.antall_unike_skip = len(self.unique_mmsi_list)

            #Henter ut koordinatene for krysningspunktene
            krysninger = self.populasjon.intersection(self.passline)

            self.populasjon['crossing_point'] = krysninger

            #Lager listevariabler til å lagre verdier for snekring av sluttpopulasjon
            cross_heading = list()
            cross_time = list()
            heading_geometric = list()
            tail_list = list()

            columns = self.populasjon.columns

            #Lager duplikate rader av halene med MultiPoint slik at alle rader representerer en unik passering
            for idx, row in self.populasjon.iterrows():

                if 'Point' == row.crossing_point.type:
                    tail_list.append(row)

                elif 'MultiPoint' == row.crossing_point.type:
                    tmp_points = list()
                    tmp_points.extend(p for p in row.crossing_point)

                    for i in range(len(tmp_points)):
                        row['crossing_point'] = tmp_points[i]
                        tail_list.append(row)

            crs = {'init': 'epsg:4326'}
            #Setter sammen halene til en GeoDataFrame
            self.populasjon = GeoDataFrame(pd.DataFrame.from_records(tail_list, columns=columns), geometry='geometry', crs=crs)


            for idx, row in self.populasjon.iterrows():

                #Henter ut den aktuelle raden sin LineString
                line = row.geometry

                #Lager listevariabler for lagring av linjens x- og y-koordinater 
                coord_list_x = []
                coord_list_y = []

                #løper gjennom linjen punkt for punkt og henter ut de respektive koordinatbestandene
                for coords in line.coords:
                    coord_list_x.append(coords[0])
                    coord_list_y.append(coords[1])

                #Deler krysningspunktet i sine respektive deler
                pass_coords_x = row['crossing_point'].x
                pass_coords_y = row['crossing_point'].y

                #Leter etter nærmeste verdi i linjens liste over x- og y-koordinater
                listeposisjon_x = min(range(len(coord_list_x)), key=lambda i: abs(coord_list_x[i]-pass_coords_x))
                listeposisjon_y = min(range(len(coord_list_y)), key=lambda i: abs(coord_list_y[i]-pass_coords_y))

                #Da det ikke er gitt at dette vil bli samme punkt for x-verdier og y-verdier henter jeg snittposisjonen når dem ikke er like. 
                listeposisjon = int((listeposisjon_x+listeposisjon_y)/2)

                #Henter ut heading og tidspunkt fra riktig plass i listene som lages i lag_haler() som finnes i functions.py 
                cross_heading.append(row.pass_heading[listeposisjon])
                cross_time.append(row.times[listeposisjon])

                tmp_point1 = line.coords[listeposisjon-1]
                tmp_point2 = line.coords[listeposisjon]

                tmp_line = LineString([(tmp_point1), (tmp_point2)])
                tmp_bearing = line_bearing(tmp_line)
                heading_geometric.append(tmp_bearing)

            #Legger til kolonne for passeringspunktets koordinater, heading og tidspunkt ved krysning. Fjerner listevariablene fra lag_haler()
            self.populasjon['heading_geometric'] = heading_geometric
            self.populasjon['heading'] = cross_heading
            self.populasjon['crossing_time'] = cross_time
            try:
                self.populasjon.drop(['times', 'pass_heading'], axis=1, inplace=True)
            except:
                pass

            #line_bearing() importeres fra functions.py
            passline_angle = line_bearing(self.passline)

            #passline_limits() finnes i functions.py  Krever passline_angle som argument og returnerer grensevinkel en og to samt trafikkretning
            #Kategoriserer skipstrafikk til enten Nord/Sør eller Øst/Vest for å kunne skille den dikotomisk
            #Grensene for trafikkinndelingen skjer dynamisk basert på passeringslinjens orientasjon.
            limit1, limit2, trafikk_retning = passline_limits(passline_angle)

            retning_list = list()

            #itererer gjennom kryssende skipshaler for å klassifisere dem på retning over linja
            for idx, row in self.populasjon.iterrows():

                if trafikk_retning == 'Ost/Vest':

                    if row['heading'] >= limit1 and row['heading'] <= limit2:

                        retning_list.append('Ost')
                    else:
                        retning_list.append('Vest')

                elif trafikk_retning == 'Nord/Syd':

                    if row['heading'] > limit1 and row['heading'] < limit2:

                        retning_list.append('Syd')
                    else:
                        retning_list.append('Nord')

            self.populasjon['retning'] = retning_list

            # printer noen interessante variabler til konsollen
            print('\n*******************************************')
            print('Passeringslinjeklasse er vellykket initiert')
            print('*******************************************\n')
            print(str(self.antall_haler)+' skipshaler har krysset passeringslinjen\n')
            print('Skipspopulasjonen består av '+str(self.antall_unike_skip)+' unike mmsi numre.')
            print('\nAntallet krysninger av linjene er: '+str(self.populasjon.shape[0])+'\n')


#==============================================================================
#Her behandles analysen av passeringslinjene gitt som GeoDataFrame
#==============================================================================

        elif type(self.passline)==GeoDataFrame:

            #Henter ut antallet passeringslinjer
            self.passline_antall = self.passline.shape[0]

            antall_haler_dict = dict()
            antall_unike_skip_dict = dict()

            #Teller for å telle det totale antallet passeringer for alle linjer
            total_counter = 0

            #liste for lagring av printtekst for den enkelte linje som initieres
            self.print_list = list()

            for i in range(self.passline_antall):

                #Henter ut aktuell passeringslinje som shapely LineString
                current_passline = self.passline.loc[i, 'geometry']

                #Henter ut navnet til passeringslinjen, benyttes osm keys i samlings-dictionary til slutt
                passeringlinje_navn = self.passline.loc[i, self.passline.columns[0]]#.lstrip('Passline_')

                #Lager en Serie på lengde med gdf som indikerer med en bool.-verdi om det er krysning eller ikke
                passeringer = self.gdf.intersects(current_passline)

                #Summerer sammen for å finne antallet haler som er involvert/antallet objekter som krysser linjen
                antall_haler_dict[passeringlinje_navn] = self.gdf.assign(passeringer=passeringer).query('passeringer != 0')['passeringer'].sum(axis=0)

                #Henter ut halene som krysser, også kalt skipspopulasjonen og legger den som value i en dictionary med passeringslinjenavn som key               
                self.populasjon_dict[passeringlinje_navn] = self.gdf.assign(passeringer=passeringer).query('passeringer != 0')

                #Legger unike mmsier representert i krysningen av linjen i en dictionary med passeringslinjenavn som key
                self.unique_mmsi_dict[passeringlinje_navn] = self.populasjon_dict[passeringlinje_navn].mmsi.unique()

                #Summerer sammen for å finne antallet unike mmsièr som er representert i populasjonen
                antall_unike_skip_dict[passeringlinje_navn] = len(self.unique_mmsi_dict[passeringlinje_navn])

                #Henter ut en Serie med krysningspunktene mellom skipspopulasjonen og linjen, kan være MultiPoint, LineString, GeometryCollection. Foreløpig ikke støtt på de to siste
                krysninger = self.populasjon_dict[passeringlinje_navn].intersection(current_passline)

                self.populasjon_dict[passeringlinje_navn]['crossing_point'] = krysninger

                columns = self.populasjon_dict[passeringlinje_navn].columns

                tail_list = list()

                #Lager duplikate rader hvor det er flere "intersections" slik at hver rad representerer en unik passering
                for idx, row in self.populasjon_dict[passeringlinje_navn].iterrows():

                    if 'Point' == row.crossing_point.type:
                        tail_list.append(row)

                    elif 'MultiPoint' == row.crossing_point.type:
                        tmp_points = list()
                        tmp_points.extend(p for p in row.crossing_point)

                        for i in range(len(tmp_points)):
                            row['crossing_point'] = tmp_points[i]
                            tail_list.append(row)

                crs = {'init': 'epsg:4326'}

                #Setter sammen den nye GeoDataFramen som har egen rad for hver unike passering.
                self.populasjon_dict[passeringlinje_navn] = GeoDataFrame(pd.DataFrame.from_records(tail_list, columns=columns), geometry='geometry', crs=crs)

                #Lager listevariabler for lagring av skipets orientering ved krysning og tidspunktet for krysningen
                cross_heading = list()
                cross_time = list()
                heading_geometric = list()
                krysningspunkt_nr = list()
                
                #Hvis ikke det er noen krysninger på den aktuelle passeringslinjen går vi videre
                if antall_haler_dict[passeringlinje_navn]==0:
                    pass
                else:

                    for idx, row in self.populasjon_dict[passeringlinje_navn].iterrows():

                        #Henter ut den aktuelle raden sin LineString
                        line = row.geometry

                        #Lager listevariabler for lagring av linjen x- og y-koordinater 
                        coord_list_x = list()
                        coord_list_y = list()

                        #løper gjennom linjen punkt for punkt og henter ut de respektive koordinatbestandene
                        for coords in line.coords:
                            coord_list_x.append(coords[0])
                            coord_list_y.append(coords[1])

                        #Deler krysningspunktet i sine respektive deler
                        pass_coords_x = row['crossing_point'].x
                        pass_coords_y = row['crossing_point'].y

                        #Leter etter nærmeste verdi i linjens liste over x- og y-koordinater
                        #Link!!!
                        listeposisjon_x = min(range(len(coord_list_x)), key=lambda i: abs(coord_list_x[i]-pass_coords_x))
                        listeposisjon_y = min(range(len(coord_list_y)), key=lambda i: abs(coord_list_y[i]-pass_coords_y))

                        #Da det ikke er gitt at dette vil bli samme punkt for x-verdier og y-verdier henter jeg snittposisjonen når dem ikke er like. 
                        listeposisjon = int((listeposisjon_x+listeposisjon_y)/2)

                        #Henter ut heading og tidspunkt fra riktig plass i listene som lages i lag_haler() som finnes i functions.py 
                        cross_heading.append(row.pass_heading[listeposisjon])
                        cross_time.append(row.times[listeposisjon])

                        tmp_point1 = line.coords[listeposisjon-1]
                        tmp_point2 = line.coords[listeposisjon]
                        
                        tmp_line = LineString([(tmp_point1), (tmp_point2)])
                        tmp_bearing = line_bearing(tmp_line)
                        heading_geometric.append(tmp_bearing)
                        krysningspunkt_nr.append(listeposisjon)

                    #Legger til kolonne for passeringspunktets koordinater, heading og tidspunkt ved krysning. Fjerner listevariablene fra lag_haler()
                    self.populasjon_dict[passeringlinje_navn]['heading_geometric'] = heading_geometric
                    self.populasjon_dict[passeringlinje_navn]['heading'] = cross_heading
                    self.populasjon_dict[passeringlinje_navn]['crossing_time'] = cross_time
                    self.populasjon_dict[passeringlinje_navn]['point_position'] = krysningspunkt_nr
                    self.populasjon_dict[passeringlinje_navn].drop(['times', 'pass_heading'], axis=1, inplace=True)

                #kalkulerer bearing til passeringslinjen. line_bearing() finnes i functions.py
                passline_angle = line_bearing(current_passline)

                #passline_limits() finnes i functions.py  Krever passline_angle som argument og returnerer grensevinkel en og to samt trafikkretning
                #Kategoriserer skipstrafikk til enten Nord/Sør eller Øst/Vest for å kunne skille den dikotomisk
                #Grensene for trafikkinndelingen skjer dynamisk basert på passeringslinjens orientasjon.
                limit1, limit2, trafikk_retning = passline_limits(passline_angle)
                
                self.passline['trafikk_retning'] = trafikk_retning
                
                retning_list = list()
                rutepunkt_list = list()

                #itererer gjennom kryssende skipshaler for å klassifisere dem på retning over linja
                for idx, row in self.populasjon_dict[passeringlinje_navn].iterrows():

                    if trafikk_retning == 'Ost/Vest':

                        if row['heading'] >= limit1 and row['heading'] <= limit2:
                            retning_list.append('Ost')
                            tmp_rutepunkt = str(passeringlinje_navn) + 'Ost'
                            rutepunkt_list.append(tmp_rutepunkt)
                        else:
                            retning_list.append('Vest')
                            tmp_rutepunkt = str(passeringlinje_navn) + 'Vest'
                            rutepunkt_list.append(tmp_rutepunkt)

                    elif trafikk_retning == 'Nord/Syd':
                        if row['heading'] > limit1 and row['heading'] < limit2:
                            retning_list.append('Syd')
                            tmp_rutepunkt = str(passeringlinje_navn) + 'Syd'
                            rutepunkt_list.append(tmp_rutepunkt)

                        else:
                            retning_list.append('Nord')
                            tmp_rutepunkt = str(passeringlinje_navn) + 'Nord'
                            rutepunkt_list.append(tmp_rutepunkt)
                    else:
                        pass

                self.populasjon_dict[passeringlinje_navn]['retning'] = retning_list
                self.populasjon_dict[passeringlinje_navn]['passert_linje'] = passeringlinje_navn 
                self.populasjon_dict[passeringlinje_navn]['rutepunkt'] = rutepunkt_list

                antall_krysninger = self.populasjon_dict[passeringlinje_navn].shape[0]

                total_counter += antall_krysninger

                print_string = "\n*********************************************\nPasseringslinje "+str(passeringlinje_navn)+"\n*********************************************\n"+str(antall_haler_dict[passeringlinje_navn])+" skipshaler har krysset over linjen\nSkipspopulasjonen består av "+str(antall_unike_skip_dict[passeringlinje_navn])+" unike mmsi nummer\nAntallet krysninger av linjen er "+str(antall_krysninger)+"\n"

                self.print_list.append(print_string)

            # printer noen interessante variabler til konsollen
            print('\n*********************************************')
            print('Passeringslinjeklasse er vellykket initiert')
            print('*********************************************\n')
            print('De '+str(self.passline_antall)+' linjene har samlet blitt krysset '+str(total_counter)+' antall ganger.')

            for item in self.print_list:
                print(item)
            
            self.total_populasjon = GeoDataFrame(pd.concat(self.populasjon_dict, ignore_index=True, sort=False), geometry='geometry', crs = crs)


    def antall_skipstype(self, column='shiptype_nr', agg_column = 'Antall_passeringer'):
        
        if type(self.passline)==LineString:
            
            self.grupperte_passeringer = self.populasjon.groupby([column]).agg({agg_column:{'Antall Passeringer': 'sum'}, 'mmsi':{'Antall skip': 'count'}})
            self.grupperte_passeringer.columns = self.grupperte_passeringer.columns.droplevel(0)
            self.grupperte_passeringer = self.grupperte_passeringer.reset_index()
            self.grupperte_passeringer.rename(columns={'shiptype_nr': 'Skipstype_nr'}, inplace=True)
            
            print('\nAntall skip passert gruppert på skipstype: ')
            print(self.grupperte_passeringer)
            
            return self.grupperte_passeringer
        
        elif type(self.passline)==GeoDataFrame:
            
            self.group_table_dict = {}
            self.grupperte_passeringer_dict = {}
            
            for i in range(self.passline_antall):
                
                passeringlinje_navn = self.passline.loc[i, self.passline.columns[0]]
                
                self.grupperte_passeringer_dict[passeringlinje_navn] = self.populasjon_dict[passeringlinje_navn].groupby([column]).agg({agg_column:{'Antall Passeringer': 'sum'}, 'mmsi':{'Antall skip': 'count'}})
 
                self.grupperte_passeringer_dict[passeringlinje_navn].columns = self.grupperte_passeringer_dict[passeringlinje_navn].columns.droplevel(0)
                self.grupperte_passeringer_dict[passeringlinje_navn] = self.grupperte_passeringer_dict[passeringlinje_navn].reset_index()
                self.grupperte_passeringer_dict[passeringlinje_navn].rename(columns={'shiptype_nr': 'Skipstype_nr'}, inplace=True)
                 
            
            print('Antall skip per passeringslinje gruppert på skipstype: ')
            print(self.grupperte_passeringer_dict)
              
            return self.grupperte_passeringer_dict
        
        else:
            pass
        
    
    def pivot(self, index='shiptype_label', column='lengdegruppe'):
         #Lager fasit på rekkefølge på kolonner
        column_list=['Missing_length', '0-12', '12-21', '21-28', '28-70', '70-100', '100-150', '150-200', '200-250', '250-300', '300-350', '<350']
        
        if type(self.passline)==LineString:
                        
            
            #Lager pivottabellen, vil få kolonner i tilfeldig rekkefølge
            pivot = self.populasjon.pivot_table(values= 'passeringer', index= [index], columns=[column], aggfunc=np.sum)
            
            
            #Henter ut kolonnene som er felles for fasit på rekkefølge og pivot
            columns = [x for x in column_list if x in pivot]
            
            #Sørger for at kolonnene kommer i riktig rekkefølge
            pivot=pivot[columns]
            
            return pivot
        
        elif type(self.passline)==GeoDataFrame:
            pivot_table_dict = {}
            self.pivot_dict = {}
            
            for i in range(self.passline_antall):
                
                passeringlinje_navn = self.passline.loc[i, self.passline.columns[0]]
                
                pivot_table_dict[passeringlinje_navn] = self.populasjon_dict[passeringlinje_navn].pivot_table(values= 'passeringer', index= [index], columns=[column], aggfunc=np.sum)
                
                columns = [x for x in column_list if x in pivot_table_dict[passeringlinje_navn]]       
                                
                self.pivot_dict[passeringlinje_navn] = pivot_table_dict[passeringlinje_navn][columns]
                
            print("\nPivot-tabeller samlet i en dictionary med passeringslinjenavn som 'key' \n")

            return self.pivot_dict
    
        else:
            pass

    def hierchical(self):
        
        if type(self.passline)==LineString:
            
            grupperte_passeringer = self.populasjon.groupby(['shiptype_label', 'retning']).agg({'passeringer':{'Antall Passeringer': 'sum'}, 'mmsi':{'Antall skip': 'count'}})
            grupperte_passeringer.columns = grupperte_passeringer.columns.droplevel(0)
            grupperte_passeringer.unstack(0)
            
            return grupperte_passeringer
        
        elif type(self.passline)==GeoDataFrame:
            
            grupperte_passeringer_dict = dict()
            
            for i in range(self.passline_antall):
                
                passeringlinje_navn = self.passline.loc[i, self.passline.columns[0]]
                grupperte_passeringer_dict[passeringlinje_navn] = self.populasjon_dict[passeringlinje_navn].groupby(['shiptype_label', 'skipsretning']).agg({'ant_passeringer':{'Antall Passeringer': 'sum'}, 'mmsi':{'Antall skip': 'count'}})
                grupperte_passeringer_dict[passeringlinje_navn].columns = grupperte_passeringer_dict[passeringlinje_navn].columns.droplevel(0)
                grupperte_passeringer_dict[passeringlinje_navn].unstack()
            
        return grupperte_passeringer_dict
            
#Not working yet
    def pivot_split_direction(self):
        
        gdf_dict = self.populasjon_dict
        retning = self.passline['trafikk_retning']
        gdf = GeoDataFrame()
        for i in range(self.passline_antall):
        
        
        
            retning1_list = list()
            retning2_list = list()
            
            for row in retning:
                
                passeringlinje_navn = self.passline.loc[row, self.passline.columns[0]].lstrip('Passline_')
                
                retning1, retning2 = row['trafikk_retning'].split("/")
                
                retning1_list.append(retning1)
                retning2_list.append(retning2)
        
                    
        gdf1 = gdf_dict[gdf.skipsretning == retning1]
        gdf2 = gdf_dict[gdf.skipsretning == retning2]
        pivot2 = pd.pivot_table(gdf2, values= ['ant_passeringer'], index= ['shiptype_nr', 'lengdegruppe'], columns=['skipsretning'], aggfunc=np.sum )
        pivot1 = pd.pivot_table(gdf1, values= ['ant_passeringer'], index= ['shiptype_nr', 'lengdegruppe'], columns=['skipsretning'], aggfunc=np.sum )
        
        return pivot1, pivot2


    def map_html(self, tiltakspunkter, filepath):
        """
        tiltakspunkter er av typen Point og oppgitt i epsg:4326
        filepath er der du ønsker .html filen med kart skal havne.
        """

        tiltakspunkter = tiltakspunkter

        
        box_tmp = bounding_box(tiltakspunkter)
        box_center_x = (box_tmp[0]+box_tmp[2])/2 
        box_center_y = (box_tmp[1]+box_tmp[3])/2
        
        map_center_lon = box_center_x
        map_center_lat = box_center_y
        
        map = folium.Map(location=[map_center_lat,map_center_lon], zoom_start=9, tiles='Stamen Terrain')
        
        tiltaksFeature = FeatureGroup(name='Tiltakspunkter', show=False)
        
        marker_cluster = plugins.MarkerCluster(options = dict(zoomToBoundsOnClick = False)).add_to(tiltaksFeature)
        
        #feature_tiltak = FeatureGroup(name='tiltakspunkter')
        tooltip_tiltak = 'Tiltakspunkt'
        
        tmp_tiltak = tiltakspunkter['punkt_geom_wkt']
        x_list = tmp_tiltak.apply(lambda p: p.x)
        y_list = tmp_tiltak.apply(lambda p: p.y)
        for i in range(0, len(x_list)):
            try:
                Marker(location=[y_list[i],x_list[i]], popup=tiltakspunkter['punkt_navn'][i], icon=folium.Icon(color='red', icon_color='black', icon='angle-double-down', prefix = 'fa'), tooltip = tooltip_tiltak).add_to(marker_cluster)
            except:
                Marker(location=[y_list[i],x_list[i]], popup='Atter et punkt', icon=folium.Icon(color='red', icon_color='black', icon='angle-double-down', prefix = 'fa'), tooltip = tooltip_tiltak).add_to(marker_cluster)
        
        
        feature_skipshaler = FeatureGroup(name='skipshaler')
        

        try:
            oljetankskip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'oljetankskip')
            
            haler_feat_10 = self.total_populasjon[self.total_populasjon.shiptype_nr == 10]
            skipshaler_10_json = haler_feat_10.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#4DB6AC', 'weight' : 3, 'opacity': 0.1,}
            haler_olje = folium.features.GeoJson(skipshaler_10_json, style_function=style_skipshaler)
            haler_olje.add_to(oljetankskip)
        except:
            pass
        
        try:
            kjemikalie_produkttankskip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'kjemikalie_produkttankskip')
            
            haler_feat_11 = self.total_populasjon[self.total_populasjon.shiptype_nr == 11]
            skipshaler_11_json = haler_feat_11.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#26A69A', 'weight' : 3, 'opacity': 0.1,}
            haler_kjemi = folium.features.GeoJson(skipshaler_11_json, style_function=style_skipshaler)
            haler_kjemi.add_to(kjemikalie_produkttankskip)
        except:
            pass
        
        try:        
            gasstankskip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'gasstankskip')
            
            haler_feat_12 = self.total_populasjon[self.total_populasjon.shiptype_nr == 12]
            skipshaler_12_json = haler_feat_12.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#009688', 'weight' : 3, 'opacity': 0.1,}
            haler_gass = folium.features.GeoJson(skipshaler_12_json, style_function=style_skipshaler)
            haler_gass.add_to(gasstankskip)
        except:
            pass
        
        try:            
            bulkskip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'bulkskip')
            
            haler_feat_13 = self.total_populasjon[self.total_populasjon.shiptype_nr == 13]
            skipshaler_13_json = haler_feat_13.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#00897B', 'weight' : 3, 'opacity': 0.1,}
            haler_bulk = folium.features.GeoJson(skipshaler_13_json, style_function=style_skipshaler)
            haler_bulk.add_to(bulkskip)
        except:
            pass
        
        try:            
            stykkgods_roro_skip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'stykkgods_roro_skip')
            
            haler_feat_14 = self.total_populasjon[self.total_populasjon.shiptype_nr == 14]
            skipshaler_14_json = haler_feat_14.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#00796B', 'weight' : 3, 'opacity': 0.1,}
            haler_stykkgods = folium.features.GeoJson(skipshaler_14_json, style_function=style_skipshaler)
            haler_stykkgods.add_to(stykkgods_roro_skip)
        except:
            pass
        
        try:            
            konteinerskip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'konteinerskip')
            
            haler_feat_15 = self.total_populasjon[self.total_populasjon.shiptype_nr == 15]
            skipshaler_15_json = haler_feat_15.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#00695C', 'weight' : 3, 'opacity': 0.1,}
            haler_konteiner = folium.features.GeoJson(skipshaler_15_json, style_function=style_skipshaler)
            haler_konteiner.add_to(konteinerskip)
        except:
            pass
        
        try:            
            passasjerbat = plugins.FeatureGroupSubGroup(feature_skipshaler, 'passasjerbat')
            
            haler_feat_16 = self.total_populasjon[self.total_populasjon.shiptype_nr == 16]
            skipshaler_16_json = haler_feat_16.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#81C784', 'weight' : 3, 'opacity': 0.1,}
            haler_passasjer = folium.features.GeoJson(skipshaler_16_json, style_function=style_skipshaler)
            haler_passasjer.add_to(passasjerbat)
        except:
            pass
        
        try:            
            ropax_skip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'ropax_skip')
            
            haler_feat_17 = self.total_populasjon[self.total_populasjon.shiptype_nr == 17]
            skipshaler_17_json = haler_feat_17.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#66BB6A', 'weight' : 3, 'opacity': 0.1,}
            haler_ropax = folium.features.GeoJson(skipshaler_17_json, style_function=style_skipshaler)
            haler_ropax.add_to(ropax_skip)
        except:
            pass
        
        try:
            cruiseskip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'cruiseskip')
            
            haler_feat_18 = self.total_populasjon[self.total_populasjon.shiptype_nr == 18]
            skipshaler_18_json = haler_feat_18.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#4CAF50', 'weight' : 3, 'opacity': 0.1,}
            haler_cruise = folium.features.GeoJson(skipshaler_18_json, style_function=style_skipshaler)
            haler_cruise.add_to(cruiseskip)
        except:
            pass
            
        try:                    
            offshore_supplyskip = plugins.FeatureGroupSubGroup(feature_skipshaler, 'offshore_supplyskip')
            
            haler_feat_19 = self.total_populasjon[self.total_populasjon.shiptype_nr == 19]
            skipshaler_19_json = haler_feat_19.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#43A047', 'weight' : 3, 'opacity': 0.1,}
            haler_offshore = folium.features.GeoJson(skipshaler_19_json, style_function=style_skipshaler)
            haler_offshore.add_to(offshore_supplyskip)
        except:
            pass
        
        try:            
            andre_offshorefartoy = plugins.FeatureGroupSubGroup(feature_skipshaler, 'andre_offshorefartoy')
            
            haler_feat_20 = self.total_populasjon[self.total_populasjon.shiptype_nr == 20]
            skipshaler_20_json = haler_feat_20.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#388E3C', 'weight' : 3, 'opacity': 0.1,}
            haler_andre_offshore = folium.features.GeoJson(skipshaler_20_json, style_function=style_skipshaler)
            haler_andre_offshore.add_to(andre_offshorefartoy)
        except:
            pass
        
        try:            
            bronnbat = plugins.FeatureGroupSubGroup(feature_skipshaler, 'bronnbat')
            
            haler_feat_21 = self.total_populasjon[self.total_populasjon.shiptype_nr == 21]
            skipshaler_21_json = haler_feat_21.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#00E676', 'weight' : 3, 'opacity': 0.1,}
            haler_bronn = folium.features.GeoJson(skipshaler_21_json, style_function=style_skipshaler)
            haler_bronn.add_to(bronnbat)
        except:
            pass
        
        try:            
            slepefartoy = plugins.FeatureGroupSubGroup(feature_skipshaler, 'slepefartoy')
            
            haler_feat_22 = self.total_populasjon[self.total_populasjon.shiptype_nr == 22]
            skipshaler_22_json = haler_feat_22.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#00C853', 'weight' : 3, 'opacity': 0.1,}
            haler_slepe = folium.features.GeoJson(skipshaler_22_json, style_function=style_skipshaler)
            haler_slepe.add_to(slepefartoy)
        except:
            pass
        
        try:            
            andre_servicefartoy = plugins.FeatureGroupSubGroup(feature_skipshaler, 'andre_servicefartoy')
            
            haler_feat_23 = self.total_populasjon[self.total_populasjon.shiptype_nr == 23]
            skipshaler_23_json = haler_feat_23.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#9CCC65', 'weight' : 3, 'opacity': 0.1,}
            haler_andre_service = folium.features.GeoJson(skipshaler_23_json, style_function=style_skipshaler)
            haler_andre_service.add_to(andre_servicefartoy)
        except:
            pass
        
        try:            
            fiskefartoy = plugins.FeatureGroupSubGroup(feature_skipshaler, 'fiskefartoy')
            
            haler_feat_24 = self.total_populasjon[self.total_populasjon.shiptype_nr == 24]
            skipshaler_24_json = haler_feat_24.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#7CB342', 'weight' : 3, 'opacity': 0.1,}
            haler_fisk = folium.features.GeoJson(skipshaler_24_json, style_function=style_skipshaler)
            haler_fisk.add_to(fiskefartoy)
        except:
            pass
        
        try:            
            annet = plugins.FeatureGroupSubGroup(feature_skipshaler, 'annet')
            
            haler_feat_25 = self.total_populasjon[self.total_populasjon.shiptype_nr == 25]
            skipshaler_25_json = haler_feat_25.to_json(default=str)
            style_skipshaler=lambda x: {'color' : '#558B2F', 'weight' : 3, 'opacity': 0.1,}
            haler_annet = folium.features.GeoJson(skipshaler_25_json, style_function=style_skipshaler)
            haler_annet.add_to(annet)
        except:
            pass
        
        
        
        feature_passlines = FeatureGroup(name='passeringslinjer')
        passeringslinje_json = self.passline.to_json(default=str)
        tooltip_passeringslinje = 'Passeringslinje'
        style_passline=lambda x: {'color' : '#000000', 'weight' : 4, 'opacity': 1.0,}
        folium.features.GeoJson(passeringslinje_json, style_function=style_passline, tooltip = tooltip_passeringslinje).add_to(feature_passlines)
                
        
        #feature_tiltak.add_to(marker_cluster)
        marker_cluster.add_to(map)
        feature_passlines.add_to(map)
        feature_skipshaler.add_to(map)
        oljetankskip.add_to(map)
        kjemikalie_produkttankskip.add_to(map)
        gasstankskip.add_to(map)
        bulkskip.add_to(map)
        stykkgods_roro_skip.add_to(map)
        konteinerskip.add_to(map)
        passasjerbat.add_to(map)
        ropax_skip.add_to(map)
        cruiseskip.add_to(map)
        offshore_supplyskip.add_to(map)
        andre_offshorefartoy.add_to(map)
        bronnbat.add_to(map)
        slepefartoy.add_to(map)
        andre_servicefartoy.add_to(map)
        fiskefartoy.add_to(map)
        annet.add_to(map)
        
        folium.LayerControl(collapsed=False).add_to(map)    
        
        minimap = plugins.MiniMap()
        
        map.add_child(minimap)
        map.add_child(folium.LatLngPopup())
        
        
        map.save(filepath)


    def linjekalkulasjon(self, key1, key2):

        if type(self.passline)==LineString:
            print('Denne funksjonen gir ingen mening med en passeringslinje, vennligst sjekk dette objektet.')
            
        elif type(self.passline)==GeoDataFrame:
            
            passline_populasjon = self.populasjon_dict[key1]
            passline_populasjon2 = self.populasjon_dict[key2][['tail_id', 'crossing_point', 'crossing_time', 'rutepunkt', 'point_position']]
            
            diff_tabell = passline_populasjon.merge(passline_populasjon2, on= 'tail_id', how= 'inner')
            
            diff_tabell['tid_diff'] = abs(diff_tabell['crossing_time_x'] - diff_tabell['crossing_time_y'])
            
            crs = {'init': 'epsg:4326'}
            
            diff_tabell = GeoDataFrame(diff_tabell, geometry='geometry', crs = crs)
            
            avstand_liste= list()
            snittfart_liste = list()
            
            for idx, row in diff_tabell.iterrows():
                
                tmp_linje = row['geometry']
                
                point_position1 = row['point_position_x']
                point_position2 = row['point_position_y']


#GIR DETTE MENING
                if point_position1 < point_position2:
                    split_line = LineString(tmp_linje.coords[point_position1:(point_position2+1)])
                else:
                    split_line = LineString(tmp_linje.coords[(point_position2):point_position1+1])
                    
                project = partial(pyproj.transform, pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:32633'))                    
                new_line = transform(project, split_line)
                tmp_avstand = new_line.length
                avstand_liste.append(tmp_avstand)
                tid_sekund = row['tid_diff'].seconds

                try:
                    snittfart = tmp_avstand/tid_sekund
                except:
                    snittfart = 'NaN'

                snittfart_liste.append(snittfart)
                                
            diff_tabell['avstand_diff'] = avstand_liste
            diff_tabell['snittfart'] = snittfart_liste
                        
            return diff_tabell
            
        else:
            print('Funksjonen er ikke riktig instantiert')
        
    
    
  #  def rutefordeling(self, start_linje):
        
    #    rutepopulasjon = self.populasjon_dict


#         gdf_populasjon = self.gdf.assign(passeringer = self.gdf.intersects(poly_dokken)).query('passeringer == True').reset_index().drop('index', axis=1)
#         
#         unik_populasjon = gdf_populasjon.drop_duplicates(['mmsi', 'start_time'])
#         
#         frame_list = []
#         
#         for i in range(self.passline_antall):
#             passeringlinje_navn = self.passline.loc[i, self.passline.columns[0]]
#             tmp_gdf = self.populasjon_dict[passeringlinje_navn]
# 
#             if type(tmp_gdf) == type:
#                 pass
#             elif type(tmp_gdf) == GeoDataFrame:
#                 frame_list.append(tmp_gdf)
#             else: 
#                 pass
#             
#         samlet_populasjon = GeoDataFrame((pd.concat(frame_list, sort=False)), geometry='geometry')
#         
#         #samlet_populasjon.sort_values(['mmsi', 'start_time'])
#         tmp_list = []
#         for idx, row in unik_populasjon.iterrows():
#             
#             tmp_rows = samlet_populasjon.loc[(samlet_populasjon['mmsi'] == row['mmsi']) & (samlet_populasjon['start_time'] == row['start_time'])]
#             tmp_list.append(tmp_rows)
#         
#         skipsruter = GeoDataFrame(pd.concat(tmp_list, sort=False), geometry='geometry')
#         skipsruter.sort_values(['mmsi', 'start_time', 'crossing_time'])
#         
#         skipsruter['rutepunkt'] = skipsruter['rutepunkt'].map(lambda x: x.lstrip('Passline_'))
#         
#         rutetabell = skipsruter.groupby(['mmsi', 'start_time'])['rutepunkt'].apply(list)
#         
#         return rutetabell
#         #=====Betraktes som pseudikode from this point on i denne funksjonen=============
#         
#         rutetabell. reset_index/set_index/droplevel #for å fikse kolonnene er indekser i dag
#         
#         rute1_list = []
#         
#         if rutetabell['rutepunkt'].contains("ønsket rutevalg"):
#             rute1_list.append
#         #elif for sjekk av flere ruter
#         else:
#             pass
#         
#         rute_dataframe = pd.concat(rute1_list, sort=False)
#         