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

from tools import config, ustr
fontsize = 12

#Make a python import for change function getImage in class EanBarCode
from openerp.addons.report_aeroo.barcode.EANBarCode import EanBarCode

class EanBarCodeInherit(EanBarCode):
    
    def getImage(self, value, height = 50, xw=1, rotate=None, extension = "PNG", width = 50):
        """ Get an image with PIL library 
        value code barre value
        height height in pixel of the bar code
        extension image file extension"""
        from PIL import Image, ImageFont, ImageDraw
        import os
        from string import lower, upper
          
        # Get the bar code list
        bits = self.makeCode(value)
          
        # Get the bar code with the checksum added
        code = ""
        for digit in self.EAN13:
           code += "%d"%digit
          
        # Create a new image
        position = 8
          
        #Change original method. Add new parameter "width", because the image when
        #is printed, it looks "cut" and numbers doesn't appear correctly
        #new method receives a tuple, (width, height)
        im = Image.new("1",(width, height))
                
        # Load font
        ad = os.path.abspath(os.path.join(ustr(config['root_path']), u'addons'))
        mod_path_list = map(lambda m: os.path.abspath(ustr(m.strip())), config['addons_path'].split(','))
        mod_path_list.append(ad)
    
        for mod_path in mod_path_list:
            font_file = mod_path+os.path.sep+ \
                        "report_aeroo"+os.path.sep+"barcode"+os.path.sep+"FreeMonoBold.ttf"
            if os.path.lexists(font_file):
                font = ImageFont.truetype(font_file, fontsize)
                        
        """
            In this section, redefined the way in position and pixels was 
            calculated. Also, fontsize was redefined too. 
        """
        # Create drawer
        draw = ImageDraw.Draw(im)
     
        # Erase image
        draw.rectangle(((0,0),(im.size[0],im.size[1])),fill=256)
     
        # Draw first part of number
        draw.text((0, height-20), code[0], font=font, fill=0)
     
        # Draw first part of number
        draw.text((position+4, height-20), code[1:7], font=font, fill=0)
        
        # Draw second part of number
        draw.text((len(bits)/2+2+position, height-20), code[7:], font=font, fill=0)
     
        # Draw the bar codes
        for bit in range(len(bits)):
            # Draw normal bar
            if bits[bit] == '1':
                draw.rectangle(((bit+position,0),(bit+position,height-21)),fill=0)
            # Draw long bar
            elif bits[bit] == 'L':
                draw.rectangle(((bit+position,0),(bit+position,height-7)),fill=0)
                
        # Save the result image
        return im


