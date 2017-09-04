#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

HTML Table Class



Created on Mon Sep  4 15:56:39 2017

@author: que
"""
from __future__ import print_function


class Table(object):
    
    def __init__( self, nrows, ncolumns ):
        self.nrows = nrows
        self.ncolumns = ncolumns
        self.contents = [["" for i in range(self.ncolumns)] for j in range(self.nrows)]
        
        
    def __repr__(self):
        """
        Return a string representation of the table
        """
        r = "<table>\n"
        for row in range(self.nrows):
            r += "<tr>\n"
            for col in range(self.ncolumns):
                r+= "<td> "
                r+= str(self.contents[row][col])
                r+= "</td\n>"
            
            r+= "</tr>\n"
        
        r+="</table>\n"
        return r
    
    def setCell(self, row, column, content ):
        """
        Set the contents of a particular table cell
        """
        self.contents[row][column] = content
        
        
        
        


        
if __name__ == "__main__":
    
    t = Table(2,5)
    
    for i in range(t.nrows):
        for j in range(t.ncolumns):
            t.setCell(i,j,"%s-%s"%(i,j))
    assert str(t) == """<table>
<tr>
<td> 0-0</td
><td> 0-1</td
><td> 0-2</td
><td> 0-3</td
><td> 0-4</td
></tr>
<tr>
<td> 1-0</td
><td> 1-1</td
><td> 1-2</td
><td> 1-3</td
><td> 1-4</td
></tr>
</table>
"""
    # Test nested cell
    t2 = Table(2,2)
    t2.setCell(0,0, "one")
    t2.setCell(0,1, "two")
    t2.setCell(1,0,"three")
    t2.setCell(1,1, "four")
    
    t.setCell(0,0, t2)
    
    assert str(t) == """<table>
<tr>
<td> <table>
<tr>
<td> one</td
><td> two</td
></tr>
<tr>
<td> three</td
><td> four</td
></tr>
</table>
</td
><td> 0-1</td
><td> 0-2</td
><td> 0-3</td
><td> 0-4</td
></tr>
<tr>
<td> 1-0</td
><td> 1-1</td
><td> 1-2</td
><td> 1-3</td
><td> 1-4</td
></tr>
</table>
"""
    