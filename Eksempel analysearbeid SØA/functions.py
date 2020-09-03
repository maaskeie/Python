from shapely.geometry import Point, LineString#, Polygon
import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
import pandas as pd
import numpy as np
from math import sin, cos, sqrt, atan2, radians
import math

#Returnerer minste området som mulig kan lages med en rektangel for å omslutte alle punktene
def bounding_box(geom):
    
    boks = tuple(geom.geometry.total_bounds)
    
    return boks

#Lger en linje av to shapely-punkter
def make_line(point1, point2):
    
    point1 = Point(point1)
    point2 = Point(point2)
    
    pass_line = GeoSeries(LineString([(point1), (point2)]))
    
    return pass_line

#Fungerer snevert og må lages mer anvendelig
#def make_polygon(points):
#    
#    lon_list = []
#    lat_list = []
#    
#    for point in points:
#        lon_list.append(point.x)
#        lat_list.append(point.y)
#    
#    polygon_geom = Polygon(zip(lon_list, lat_list))
#    crs = {'init': 'epsg:4326'}
#    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
#    
#    return polygon

    
def expand_box(boks, buffer):
    """
    buffer gir prosentandels økning basert på koordinatverdiene
    """
    
    decimal_percentage = buffer/100
    factor = decimal_percentage+1
    
    xmin, ymin, xmax, ymax = boks
    
    x_dist = xmax - xmin
    y_dist = ymax - ymin
    
    y_dist_new = factor*y_dist
    x_dist_new = factor*x_dist
    
    add_factor_x = x_dist_new/2
    add_factor_y = y_dist_new/2    
    
    tmp1 = float(boks[0])-add_factor_x
    tmp2 = float(boks[1])-add_factor_y
    tmp3 = float(boks[2])+add_factor_x
    tmp4 = float(boks[3])+add_factor_y
    ny_boks=(tmp1, tmp2, tmp3, tmp4)
    
    print('\nEkspandert boks har følgende form: '+str(ny_boks))
    
    return ny_boks

# Moderert Menon funksjon. Vist seg nyttig i kartproduksjon
def boks_forhold_sider(boks, ratio = 1.0):
    
    tmp_hoyde_ = (boks[3] - boks[1])
    tmp_bredde = (boks[2] - boks[0])
    tmp_ratio = tmp_bredde/tmp_hoyde_

    if tmp_ratio > ratio:  # Too broad, must heighten
        hoyde_senter = boks[1] + (boks[3] - boks[1])/2
        ny_hoyde = tmp_bredde / ratio
        ny_ymax = hoyde_senter + ny_hoyde/2
        ny_ymin = hoyde_senter - ny_hoyde/2

        ratio_boks = (boks[0], ny_ymin, boks[2], ny_ymax)

    elif tmp_ratio < ratio:  # Too high, must broaden
        bredde_senter = boks[0] + (boks[2] - boks[0])/2
        ny_bredde = tmp_hoyde_ * ratio
        ny_xmin = bredde_senter - ny_bredde/2
        ny_xmax = bredde_senter + ny_bredde/2

        ratio_boks = (ny_xmin, boks[1], ny_xmax, boks[3])

    return ratio_boks

def distance_points(point1, point2):
##Denne fremgangsmåten modellerer jorden som en sfære(Haversine method). Vincenty metoden til Geopy gir 0,5% bedre svar, men gir også kompleksitet mtp environment##
    
    point1 = Point(point1)
    point2 = Point(point2)
    
    earth_radius = 6371000 #jordens omkrets i meter
    
    lon1 = radians(point1.x)
    lat1 = radians(point1.y)
       
    lon2 = radians(point2.x)
    lat2 = radians(point2.y)
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
        
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    dist = earth_radius * c
        
    return dist


