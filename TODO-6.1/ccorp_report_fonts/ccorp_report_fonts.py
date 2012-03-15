# -*- encoding: utf-8 -*-
##############################################################################
#
#    ccorp_report_fonts.py
#    ccorp_report_fonts
#    First author: Carlos Vásquez <carlos.vasquez@clearcorp.co.cr> (ClearCorp S.A.)
#    Copyright (c) 2010-TODAY ClearCorp S.A. (http://clearcorp.co.cr). All rights reserved.
#    
#    Redistribution and use in source and binary forms, with or without modification, are
#    permitted provided that the following conditions are met:
#    
#       1. Redistributions of source code must retain the above copyright notice, this list of
#          conditions and the following disclaimer.
#    
#       2. Redistributions in binary form must reproduce the above copyright notice, this list
#          of conditions and the following disclaimer in the documentation and/or other materials
#          provided with the distribution.
#    
#    THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ``AS IS'' AND ANY EXPRESS OR IMPLIED
#    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#    FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
#    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#    ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#    
#    The views and conclusions contained in the software and documentation are those of the
#    authors and should not be interpreted as representing official policies, either expressed
#    or implied, of ClearCorp S.A..
#    
##############################################################################

from tools.config import config
import report
import os

import reportlab
import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

reportlab.rl_config.warnOnMissingFontGlyphs = 0
enc = 'UTF-8'

def wrap_trml2pdf(method):
    """We have to wrap the original parseString() to modify the rml data
    before it generates the pdf."""
    #AppleGaramond
    pdfmetrics.registerFont(TTFont('AppleGaramond', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'AppleGaramond-Regular.ttf'),enc))
    pdfmetrics.registerFont(TTFont('AppleGaramond-Bold', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'AppleGaramond-Bold.ttf'),enc))
    pdfmetrics.registerFont(TTFont('AppleGaramond-Light', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'AppleGaramond-Light.ttf'),enc))
    pdfmetrics.registerFont(TTFont('AppleGaramond-Italic', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'AppleGaramond-Italic.ttf'),enc))
    pdfmetrics.registerFont(TTFont('AppleGaramond-BoldItalic', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'AppleGaramond-BoldItalic.ttf'),enc))
    pdfmetrics.registerFont(TTFont('AppleGaramond-LightItalic', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'AppleGaramond-LightItalic.ttf'),enc))
    addMapping('AppleGaramond', 0, 0, 'AppleGaramond')
    addMapping('AppleGaramond', 1, 0, 'AppleGaramond-Bold')
    addMapping('AppleGaramond', 0, 1, 'AppleGaramond-Italic')
    addMapping('AppleGaramond', 1, 1, 'AppleGaramond-BoldItalic')
    addMapping('AppleGaramond-Light', 0, 0, 'AppleGaramond-Light')
    addMapping('AppleGaramond-Light', 0, 1, 'AppleGaramond-LightItalic')
    #MyriadPro
    pdfmetrics.registerFont(TTFont('MyriadPro', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'MyriadPro-Regular.ttf'),enc))
    pdfmetrics.registerFont(TTFont('MyriadPro-Bold', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'MyriadPro-Bold.ttf'),enc))
    pdfmetrics.registerFont(TTFont('MyriadPro-Italic', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'MyriadPro-Italic.ttf'),enc))
    pdfmetrics.registerFont(TTFont('MyriadPro-BoldItalic', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'MyriadPro-BoldItalic.ttf'),enc))
    addMapping('MyriadPro', 0, 0, 'MyriadPro')
    addMapping('MyriadPro', 1, 0, 'MyriadPro-Bold')
    addMapping('MyriadPro', 0, 1, 'MyriadPro-Italic')
    addMapping('MyriadPro', 1, 1, 'MyriadPro-BoldItalic')
    #Inconsolata
    pdfmetrics.registerFont(TTFont('Inconsolata', os.path.join(os.path.abspath(config['addons_path']), 'ccorp_report_fonts', 'fonts', 'Inconsolata.ttf'), enc))
    addMapping('Inconsolata', 0, 0, 'Inconsolata')
    addMapping('Inconsolata', 1, 0, 'Inconsolata')
    addMapping('Inconsolata', 0, 1, 'Inconsolata')
    addMapping('Inconsolata', 1, 1, 'Inconsolata')
    
    def convertClearCorpFonts(*args, **argv):
        """This function replaces the type1 font names with their truetype
        substitutes and puts a font registration section at the beginning
        of the rml file. The rml file is acually a string (data)."""
        data = args[0]
        fontmap = {
            'Times-Roman':                  'AppleGaramond',
            'Times-BoldItalic':             'AppleGaramond-BoldItalic',
            'Times-Bold':                   'AppleGaramond-Bold',
            'Times-Italic':                 'AppleGaramond-Italic',
            'Times-Light':		    'AppleGaramond-Light',
            'Times-LightItalic':    'AppleGaramond-LightItalic',

            'TimesCondensed-Roman':         'AppleGaramond',
            'TimesCondensed-BoldItalic':    'AppleGaramond-BoldItalic',
            'TimesCondensed-Bold':          'AppleGaramond-Bold',
            'TimesCondensed-Italic':        'AppleGaramond-Italic',

            'Helvetica-BoldItalic':         'MyriadPro-BoldItalic',
            'Helvetica-BoldOblique':        'MyriadPro-BoldItalic',
            'Helvetica-Bold':               'MyriadPro-Bold',
            'Helvetica-Italic':             'MyriadPro-Italic',
            'Helvetica-Oblique':            'MyriadPro-Italic',
            'Helvetica':                    'MyriadPro',

            'Helvetica-ExtraLight':         'MyriadPro',

            'HelveticaCondensed-BoldItalic':'MyriadPro-BoldCondItalic',
            'HelveticaCondensed-Bold':      'MyriadPro-BoldCond',
            'HelveticaCondensed-Italic':    'MyriadPro-CondItalic',
            'HelveticaCondensed':           'MyriadPro-Cond',

            'Courier':                      'Inconsolata',
            'Courier-Bold':                 'Inconsolata',
            'Courier-BoldItalic':           'Inconsolata',
            'Courier-Italic':               'Inconsolata',
        }
        for  old, new in fontmap.iteritems():
            data = data.replace(old, new)
        return method(data, args[1:] if len(args) > 2 else args[1], **argv)
    return convertClearCorpFonts

report.render.rml2pdf.parseString = wrap_trml2pdf(report.render.rml2pdf.parseString)

report.render.rml2pdf.parseNode = wrap_trml2pdf(report.render.rml2pdf.parseNode)
