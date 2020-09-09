#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import IPython

pd.set_option('display.max_columns', 50)
# Laster inn excelfil med årlig vekst i tonnkm fra Transportytelser 2018.
tkm_v = pd.read_csv("C:/Users/33849/Documents/Python/Prognoser/Grunnlagsdata/vekst i tranpsortytelser_2010_2018.csv", sep=";")
tkm_v['vekst'] = tkm_v ['vekst']/100
tkm_v.head(15)


# Laster inn skipspopulasjoen for 2019. Filen kobles til dataene på utseilt distanse for å kategorisere skipstypene på grovere kategorier. 
df_skips_pop19 = pd.read_excel('C:/Users/33849/Documents/Python/Prognoser/Grunnlagsdata/skips_pop_2019.xlsx')
df_skips_pop19.head()
df_skips_pop19.count()
list(df_skips_pop19.columns) 

df_skips_pop19['statcode_kort']=df_skips_pop19['statcode5'].astype(str).str[0:3]
df_skips_pop19.head()

df_pop19 = df_skips_pop19.drop(columns = ['mmsi', 'callsign', 'imo', 'vessel_name'], axis = 1)
df_pop19.head()

pop19 = df_pop19.groupby('statcode_kort').apply(lambda x: x['skipstype_label'].unique())
pop19.head(30)


# Innlasting av excelfiler med utseilt distanse. Filene er lastet ned fra nettsiden havbase.no. Dataene dekker årene 2011 til 2019. 
df = pd.concat(map(pd.read_excel, glob.glob(os.path.join('', "C:/Python/UD/Grunnlagsdata/20*.xlsx"))))

df['year'] = df['ar']

#df['statcode_kort'] = df['ID']
df.head()
df.tail(30)

# Setter sammen filene for skipspopulasjon og data på utseilt distanse. Dette for å kunne aggregere utseilt distanse etter ulike skipskategoriseringer. 
df_pop = pd.merge(df, df_skips_pop19 ,how ='left', left_on='ID', right_on = 'statcode_kort') #bør utvide merge slik at jeg bruker ringt og left og slipper å lage kolonnen statcode_kort
df_pop.head()

df_pop.drop_duplicates(subset=('ID', 'Sum'), inplace = True)

df_pop.skipstype_label.value_counts()
#df_pop.skipstype.value_counts()

#Laster inn data for ankomster til Norge 2010 - 2019. Dataene er lastet ned fra Kystdatahuset. 
df_ankomst = pd.concat(map(pd.read_excel, glob.glob(os.path.join('', "G:/3_TPU/TPU/cedric_temp/ankomster/ankoms*.xlsx"))))
df_ankomst['ar'] = df_ankomst['År']
df_ankomst.shape
df_ankomst['Ankomster'].value_counts()

df_ankomst.head()
df_ankomst.Skipskategori.value_counts()

#filterer ankomster for kun å inneholde godsfartøy. 
skipstype_ank_gods = ['Stykkgodsskip', 'Bulkskip', 'Kjemikalie-/oljetankskip', 'Andre lasteskip',
                      'Offshore supply/support skip', 'Ro-Ro-lasteskip', 'Gasstankskip', 'Konteinerskip']
df_ank_gods = df_ankomst[df_ankomst['Skipskategori'].isin(skipstype_ank_gods)]
df_ank_gods.head()
df_ank_gods.Skipskategori.value_counts()
#******************************************************************************
#Grupperer alle ankomster etter år
ankomst_grp = df_ankomst.groupby(['År'])
ankomst_grp.head(20)

df_ank_tot = pd.pivot_table(df_ankomst, values = 'Ankomster', index = 'ar', aggfunc=np.sum) 
#df_ank_tot['ar'] = df_ank_tot.index
df_ank_tot.head(20)

df_ud_tot = pd.pivot_table(df_pop, values = ('Sum'), index= 'ar', aggfunc=np.sum)
df_ud_tot.head(20)

