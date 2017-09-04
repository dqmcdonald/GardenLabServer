#!/usr/bin/env python
import os,sys
import cgi
import cgitb; cgitb.enable()


from pyhtml.table import Table
from pyhtml.page import Page

t = Table(2,3)
t.setCell(0,1, "<H3>Table</H3>")

p = Page("GardenLab Plotting")
p.addContent(t)

print("Content-type: text/html\n")
print p