def hale_evaluering(prev_mmsi, current_mmsi, prev_sog, current_sog, prev_pos, current_pos, prev_time, current_time):
 
    if prev_mmsi == None and prev_sog == None and prev_pos == None and prev_time == None:
        tmp = 'Legg til'
        return tmp 
    
    dist_m = float(distance_points(current_pos, prev_pos))
    
    time_gap_seconds = float((current_time - prev_time).seconds)
    
    if time_gap_seconds == 0:
        time_gap_seconds = 0.1
    else: 
        pass
    
    speed_ms = float(dist_m/time_gap_seconds)
        
    
    if current_mmsi != prev_mmsi:   #Klipper hale om det er ny båt i lista
        tmp = 'Klipp'
        return tmp
    
    elif dist_m > 5000: 
                    #Klipper hale om det er mer enn 3km til forrige punkt
        tmp = 'Klipp'
        return tmp
    
    elif time_gap_seconds > 3600:   #Klipper hale om det er mer enn 1 timer til forrige punkt
        tmp = 'Klipp'
        return tmp
        
    elif speed_ms < 1.0:            #Ignorerer hale om farten kommer under 1m/s (3,6 km/t) i snitt siden forrige punkt
        tmp = 'Ignorer punkt'
        return tmp
    
    elif dist_m < 20:                #Ignorerer halen om avstanden er mindre enn 2m til forrige punkt
        tmp = 'Ignorer punkt'
        return tmp
    
    else:
        tmp = 'Legg til'                  #Ingen klippekriterier nådd, legges til og fortsetter til neste punkt i lista.
        return tmp
    
        
def lag_haler(points):
    
    #kolonneliste fra aisdata ['imo_nr', 'vessel_length', 'vessel_name', 'callsign', 'statcode5_fp', 'cog', 'true_heading', 'nav_status', 'dist_prevpoint', 'sec_prevpoint', 'calc_speed', 'message_nr']
    tmp_gdf = points#.loc[points.sog > 1]
    
    prev_mmsi, prev_imo, prev_callsign, prev_sog, prev_pos, prev_time, start_time, end_time = None, None, None, None, None, None, None, None
    
    #ønskede berikelseskolonner med statiske verdier må behandles som variablene under:
    #prev_imo, prev_vessel_length, prev_vessel_name, prev_callsign, prev_statcode5 = None, None, None, None, None   
    
    all_tracks = []
    single_track = []
    track_timestamp = []
    track_heading = []

    
    iterator = 1
    row_iterator = 0
    total_number = tmp_gdf.shape[0]
    tmp = ''
    
    print('\nstarter produksjon av haler:\n')
    
    for idx, row in tmp_gdf.sort_values(by=['mmsi', 'date_time_utc']).iterrows():
        row_iterator += 1
        current_mmsi = row['mmsi']
        current_imo = row['imo']
        current_callsign = row['callsign']
        current_sog = row['sog']
        current_pos = row['geom']
        current_time = row['date_time_utc']
        current_heading = row['true_heading']
        current_transponder = row['message_nr']
                
        tmp = hale_evaluering(prev_mmsi, current_mmsi, prev_sog, current_sog, prev_pos, current_pos, prev_time, current_time)

        if tmp == 'Legg til':
            single_track.append(current_pos)
            track_timestamp.append(current_time)
            track_heading.append(current_heading)
            
            if start_time == None:
                start_time = row['date_time_utc']
                    
        elif tmp == 'Klipp':
            if prev_time == None:
                end_time = row['date_time_utc']
                track_timestamp.append(current_time)
                track_heading.append(current_heading)
                
                
            else:
                end_time = prev_time
                track_timestamp.append(current_time)
                track_heading.append(current_heading)
                
            
            
                     
            all_tracks.append(dict(mmsi = prev_mmsi, imo = prev_imo, callsign = prev_callsign, start_time = start_time, end_time = end_time, times = track_timestamp.copy(), pass_heading = track_heading.copy(), transponder_type = current_transponder, track = single_track.copy())) 
            single_track = [current_pos]
            track_timestamp = [current_time]
            track_heading = [current_heading]
            start_time = row['date_time_utc']
            
            iterator +=1
            if iterator % 5000 == 0:
                print('\nProduserte haler så langt: '+str(iterator)+'\nBasert på avleste '+str(row_iterator)+' av '+str(total_number)+' rader')
        
        elif tmp == 'Ignorer punkt':
            current_mmsi, current_imo, current_callsign, current_sog, current_pos, current_time = prev_mmsi, prev_imo, prev_callsign, prev_sog, prev_pos, prev_time
        else:
            pass
            
            
        
        prev_mmsi, prev_imo, prev_callsign, prev_sog, prev_pos, prev_time = current_mmsi, current_imo, current_callsign, current_sog, current_pos, current_time
        
    
    
    all_tracks.append(dict(mmsi = prev_mmsi, imo = prev_imo, callsign = prev_callsign, start_time = start_time, end_time = prev_time, times = track_timestamp.copy(), pass_heading = track_heading.copy(), transponder_type = current_transponder, track = single_track.copy()))    
    haler = (pd.DataFrame(all_tracks).assign(num_points=lambda row: row['track'].map(len))).query('num_points >1').assign(geometry = lambda df:[LineString(el) for el in df['track']]).pipe(lambda x: gpd.GeoDataFrame(x, crs={'init':'epsg:4326'})).drop('track', axis=1).drop('num_points', axis=1)[['mmsi', 'imo', 'callsign', 'start_time', 'end_time', 'times', 'pass_heading', 'transponder_type', 'geometry']]
    haler.insert(0, 'tail_id', range(1, 1+len(haler)))

    print('\nFerdig med produksjon av '+str(iterator)+' haler!\n')   

    
    return haler


