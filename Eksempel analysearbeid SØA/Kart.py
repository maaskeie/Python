# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 10:58:21 2018

@author: 5240
"""
from geopandas import GeoSeries
from matplotlib.collections import LineCollection
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from shapely.geometry import Point, LineString, MultiLineString
from descartes import PolygonPatch

class Kart(object):
    """
    En klasse for å håndtere plotting av kart i python. 
    """
    
    def __init__(self, omraade):
        
        self.xmin, self.ymin, self.xmax, self.ymax = omraade
            
        wms_url = "http://openwms.statkart.no/skwms1/wms.norges_grunnkart_graatone?version=1.3.0&request=GetMap&CRS=CRS:84&bbox="+str(self.xmin)+","+str(self.xmax)+","+str(self.ymin)+","+str(self.ymax)+"&styles=default&format=image/png"
        wms_layer = "Norges_grunnkart_graatone"
        
        self.figure = plt.figure(figsize=(20,20))
        self.ax = self.figure.add_subplot(1, 1, 1, projection= ccrs.PlateCarree())
        self.ax.add_wms(wms=wms_url, layers=wms_layer, cmap=None, transform=ccrs.Geodetic())
        self.ax.set_extent((self.xmin,self.xmax,self.ymin,self.ymax))
        
        self.point_color = '#FF0000'        #rød
        self.line_color = '#0040FF'         #grønn
        self.polygon_color = '#00FFBF'      #blå
        
        self.ax.set_title('Strekningsvise Tiltak', fontdict={'fontsize': 20, 'fontweight': 'medium'})

    
    def punkt_plot(self, punkter, alpha=None, color=None, size=10):
        
        x = punkter.x
        y = punkter.y
        
        
        if alpha == None:
            alpha = 0.5
        else:
            alpha = alpha
            
        
        if color == None:
            color = self.point_color     #rød, hentes fra __init__(), flere farger finnes på: www.javescripter.net/faq/rgbtohex.htm
        else:
            color = color
        
        size=size
        
        self.ax.scatter(x, y, color=color, alpha=alpha, s=size, marker='D', transform=ccrs.Geodetic())
        
        
        return self.ax


    def linje_plot(self, geometry, color=None, alpha=None, linewidth=1.0):
        
        if color == None:
            color = self.line_color
        else:
            color = color
            
        if alpha == None:
            alpha = 0.05
        else:
            alpha = alpha
            
        lines = []
        
        if type(geometry) == LineString:
            geometry = [geometry]
        elif type(geometry) == GeoSeries:
            geometry = geometry.values
        else:
            print('Ingen forståelig linjegeometri')
            return None
        
        for linje in geometry:
            if not type(linje) == LineString:
                for line in linje:
                    x, y = line.coords.xy
                    lines.append(list(zip(x, y)))
            else:
                x, y = linje.coords.xy
                lines.append(list(zip(x, y)))
                
        collection = LineCollection(lines, colors=color, alpha=alpha, transform=ccrs.PlateCarree(), linewidth=linewidth, label='Skipstrafikk')
        
        self.ax.add_collection(collection)
        
        return self.ax
    
    def area_plot(self, geometry, facecolor=None, alpha=None, edgecolor=None):
        
        geometry = list(geometry.values)
        
        if facecolor == None:
            facecolor = self.polygon_color
        else:
            facecolor = facecolor
        
        
        if alpha == None:
            alpha = 0.8
        else:
            alpha = alpha
        
        if edgecolor == None:
            edgecolor = '#000000'
        else:
            edgecolor = edgecolor
        
        if 'GeoAxesSubplot' in str(type(self.ax)):
            polies = []
            for geo in geometry:
                if geo.geom_type == 'MultiPolygon':
                    for pol in geo:
                        polies.append(pol)
                else:
                    polies.append(geo)
            self.ax.add_geometries(polies,
                                   ccrs.PlateCarree(),
                                   facecolor=facecolor,
                                   edgecolor=edgecolor,
                                   alpha=alpha,
                                   label='Utdypninger'
                                   )
        else:
            polies = []
            for geo in geometry:
                if geo.geom_type == 'MultiPolygon':
                    for pol in geo:
                        polies.append(PolygonPatch(pol, fc=facecolor, ec=None, alpha=alpha, label='Utdypning'))
                else:
                    polies.append(PolygonPatch(geo, fc=facecolor, ec=None, alpha=alpha, label='Utdypning'))

            for patch in polies:
                self.ax.add_patch(patch)

        if 'GeoAxesSubplot' not in str(type(self.ax)):
            self.ax.axis('scaled')
            self.ax.set_xlim([self.bounding_box[0], self.bounding_box[2]])
            self.ax.set_ylim([self.bounding_box[1], self.bounding_box[3]])

        return self.ax
    
    
    
    
    def tegnforklaring(self):
        
        utdypning_legend = mpatches.Patch(color=self.polygon_color)        
#        omrade_legend = mpatches.Patch(color=self.polygon_color, label='Tiltaksomraadet')
#        
        skipstrafikk_legend = mlines.Line2D([], [], color=self.line_color)
#        
        tiltakspunkt_legend = mlines.Line2D([0], [0], marker='D', markersize=10, color='white', markerfacecolor=self.point_color),
#        
#        legend_elements = [utdypning_legend, skipstrafikk_legend, tiltakspunkt_legend]
#        
#        plt.legend(handles=[legend_elements], loc='lower left')

        plt.legend(
                [utdypning_legend, skipstrafikk_legend, tiltakspunkt_legend], 
                ['Utdypning', 'Skipstrafikk', 'Tiltakspunkt'], 
                loc='lower right', 
                fancybox=True, 
                shadow=True,
                facecolor='#E8E8E8',
                edgecolor='#000000',
                title='Tegnforklaring',
                title_fontsize='large'
                )

        plt.show()
        
    
    def lagre(self, filepath):
        
        self.figure.savefig(filepath)
        print('Kartet er lagret under oppgitt filbane')
        