#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 18:52:09 2017

HTML For class

@author: que
"""

from __future__ import print_function

class Form(object):
    """
    HTML form object - basically a container for other objects with a form
    """
    
    def __init__(self, action, method, submit_text =None):
        self.contents = []
        self.action = action
        self.method = method
        self.submit_text = submit_text
        pass
    
    def __repr__(self):
        form = "<FORM action=%s method=%s >\n" % (self.action, self.method)
        for c in self.contents:
            form += str(c)
            form += '\n'
        
        if self.submit_text is not None:
            form += '<input type="submit" value="%s">\n' % self.submit_text
        form += "\n</FORM>\n"
        return form
        
    def addContent(self, content):
        self.contents.append(content)
        
        

    
if __name__=="__main__":

    f = Form("/cgi/plot.py", "post","Plot")  
    
    f.addContent('<input type="radio" name="color" value="Green"> Green<br>')

    assert(str(f)== """<FORM action=/cgi/plot.py method=post >
<input type="radio" name="color" value="Green"> Green<br>
<input type="submit" value="Plot">

</FORM>
""")
    