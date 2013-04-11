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

from osv import osv, fields
from tools.translate import _

class company_webkit(osv.osv):
	_name = "res.company"
	_inherit = "res.company"
	
	def _get_default_header(self,cr,uid,ids):
		return """
<html>
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
		<script>
			function subst() {
			var vars={};
			var x=document.location.search.substring(1).split('&');
			for(var i in x) {var z=x[i].split('=',2);vars[z[0]] = unescape(z[1]);}
			var x=['frompage','topage','page','webpage','section','subsection','subsubsection'];
			for(var i in x) {
			var y = document.getElementsByClassName(x[i]);
			for(var j=0; j<y.length; ++j) y[j].textContent = vars[x[i]];
				}
			}
		</script>
		<style type="text/css">
			${css}
		</style>
		</head>
	<body class = "header" onload="subst()">
		<table class="header-table" cellspacing = "3">
			<tbody>
				<tr>
					<td>
						${helper.embed_logo_by_name('company_logo')|n}	
					</td>
					<td>
						<table class="company_data">
							<tr class = "title">
								<td>${company.partner_id.name |entity}</td>
								<td style = "text-align : right;">${_("Address")}</td>
							</tr>
							<tr>
								<td>${_("ID Num")}: ${company.partner_id.ref | entity}</td>
								<td style = "text-align : right;">${company.partner_id.address[0].street or ''|entity}</td>
							</tr>
							<tr>
								<td>${_("Tel-fax")}: ${company.partner_id.address[0].phone or '-'|entity}</td>
								<td style = "text-align : right;">${company.partner_id.address[0].street2 or ''|entity}</td>
							</tr>
							<tr>
								<td>${_("E-mail")}: ${company.partner_id.address[0].email or '-'|entity}</td>
								<td style = "text-align : right;">${company.partner_id.address[0].zip or ''|entity} ${company.partner_id.address[0].city or ''|entity}</td>
							</tr>
							<tr>
								<td>${_("Web")}: ${company.partner_id.website or '-'|entity}</td>
								%if company.partner_id.address[0].country_id :
									<td style = "text-align : right;">${company.partner_id.address[0].state_id.name  or ''|entity}, ${company.partner_id.address[0].country_id.name or ''|entity} </td>
								%else:
									<td style = "text-align : right;">&nbsp;</td>
								%endif
							</tr>
						</table>
					</td>
				</tr>
			</tbody>
		</table>
		
		<p class = "slogan">${company.rml_header1}</p>
		</body>
</html>
"""
	
	def _get_default_footer(self,cr,uid,ids):
		return """
<html>
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
		<script>
			function subst() {
			var vars={};
			var x=document.location.search.substring(1).split('&');
			for(var i in x) {var z=x[i].split('=',2);vars[z[0]] = unescape(z[1]);}
			var x=['frompage','topage','page','webpage','section','subsection','subsubsection'];
			for(var i in x) {
			var y = document.getElementsByClassName(x[i]);
			for(var j=0; j<y.length; ++j) y[j].textContent = vars[x[i]];
				}
			}
		</script>
		<style type="text/css">
			${css}
		</style>
	</head>
	<body class = "footer" onload="subst()">
		<table class = "footer_table">
			<tr><td><p class ="company_footer">${company.webkit_footer1 or '&nbsp;'}</p></td></tr>
			<tr><td><p class ="company_footer">${company.webkit_footer2 or '&nbsp;'}</p></td><td style="text-align:right;font-size:12;">Page <span class="page"/></td><td style="text-align:left;font-size:12;">  of <span class="topage"/></td></tr>
			<tr><td><p class ="company_footer">${company.webkit_footer3 or '&nbsp;'}</p></td></tr>
        </table>
    </body>
</html>
		"""
	def _get_default_css(self,cr,uid,ids):
		return """
			.header {
				padding : 200px 10px 5px 10px;
				border:0; margin: 0;
			}
			.header-table {
				width: 100%;
				padding-top: 8%;
			}
			.partner-table {
				width: 100%;
				font-family: Arial,Verdana, Sans, Serif;
				font-size: 12;
			}

			#data-table {
				width: 100%;
				padding-top: 20px;
				font-family: Arial,Verdana, Sans, Serif;
				font-size: 12;
			}
			#data-table th{
				border-bottom:2px solid black;
				text-align:center;
				font-size:12;
				font-weight:bold;
				padding-right:3px;
				padding-left:3px;
			}
			#data-table thead {
				display:table-header-group;
			}

			.title {
				font-size:16;
				font-weight: bold;
			}

			.company_address{
				width : 100%;
				text-align: right;
				font-family: Arial,Verdana, Sans, Serif;
				font-size: 13;
			}

			.company_data {
				width : 100%;
				text-align: center;
				font-family: Arial,Verdana, Sans, Serif;
				font-size: 13;
				
			}
			
			.company_footer {
				font-family: Arial,Verdana, Sans, Serif;
				font-size: 8.4;
				font-style : italic;
			}
			.footer {
				border-top: 1px solid black; 
				width: 100%;
				border:0; margin: 0;
				padding-bottom: 300px;
			}

			.data {
				padding : 5px 10px 10px 10px;
				border:0; margin: 0;
			}

			.footer_table {
				width: 100%;
				padding-bottom: 150px;
				border-top: 1px solid black;
			}
			
			.slogan {
				font-family: Arial,Verdana, Sans, Serif;
				font-size: 10;
				font-style : italic;
				color : #888888;
			}
			
			#notes_table {
				font-family: Arial,Verdana, Sans, Serif;
				font-size: 12;
				font-style : italic;
				width:65%;
				border-collapse:separate;
				border-spacing:10px;
			}
			#notes_table td{
				background-color: #eee;
				padding: 10px
			}
			
			.document_data {
				font-family: Arial,Verdana, Sans, Serif;
				font-size: 13;
				width : 100%;
			}
			
			#data-table tbody tr.even td {
				background-color: #eee;
			}
			#data-table tbody tr.odd  td {
				background-color: #fff;
			}
			
			.notes{
				padding-top : 0px;
				margin-left: 5px;
				font-style : italic;
			}
			#desc_col{
				width : 380px;
			}

		"""
	def create(self,cr,uid, vals,context=None):
		company_id = super(company_webkit,self).create(cr,uid,vals,context)
		obj_company = self.pool.get('res.company').browse(cr,uid,company_id)
		
		vals = {
			'name' : 'Base ' + obj_company.name, 
			'html': obj_company._get_default_header(), 
			'css' : obj_company._get_default_css(),
			'footer_html' : obj_company._get_default_footer(),
			'margin_top' : 55.00,
			'margin_bottom' : 24.00,
			'orientation' : 'Portrait',
			'format' : 'Letter',
		}
		register_id = self.pool.get('ir.header_webkit').search(cr,uid,[('name','=', 'Base ' + obj_company.name)])
		if not register_id:
			#obj_header = super(rent_contract,self).create(cr,uid,vals,context) 
			obj_company.write({'header_webkit' : [(0,0, vals)]})
		return obj_company.id
		
	_columns = {
		'webkit_footer1': fields.char('Report Footer 1', size=200),
		'webkit_footer2': fields.char('Report Footer 2', size=200),
		'webkit_footer3': fields.char('Report Footer 3', size=200),
	}
company_webkit()