def write_csv(table, filepath):
    
    pd = table
    pd.to_csv(filepath, sep=';', index=False, mode='w')
    

def table_merge(table1, table2):
    #Utvis forsiktighet ved kombinering av flere tabeller. Sjekk at kolonner og rader endrer som ønsket
    
    columns_to_use = table2.columns.difference(table1.columns)
    
    merged_table = table1.merge(table2[columns_to_use], on='mmsi', left_index=True, right_index=True, how='left')
    
    return merged_table


def get_lengdegruppe(length):
    lengdegrupper = [(0, 'Missing_length'),
                        (30, "0-30"),
                        (70, "30-70"),
                        (100, "70-100"),
                        (150, "100-150"),
                        (200, "150-200"),
                        (250, "200-250"),
                        (300, "250-300"),
                        (1000, ">350")]
    
    {'0': '0-12'}
    
    try:
        length = float(length)
    except:
        return 'Missing_length'
    
    for verdi, gruppe in lengdegrupper:
        if length<=verdi:
            return gruppe
    return 'Missing_length'

#Funksjon benyttet for å finne hvilken dikotomisk inndeling som skip skal deles i over en linje
def line_bearing(line):
    
    if type(line)==LineString:
        pointA = line.coords[0]
        pointB = line.coords[1]
        
        lat1 = math.radians(pointA[0])
        lat2 = math.radians(pointB[0])
        
        difflong = math.radians(pointB[1] - pointA[1])
        
        x = math.sin(difflong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(difflong))
        
        tmp_bearing = math.atan2(x, y)
        tmp_bearing = math.degrees(tmp_bearing)
        bearing = (90 - tmp_bearing) % 360
        
        return bearing
   
    
    elif type(line)==GeoDataFrame:
        
        bearing_list = []
        line_nr = line.shape[0]
        
        for i in range(line_nr):
            
            tmp_pass_line = line.loc[i, 'geometry']
            
            pointA = tmp_pass_line.coords[0]
            pointB = tmp_pass_line.coords[1]
            
            lat1 = math.radians(pointA[0])
            lat2 = math.radians(pointB[0])
            
            difflong = math.radians(pointB[1] - pointA[1])
            
            x = math.sin(difflong) * math.cos(lat2)
            y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(difflong))
            
            tmp_bearing = math.atan2(x, y)
            tmp_bearing = math.degrees(tmp_bearing)
            bearing = (90 - tmp_bearing) % 360
            bearing_list.append(bearing)
        return bearing_list    

#Funksjon som returnerer en endret gradering mellom representasjonene -180 <-> 180 til 0 <-> 360
def passline_limits(passline_angle):
    
    if (passline_angle <= 45 and passline_angle >= 0) or (passline_angle >= 315 and passline_angle < 360) or (passline_angle >= 135 and passline_angle <= 225):
        
        #Setter trafikkretning
        trafikk_retning = 'Ost/Vest'
                
        if (passline_angle <= 45 and passline_angle >= 0):
            
            limit1 = passline_angle
            limit2 = passline_angle + 180
        
        elif (passline_angle >= 315 and passline_angle <= 360):
            
            limit1 = passline_angle - 180
            limit2 = passline_angle
            
        elif (passline_angle <= 225 and passline_angle >= 180):
            
            limit1 = passline_angle - 180
            limit2 = passline_angle
            
        elif (passline_angle < 180 and passline_angle >= 135):
            
            limit1 = passline_angle
            limit2 = passline_angle + 180
            
        else:
            limit1 = 0
            limit2 = 180
            
    #Fra 45 til 135 samt fra 225 til 315 indikerer en passeringslinje orintert Øst/Vest som vil dele trafikken inn i nord/syd
    elif (passline_angle > 45 and passline_angle < 135) or (passline_angle > 225 and passline_angle < 315):
        
        #Setter trafikkretning
        trafikk_retning = 'Nord/Syd'
        
        if (passline_angle > 45 and passline_angle < 135):
            
            limit1 = passline_angle
            limit2 = passline_angle + 180
            
        elif (passline_angle < 135 and passline_angle > 225):
            
            limit1 = passline_angle - 180
            limit2 = passline_angle
            
        else:
            limit1 = 90
            limit2 = 270
            
    
    return limit1, limit2, trafikk_retning



