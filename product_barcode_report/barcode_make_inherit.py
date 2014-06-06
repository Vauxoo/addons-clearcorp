# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
    To override this function and add new parameter, width (this is for create a image,
    because the original image is display incorrectly (looks like "cut"). So,
    the solution is adjust the function that create the image and adapt with 
    height and width the position of pixels.
    
    To override the function, import the file as a "python" import and then,
    override the function "make_barcode". But, also, "original" class EanBarCode
    was override too, and it must be change the instance of class EanBarCode for
    EanBarCodeInherit. This class is an inherit class with other changes.
    
"""
from openerp.addons.report_aeroo.barcode import barcode
from openerp.addons.product_barcode_report.EANBarCode_inherit import EanBarCodeInherit

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def make_barcode(code, code_type='ean13', rotate=None, height=50, xw=1, width=50):
    if code:
        if code_type.lower()=='ean13':
            bar=EanBarCodeInherit() #change class instance
            #this method was changed in EanBarCodeInherit class. 
            #Add width parameter
            im = bar.getImage(code,height=height,width=width)
        elif code_type.lower()=='code128':
            im = get_code(code, xw, height)
        elif code_type.lower()=='code39':
            im = create_c39(height, xw, code)
    else:
        return StringIO(), 'image/png'

    tf = StringIO()
    try:
        if rotate!=None:
            im=im.rotate(int(rotate))
    except Exception, e:
        pass
    im.save(tf, 'png')
    size_x = str(im.size[0]/96.0)+'in'
    size_y = str(im.size[1]/96.0)+'in'
    return tf, 'image/png', size_x, size_y

#With this instruction, override method. barcode is the original file where
#make_barcode function is. Then, assign new function (it must have the same name)
#and override original function
barcode.make_barcode = make_barcode