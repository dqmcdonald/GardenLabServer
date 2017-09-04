#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Select element of FORM. Intended to be added to form object.


Created on Tue Sep  5 08:42:08 2017


@author: que
"""

from __future__ import print_function

class FormSelect:
    """
    Select element of HTML form
    """
    
    def __init__(self, name, items, current_item=None):
        self.name = name
        self.items = [x for x in items]
        self.current_item = current_item
        
    
    def setCurrentItem(self, current_item):
        if current_item not in self.items:
            raise ValueError("%s is not one of the valid options" % current_item)
        self.current_item = current_item
        
    
    def __repr__(self):
        sel = '<select name="%s">\n' % (self.name)
        for i in self.items:
            if i == self.current_item:
                selected = "selected"
            else:
                selected = ""
            sel += '<option value="%s" %s>%s</option>\n' % (i,selected,i)
        sel += '</select>\n'
        return sel
        
        

if __name__ == "__main__":
    
    s= FormSelect( "cars", ['volvo','saab','fiat','audi'], 'fiat')
    
    assert( str(s) == """<select name="cars">
<option value="volvo" >volvo</option>
<option value="saab" >saab</option>
<option value="fiat" selected>fiat</option>
<option value="audi" >audi</option>
</select>
""")
    
    s.setCurrentItem('audi')
    
    assert( str(s) == """<select name="cars">
<option value="volvo" >volvo</option>
<option value="saab" >saab</option>
<option value="fiat" >fiat</option>
<option value="audi" selected>audi</option>
</select>
""")
    
    try:
        s.setCurrentItem('VW')
    except ValueError:
        print("Correctly caught bad current item")
    else:
        print("***Failed to catch setting bad current item")
        