def seilingstid(hale_df, tellelinje1, tellelinje2, returner_hale_index=False):
    """
    MODIFISERT MENON-KODE
    Klipper alle haler i hale_df som passerer både tellelinje 1 og 2 og
    returnerer segmentene som ligger mellom, samt tilhørende seilingstid brukt
    mellom linjene, lengde på seilasen mellom linjene i m og gjennomsnittlig
    hastighet i m/s.

    Funksjonen er så lang som den er for å håndtere edge-cases som i stor grad
    resulterer av at shapely.split() har en bug ved selv-kryssende linjer. Om
    denne skulle bli fikset så kan funksjonen potensielt skrives om.

    Input:
    hale_df:                pandas dataframe med haler
    tellelinje 1/2:         i vilkårlig rekkefølge, shapely geometrier
    returner_hale_index:    hvis True, returnerer en liste indexer av samme
                            lengde som klipp-outputen som korresponderer til
                            halene brukt i hvert av klippene.

    Output:
    klipp_df:               pandas dataframe som inneholder klippene
    [hale_indices]:         liste med indexer (se returner_hale_index)


    ADVARSEL: behandler kun ca. 50 haler i sekundet
    """

    #projeksjonen antar at input er en epsg:4326-projeksjon, som er standard for geosatelittdata
    #denne brukes for å regne om klippenes lengde fra epsg:4326-koordinater til nautiske mil
    #projeksjon = partial(pyproj.transform,
                         #pyproj.Proj(init='epsg:4326'),
                         #pyproj.Proj(init='epsg:32632'))

    klipp_df = gpd.GeoDataFrame()
    #hvis returner_hale_index er True vil denne fylles med indexer fra hale_df korresponderende til klippene i klipp_df
    hale_indices = []
    
    
    #iterer over haler
    for idx, hale_serie in hale_df.iterrows():
        hale = hale_serie.geometry
        hale_punkter = [Point(p) for p in hale.coords]

        #sjekker først om halen krysser begge tellelinjene
        if hale.intersects(tellelinje1) and hale.intersects(tellelinje2):

            #henter ut punktene der halen og tellelinjene krysser
            intersect_punkter_1 = hale.intersection(tellelinje1)
            intersect_punkter_2 = hale.intersection(tellelinje2)


            #dersom det kun finnes ett krysningspunkt per tellelinje puttes det i en liste for å funke i for-loopen senere
            if isinstance(intersect_punkter_1,Point):
                intersect_punkter_1 = [intersect_punkter_1]
            elif isinstance(intersect_punkter_1,LineString): #for aa vaere kompatibel med polygoner
                intersect_punkter_1 = [Point(p) for p in intersect_punkter_1.coords]
            elif isinstance(intersect_punkter_1[0],LineString): #for aa vaere kompatibel med polygoner
                temp = []
                for l in intersect_punkter_1:
                    temp.extend([Point(p) for p in l.coords])
                intersect_punkter_1 = temp

            if isinstance(intersect_punkter_2,Point):
                intersect_punkter_2 = [intersect_punkter_2]
            elif isinstance(intersect_punkter_2,LineString): #for aa vaere kompatibel med polygoner
                intersect_punkter_2 = [Point(p) for p in intersect_punkter_2.coords]
            elif isinstance(intersect_punkter_2[0],LineString): #for aa vaere kompatibel med polygoner
                temp = []
                for l in intersect_punkter_2:
                    temp.extend([Point(p) for p in l.coords])
                intersect_punkter_2 = temp

            intersect_idx_1 = []
            intersect_idx_2 = []
            intersect_time_1 = []
            intersect_time_2 = []

            #spar på punktene der halen krysser tellelinjene så de kan legges inn i klippet
            krysningspunkter_1 = []
            krysningspunkter_2 = []

            #iterer over krysningspunktene
            for punkt in intersect_punkter_1:

                #regn ut avstander fra hvert punkt i halen til krysningspunktene
                #(kan effektiviseres ved å filtrere ut hale-punkter utenfor loopen)
                point_distances = np.array([hale_punkt.distance(punkt) for hale_punkt in hale_punkter])

                #henter lokale minimum i avstand for å finne potensielle krysningspunkter.
                #NB: antar at halen ikke begynner eller slutter på et krysningspunkt
                local_minima = np.where(np.r_[True, point_distances[1:] <= point_distances[:-1]] &
                                        np.r_[point_distances[:-1] <= point_distances[1:], True])[0]

                #iterer over de potensielle krysningspunktene
                for minima in local_minima:
                    #hent avstand til forrige og neste punkt
                    linje_bak, linje_frem = None, None

                    if minima > 0:
                        linje_bak = LineString([hale_punkter[minima],hale_punkter[minima-1]]).buffer(0.0001)
                    if minima < len(hale_punkter) - 1:
                        linje_frem = LineString([hale_punkter[minima],hale_punkter[minima+1]]).buffer(0.0001)

                    if linje_bak is not None and linje_bak.contains(punkt):
                        #legger til indexen til det nærmeste hale-punktet til krysningspunktet
                        #(tiden hentes ut her fordi det tillater inerpolering,
                        #men for øyeblikket støttes ikke dette)
                        intersect_idx_1.append(minima)
                        krysningspunkter_1.append(punkt)
                        weight = point_distances[minima-1] / hale_punkter[minima-1].distance(hale_punkter[minima])
                        intersect_time_1.append(hale_serie.times[minima-1] + ((hale_serie.times[minima] -
                                                                                hale_serie.times[minima-1]) * weight))
                    elif linje_frem is not None and linje_frem.contains(punkt):
                        #krysning funnet
                        intersect_idx_1.append(minima)
                        krysningspunkter_1.append(punkt)
                        weight = point_distances[minima] / hale_punkter[minima].distance(hale_punkter[minima+1])
                        intersect_time_1.append(hale_serie.times[minima] + ((hale_serie.times[minima+1] -
                                                                                hale_serie.times[minima]) * weight))

            #se kommentarer for intersect_punkter_1
            for punkt in intersect_punkter_2:

                point_distances = np.array([hale_punkt.distance(punkt) for hale_punkt in hale_punkter])
                local_minima = np.where(np.r_[True, point_distances[1:] <= point_distances[:-1]]
                                        & np.r_[point_distances[:-1] <= point_distances[1:], True])[0]

                for minima in local_minima:

                    linje_bak, linje_frem = None, None

                    if minima > 0:
                        linje_bak = LineString([hale_punkter[minima],hale_punkter[minima-1]]).buffer(0.01)
                    if minima < len(hale_punkter) - 1:
                        linje_frem = LineString([hale_punkter[minima],hale_punkter[minima+1]]).buffer(0.01)

                    if linje_bak is not None and linje_bak.contains(punkt):
                        intersect_idx_2.append(minima)
                        krysningspunkter_2.append(punkt)
                        weight = point_distances[minima-1] / hale_punkter[minima-1].distance(hale_punkter[minima])
                        intersect_time_2.append(hale_serie.times[minima-1] + ((hale_serie.times[minima] -
                                                                                hale_serie.times[minima-1]) * weight))


                    elif linje_frem is not None and linje_frem.contains(punkt):
                        intersect_idx_2.append(minima)
                        krysningspunkter_2.append(punkt)
                        weight = point_distances[minima] / hale_punkter[minima].distance(hale_punkter[minima+1])
                        intersect_time_2.append(hale_serie.times[minima] + ((hale_serie.times[minima+1] -
                                                                                hale_serie.times[minima]) * weight))



            #henter ut de unike hale-punkt-indexene
            unq1, unq_idx1 = np.unique(intersect_idx_1, return_index=True)
            unq2, unq_idx2 = np.unique(intersect_idx_2, return_index=True)

            intersect_idx_1 = unq1
            intersect_idx_2 = unq2

            krysningspunkter_1 = [krysningspunkter_1[u] for u in unq_idx1]
            krysningspunkter_2 = [krysningspunkter_2[u] for u in unq_idx2]

            #henter ut de tilsvarende hale-tid indexene
            intersect_time_1 = np.array(intersect_time_1)[unq_idx1]
            intersect_time_2 = np.array(intersect_time_2)[unq_idx2]

            #i tilfelle punktene ikke er sortert etter tid
            time_sort_idx_1 = np.argsort(intersect_time_1)
            time_sort_idx_2 = np.argsort(intersect_time_2)

            #sorterer etter tid
            intersect_idx_1 = list(intersect_idx_1[time_sort_idx_1])
            intersect_idx_2 = list(intersect_idx_2[time_sort_idx_2])

            intersect_time_1 = list(intersect_time_1[time_sort_idx_1])
            intersect_time_2 = list(intersect_time_2[time_sort_idx_2])

            krysningspunkter_1 = [krysningspunkter_1[t] for t in time_sort_idx_1]
            krysningspunkter_2 = [krysningspunkter_2[t] for t in time_sort_idx_2]


            #iterer over krysningspunktene og hent ut krysningsparene.
            #lag så en dataframe av geometri, tidspunkter, utregnet avstand
            #samt hastighet.

            while len(intersect_idx_1) > 0 and len(intersect_idx_2) > 0:
                start_idx = None
                slutt_idx = None
                klipp_start = None
                klipp_slutt = None
                hale_klippet = None
                foerste_kryss = None

                if intersect_idx_1[0] < intersect_idx_2[0]:

                    if len(intersect_idx_1) > 1 and intersect_idx_1[1] < intersect_idx_2[0]:
                        krysningspunkter_1 = krysningspunkter_1[1:]
                        intersect_idx_1 = intersect_idx_1[1:]
                        intersect_time_1 = intersect_time_1[1:]

                    else:
                        start_idx = intersect_idx_1[0]
                        slutt_idx = intersect_idx_2[0]

                        klipp_start = intersect_time_1[0]
                        klipp_slutt = intersect_time_2[0]


                        foerste_kryss = 1
                        krysningspunkter_1 = krysningspunkter_1[1:]
                        krysningspunkter_2 = krysningspunkter_2[1:]

                        intersect_idx_1 = intersect_idx_1[1:]
                        intersect_idx_2 = intersect_idx_2[1:]

                        intersect_time_1 = intersect_time_1[1:]
                        intersect_time_2 = intersect_time_2[1:]


                else:

                    if len(intersect_idx_2) > 1 and intersect_idx_2[1] < intersect_idx_1[0]:
                        krysningspunkter_2 = krysningspunkter_2[1:]
                        intersect_idx_2 = intersect_idx_2[1:]
                        intersect_time_2 = intersect_time_2[1:]

                    else:
                        start_idx = intersect_idx_2[0]
                        slutt_idx = intersect_idx_1[0]

                        intersect_idx_2 = intersect_idx_2[1:]
                        intersect_idx_1 = intersect_idx_1[1:]

                        klipp_start = intersect_time_2[0]
                        klipp_slutt = intersect_time_1[0]

                        intersect_time_2 = intersect_time_2[1:]
                        intersect_time_1 = intersect_time_1[1:]


                        foerste_kryss = 2
                        krysningspunkter_1 = krysningspunkter_1[1:]
                        krysningspunkter_2 = krysningspunkter_2[1:]



                if slutt_idx is None or slutt_idx - start_idx <= 1:
                    continue

                hale_klippet = LineString(
                                          hale_punkter[start_idx:slutt_idx]
                                          )
                lengde = distance_points(hale_punkter[start_idx], hale_punkter[slutt_idx]) * 1000 #metrisk meter

                tid_brukt = (klipp_slutt - klipp_start).total_seconds()

                klipp_df = klipp_df.append(gpd.GeoDataFrame([[hale_serie.mmsi, klipp_start, klipp_slutt,
                                                             lengde, lengde / tid_brukt,
                                                             foerste_kryss, hale_klippet]],
                            columns=['mmsi','start_tid','slutt_tid','lengde','obs_speed','første_linje_krysset','geometry'], geometry='geometry'))

                if returner_hale_index:
                    hale_indices.append(idx)

    if klipp_df.shape[0] > 0:
        klipp_df = klipp_df.set_geometry('geometry')

    if returner_hale_index:
        return klipp_df, hale_indices

    return klipp_df