#******************************************************************************
#Summerer ankomster etter år, kun godsfartøy
ankomst_grp = df_ankomst.groupby(['ar'])
ankomst_grp.head(20)
#df_ank_tot = ankomst_grp['Ankomster'].agg('sum')
#df_ank_tot.head(11)


ank_tot_gods = pd.pivot_table(df_ank_gods, values = 'Ankomster', index = 'ar', aggfunc=np.sum)
#ank_tot_gods['ar'] =ank_tot_gods.index
ank_tot_gods.head(20)

#******************************************************************************
#Filterere data på utseilt distanse for å lage datasett for godsfartøy
df_pop.groupby(['year'])

skipstype_gods = ['Stykkgods/roro-skip', 'Bulkskip', 'Kjemikalie-/produkttankskip', 'Oljetankskip', 'Offshore supply skip'
                  'Gasstankskip', 'Konteinerskip', 'Brønnbåt']

df_pop1 = df_pop[df_pop['skipstype_label'].isin(skipstype_gods)]
df_pop1.head(20)
df_pop1.Skipstype.value_counts()

df_ud_gods = pd.pivot_table(df_pop1, values = 'Sum', index = 'ar', aggfunc=np.sum)
df_ud_gods.head(12)

#******************************************************************************
#Setter sammen data for utseilt distanse og for ankomster, alle fartøy. 
df_ank_tot.head()
#df_ank_tot['År']=df_ank_tot['ar']
df_ud_tot.head()
df_ud_tot.columns

df_ud_ank = pd.merge(df_ud_tot, df_ank_tot, how = 'right', left_on='ar', right_on = 'ar')
df_ud_ank.head()

df_ud_ank.sort_values(by=['ar'], inplace = True)
#df_ud_ank['ar'] = df_ud_ank['year']
#df_ud_ank.head(20)
#******************************************************************************
#Setter sammen data for utseilt distanse og ankomster for godsfartøy. 
ank_tot_gods.head(10)
ank_tot_gods.reset_index(inplace=True)
#ank_tot_gods.drop(columns='ar', inplace=True)

df_ud_gods.head(10)
df_ud_gods.columns

df_gods = pd.merge(df_ud_gods, ank_tot_gods, how = 'right', left_on='ar', right_on = 'ar')
#df_gods.reset_index(inplace=True)
df_gods.head(15)


df_gods.sort_values(by=['ar'], inplace = True)

ank_tot_gods.head(10)
#******************************************************************************
#Pivot som gir en tabell der ud summeres over år og skipstyper. 
#df_ud_ank.to_excel("C:/Python/UD/Grunnlagsdata/ud_ank.xlsx") 
#ank_tot_gods.to_excel("C:/Python/UD/Grunnlagsdata/ank_tot_god.xlsx") 
#df_pop.to_excel("C:/Python/UD/Grunnlagsdata/df_pop.xlsx") 
df_ud_ank.reset_index(inplace=True)
df_ud_ank.head()


#df_gods.reset_index(inplace=True)
df_gods.head()

#******************************************************************************
# create figure and axis objects with subplots()
formatter = ticker.FormatStrFormatter('nm%1000 000f')

#******************************************************************************
#Figur som viser utvikling i utseilt distanse og ankomster til norske havner for årene 2011 til 2019. 
# create figure and axis objects with subplots()
fig,ax = plt.subplots(figsize=(15, 12))
# make a plot
lns1 = ax.plot(df_ud_ank.ar, df_ud_ank.Sum, color="red", marker="o", label='Utseilt distanse, alle')
lns2 = ax.plot(df_gods.ar, df_gods.Sum, color="orange", marker="o", label ='Utseilt distanse, godsfartøy')
# set x-axis label
ax.set_xlabel("År",fontsize=14)
# set y-axis label
ax.set_ylabel("Utseilt distanse (nm)",color="red",fontsize=14)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
plt.title('Utvikling i utseilt distanse og ankomster for årene 2011 til 2019')
plt.grid()
# twin object for two different y-axis on the sample plot
ax2=ax.twinx()

