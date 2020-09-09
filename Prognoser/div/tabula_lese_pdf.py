# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 14:03:48 2020

@author: 4112
"""

import tabula
from tabula import read_pdf
import pandas as pd

data = tabula.read_pdf(r'H:/TØI_rapporter/Transportytelser i Norge 1946-2018.pdf', pages=49)
#tonnkm_dom.head()
type(data)
print(data)
tabula.convert_into(r'H:/TØI_rapporter/Transportytelser i Norge 1946-2018.pdf', "C:/Python/UD/Grunnlagsdata/tonnkm_dom.csv", output_format="csv", pages=49)

#tonnkm_dom = pd.read_csv("C:/Python/UD/Grunnlagsdata/tonnkm_dom.csv")
#tonnkm_dom.head(50)


#tonn_dom1 = tabula.convert_into(r'H:/TØI_rapporter/Transportytelser i Norge 1946-2018.pdf', 'C:/Python/UD/Grunnlagsdata/test.csv', output_format="csv", pages=49)


tonnkm_eximp = read_pdf(r'H:/TØI_rapporter/Transportytelser i Norge 1946-2018.pdf', pages=53)
tonnkm_eximp

tonnkm_skipskat = pd.read_excel(r'C:/Python/UD/Grunnlagsdata/tonnkm etter skipstyper.xlsx')
tonnkm_skipskat.head()