# make a plot with different y-axis using second axis object
lns3 = ax2.plot(df_ud_ank.ar, df_ud_ank.Ankomster ,color="blue" ,marker="o", label='Ankomster, alle')
lns4 = ax2.plot(df_gods.ar, df_gods.Ankomster ,color="green" ,marker="o", label='Ankomster, godsfartøy')
ax2.set_ylabel("Ankomster",color="blue",fontsize=14)
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
#ax.legend(loc=0)
#ax2.legend(loc=1)
lns = lns1+lns2+lns3+lns4
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=0)

plt.show()

#******************************************************************************
#Figur som viser utvikling kun for godsfartøy på utseilt distanse og ankomster for årene 2011 til 2019. 
#fig,ax = plt.subplots(figsize=(15, 9))
## make a plot
#ax.plot(df_gods.ar, df_gods.Sum, color="red", marker="o")
## set x-axis label
#ax.set_xlabel("År",fontsize=14)
## set y-axis label
#ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
#ax.set_ylabel("Utseilt distanse (nm)",color="red",fontsize=14)
#plt.title('Utvikling i utseilt distanse og ankomster for godsfartøy for årene 2010 til 2019')
## twin object for two different y-axis on the sample plot
#ax2=ax.twinx()
## make a plot with different y-axis using second axis object
#ax2.plot(df_gods.ar, df_gods.Ankomster ,color="blue" ,marker="o")
#ax2.set_ylabel("Ankomster",color="blue",fontsize=14)
#ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
#plt.show()

df_ud_ank.head()
df_piv = df_ud_ank.pivot_table(columns = 'ar', values=['Ankomster', 'Sum'])
df_piv.head(11)

df_piv.reset_index(inplace = True)

df_piv.columns
df_piv.dtypes


#
#df_piv['2011v'] = 1
#df_piv['2012v'] = df_piv.iloc[[0,1],9] +(df_piv.iloc[[0,1],9] * ((df_piv.iloc[[0,1],1] - df_piv.iloc[[0,1],0])/df_piv.iloc[[0,1],0]))
#df_piv['2013v'] = df_piv.iloc[[0,1],10] +(df_piv.iloc[[0,1],10] * ((df_piv.iloc[[0,1],2] - df_piv.iloc[[0,1],1])/df_piv.iloc[[0,1],1]))
#df_piv['2014v'] = df_piv.iloc[[0,1],11] +(df_piv.iloc[[0,1],11] * ((df_piv.iloc[[0,1],3] - df_piv.iloc[[0,1],2])/df_piv.iloc[[0,1],2]))
#df_piv['2015v'] = df_piv.iloc[[0,1],12] +(df_piv.iloc[[0,1],12] * ((df_piv.iloc[[0,1],4] - df_piv.iloc[[0,1],3])/df_piv.iloc[[0,1],3]))
#df_piv['2016v'] = df_piv.iloc[[0,1],13] +(df_piv.iloc[[0,1],13] * ((df_piv.iloc[[0,1],5] - df_piv.iloc[[0,1],4])/df_piv.iloc[[0,1],4]))
#df_piv['2017v'] = df_piv.iloc[[0,1],14] +(df_piv.iloc[[0,1],14] * ((df_piv.iloc[[0,1],6] - df_piv.iloc[[0,1],5])/df_piv.iloc[[0,1],5]))
#df_piv['2018v'] = df_piv.iloc[[0,1],15] +(df_piv.iloc[[0,1],15] * ((df_piv.iloc[[0,1],7] - df_piv.iloc[[0,1],6])/df_piv.iloc[[0,1],6]))
#df_piv['2019v'] = df_piv.iloc[[0,1],16] +(df_piv.iloc[[0,1],16] * ((df_piv.iloc[[0,1],8] - df_piv.iloc[[0,1],7])/df_piv.iloc[[0,1],7]))


df_ud_ank.set_index('ar')

df_pct = df_ud_ank.pct_change()
df_pct.set_index(pd.Index([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]), inplace = True)
df_pct['year'] = df_pct.index
df_pct
df_v = pd.merge(df_pct, tkm_v, how = 'left', left_on= 'year', right_on = 'year')
df_v.head(15)


fig,ax = plt.subplots(figsize=(15, 9))
# make a plot
ax.plot(df_v.year, df_v.Sum, color="red", marker="o", label='Utseilt distanse')
ax.plot(df_v.year, df_v.Ankomster, color="blue", marker="o")
ax.plot(df_v.year, df_v.vekst, color="green", marker="o", label='tonnkm')
# set x-axis label
ax.set_xlabel("År",fontsize=14)
# set y-axis label
ax.legend()
ax.set_ylabel("Prosentvis endring", fontsize=14)
plt.title('Vekst i utseilt distanse, ankomster og tonnkm for årene 2010 til 2019 (prosent)', fontsize=16)
#

fig,ax = plt.subplots(figsize=(15, 9))
# make a plot
ax.plot(df_v.year, df_v.Sum, color="red", label='Utseilt distanse')
ax.plot(df_v.year, df_v.Ankomster, color="blue")
ax.plot(df_v.year, df_v.vekst, color="green", label='tonnkm')
# set x-axis label
ax.set_xlabel("År",fontsize=14)
# set y-axis label
ax.legend()
ax.set_ylabel("Prosentvisendring", fontsize=14)
plt.title('Vekst i utseilt distanse, ankomster og tonnkm for årene 2010 til 2019 (prosent)', fontsize=16)
#

#Visulaisere endring i ankomster og utseilt distanse etter skipskategorier og størrelser

# Laster inn skipspopulasjoen for 2019. 
#Filen kobles til mapping av statcode koder og navn for å kunne mappe til data fra Kystdatahuset.  
df_skips_pop19 = pd.read_excel('C:/Python/UD/Grunnlagsdata/statcode5.xlsx')
df_skips_pop19['statcode_kort']=df_skips_pop19['statcode5'].astype(str).str[0:3]
df_skips_pop19.head()

#laster inn data som gjør det mulig å mappe basert på skipkategorinavn og statcode
skips_pop = pd.read_excel('C:/Python/UD/Grunnlagsdata/skips_pop.xls')
skips_pop.head()

kyv_data_pop = pd.read_excel('C:/Python/UD/Grunnlagsdata/Kystdatahuset mapping skipskategori skipsgruppe og skipstype statcode5 pr 01.xlsx')
kyv_data_pop.head()

df_pop = pd.merge(df_skips_pop19, skips_pop, how = 'left', left_on= 'statcode5', right_on = 'statcode5')
df_pop.head()

df_pop1 = pd.merge(df_pop, kyv_data_pop, how = 'left', left_on= 'l5name_reg', right_on = 'l5name_reg')
df_pop1.head()

df_pop1.columns

df.head()

#Data på utseilt distanse kobles med skipsrregistrene. 
merge_ud = pd.merge(df, df_pop1, how='left', left_on='ID', right_on='statcode3')
merge_ud.head()



ud_test = pd.pivot_table(merge_ud, ('Sum'),['Skipskategori', 'year'])
ud_test.head()


ud_test1 = ud_test.reset_index()
ud_test1.head()

table = pd.pivot_table(ud_test1, values='Sum', index = ['year'], columns=['Skipskategori'], aggfunc=np.sum)
table.head()
table.columns

table.rename(columns={'Offshorefartøy og spesialfartøy':'Offshorefartøy_og_spesialfartøy'}, inplace = True)
table.columns

table1 = table.reset_index()
table1.head()

#plt.plot(table)
#

fig,ax = plt.subplots(figsize=(15, 15))
# make a plot
ax.plot(table.Fiskefartøy, color="b", label='Fiskefartøy')
ax.plot(table.Passasjerskip, color="y", label='Passasjerskip')
ax.plot(table.Tankskip, color="brown", label='Tankskip')
ax.plot(table.Lasteskip, color="g", label='Lasteskip')
ax.plot(table.Offshorefartøy_og_spesialfartøy, color="k", label='Offshorefartøy og spesialfartøy')
#ax.plot(ud_test1.year, ud_test1.Skipskategori, color="blue")
# set x-axis label
ax.set_xlabel("År",fontsize=14)
# set y-axis label
ax.legend()
ax.set_ylabel("Utseilt distanse (nm)", fontsize=14)
plt.title('Utseilt distanse 2011 til 2019 (nm)', fontsize=16)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
plt.grid(True)
#



#df_pop.sort_values(by=['Skipstype'],inplace=True, ascending=True)
#df_pop.head(20)

#df_sum_ar = df_pop.groupby(['ID', 'Skipstype', 'ar'])['< 1000 GT', '1000 - 4999 GT', '5000 - 9999 GT', '10000 - 24999', '25000 - 49999', '50000 - 99999', '>= 100000','Sum'].sum()
#df_sum_ar.head(40)

#df_sum_ar['sum_v'] = df_sum_ar.pct_change('Sum')


#************************************************
#Pivot som gir en tabell der ud summeres over år og skipstyper. 
#df_pivot_sum = pd.pivot_table(df_pop, ( '< 1000 GT', '1000 - 4999 GT', '5000 - 9999 GT', '10000 - 24999', '25000 - 49999', '50000 - 99999', '>= 100000','Sum'),['skipstype_agg'], 'År')
#print(df_pivot_sum)
#df_pivot_sum.to_excel("C:/Python/UD/Grunnlagsdata/ud_pr_ar.xlsx") 

#print(df_v)
#df_v.to_excel("C:/Python/UD/Grunnlagsdata/vekst_ar.xlsx") 

#df_sum = df_pivot_sum.filter(like='Sum', axis=1)
#df_sum.head(30)

#labels = ud_test1['year']
#skipskategori = ud_test1['Skipskategori']
#utseilt_distanse = ud_test1['Sum']
#
#fig, ax = plt.subplots(skipskategori, label='Skipskategori')
#
#rects1 = ax.plot(skipskategori, label='Skipskategori')
#rects2 = ax.plot(utseilt_distanse, label='Utseilt distanse')
##
#[‎09.‎06.‎2020 14:49]  Øystein Linnestad:  
#start = '2019-01-01'
#end = '2019-12-31'
#
#db = DataBase(start, end)
#havbase = db.havbase()
#havbase.to_pickle("C:\filsti.pkl") 
#

#******************************************************************************
#Tonnkm etter skipskategorier, dataene er hentet fra https://www.toi.no/getfile.php?mmfileid=51191

tonnkm_skipskat = pd.read_excel(r'C:/Python/UD/Grunnlagsdata/tonnkm etter skipstyper.xlsx')
tonnkm_skipskat.head(15)
tonnkm_skipskat.rename(columns={"Skipstyper":"ar"}, inplace= True)

#tonnkm_gods = tonnkm_skipskat.drop(columns=("Andre aktiviteter", "Andre offshore service skip", "Fiske- og fangstfartøy", "Ukjent"))
#tonnkm_gods= tonnkm_skipskat[tonnkm_skipskat['skipstype_label'].isin(skipstype_gods)]

#df_pop1 = df_pop[df_pop['skipstype_label'].isin(skipstype_gods)]



fig,ax = plt.subplots(figsize=(15, 12))
# make a plot
lns1 = ax.plot(df_ud_ank.ar, df_ud_ank.Sum, color="red", marker="o", label='Utseilt distanse, alle')
lns2 = ax.plot(df_gods.ar, df_gods.Sum, color="orange", marker="o", label ='Utseilt distanse, godsfartøy')
# set x-axis label
ax.set_xlabel("År",fontsize=14)
# set y-axis label
ax.set_ylabel("Utseilt distanse (nm)",color="red",fontsize=14)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
plt.title('Utvikling i utseilt distanse og tonnkm for årene 2010 til 2019')
plt.grid()
# twin object for two different y-axis on the sample plot
ax2=ax.twinx()

# make a plot with different y-axis using second axis object
lns3 = ax2.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Total ,color="blue" ,marker="o", label='Tonnkm, alle')
#lns4 = ax2.plot(df_gods.ar, df_gods.Ankomster ,color="green" ,marker="o", label='Ankomster, godsfartøy')
ax2.set_ylabel("Tonnkm (millioner)",color="blue",fontsize=14)
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
#ax.legend(loc=0)
#ax2.legend(loc=1)
lns = lns1+lns2+lns3
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=0)

plt.show()

tonnkm_skipskat.rename(columns={"Fiske- og fangstfartøy":"Fiskefangstfartøy", "Kjemikalie-/produkttankere":"Kjemikalieprodukttankere", 
                            "Kjøle-/fryseskip":"Reefer", "Offshore-supplyskip":"Offshoresupply", "Ro-Ro-last":"RoRolast" }, inplace= True)

fig,ax = plt.subplots(figsize=(15, 12))
# make a plot
#lns1 = ax.plot(df_ud_ank.ar, df_ud_ank.Sum, color="red", marker="o", label='Utseilt distanse, alle')
#lns2 = ax.plot(df_gods.ar, df_gods.Sum, color="orange", marker="o", label ='Utseilt distanse, godsfartøy')
# set x-axis label
ax.set_xlabel("År",fontsize=14)
# set y-axis label
#ax.set_ylabel("Utseilt distanse (nm)",color="red",fontsize=14)
#ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
plt.title('Utvikling tonnkm for årene 2010 til 2018')
plt.grid()
# twin object for two different y-axis on the sample plot
#ax2=ax.twinx()

# make a plot with different y-axis using second axis object
lns1 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Total ,color="blue" ,marker="o", label='Tonnkm, alle')
lns2 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Bulkskip ,color="brown" ,marker="o", label='Bulkskip')
lns3 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Gasstankskip ,color="pink" ,marker="o", label='Gasstankskip')
lns4 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Kjemikalieprodukttankere ,color="black" ,marker="o", label='Kjemikalie-/produkttankere')
lns5 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.RoRolast ,color="green" ,marker="o", label='Ro-Ro-last')
lns6 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Konteinerskip ,color="yellow" ,marker="o", label='Konteinerskip')
lns7 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Stykkgodsskip ,color="green" ,marker="o", label='Stykkgodsskip')
lns8 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Reefer, color="indigo" , marker="o", label= "Kjøle- og fryseskip")

#lns4 = ax2.plot(df_gods.ar, df_gods.Ankomster ,color="green" ,marker="o", label='Ankomster, godsfartøy')
ax.set_ylabel("Tonnkm (millioner)",color="blue",fontsize=14)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))
#ax.legend(loc=0)
#ax2.legend(loc=1)
lns = lns1+lns2+lns3+lns4+lns5+lns6+lns7+lns8
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=0)

plt.show()

tonnkm_skipskat.head(15)

fig,ax = plt.subplots(figsize=(15, 12))
# make a plot
lns3 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Gasstankskip ,color="pink" ,marker="o", label='Gasstankskip')
lns4 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Kjemikalieprodukttankere ,color="black" ,marker="o", label='Kjemikalie-/produkttankere')
lns5 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.RoRolast ,color="green" ,marker="o", label='Ro-Ro-last')
lns6 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Konteinerskip ,color="yellow" ,marker="o", label='Konteinerskip')
# set x-axis label
ax.set_xlabel("År",fontsize=14)

plt.title('Utvikling tonnkm for årene 2010 til 2018')
plt.grid()
#lns7 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Stykkgodsskip ,color="green" ,marker="o", label='Stykkgodsskip')
lns8 = ax.plot(tonnkm_skipskat.ar, tonnkm_skipskat.Reefer, color="indigo" , marker="o", label= "Kjøle- og fryseskip")
ax.set_ylabel("Tonnkm (millioner)",color="blue",fontsize=14)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' ')))

lns = lns3+lns4+lns5+lns6+lns8
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=0)

plt.show()