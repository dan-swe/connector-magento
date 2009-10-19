#########################################################################
#This module intergrates Open ERP with the magento core                 #
#Core settings are stored here                                          #
#########################################################################
#                                                                       #
# Copyright (C) 2009  Sharoon Thomas                                    #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

from osv import osv, fields
import magerp_osv

class res_partner_category(magerp_osv.magerp_osv):
    _inherit = "res.partner.category"
    _LIST_METHOD = 'ol_customer_groups.list'
    _columns = {
                'magento_id':fields.integer('Customer Group ID'),
                'tax_class_id':fields.integer('Tax Class ID'),
                'instance':fields.many2one('external.referential', 'Magento Instance', readonly=True, store=True),
                }
res_partner_category()

class res_partner_address(magerp_osv.magerp_osv):
    _inherit = "res.partner.address"
    _MAGE_FIELD = 'magento_id'
    _LIST_METHOD = 'ol_customer_address.list'
        
    _columns = {
        'magento_id':fields.integer('Magento ID'),
        'lastname':fields.char('Last Name', size=100),
        'instance':fields.many2one('external.referential', 'Magento Instance', readonly=True, store=True),
        'exportable':fields.boolean('Export to magento?'),
                }
    _defaults = {
        'exportable':lambda * a:True
                 }
res_partner_address()

class res_partner(magerp_osv.magerp_osv):
    _inherit = "res.partner"
    _MAGE_FIELD = 'magento_id'
    _LIST_METHOD = 'customer.list'
    _columns = {
        'magento_id':fields.integer('Magento customer ID', readonly=True, store=True),
        'group_id':fields.many2one('res.partner.category', 'Magento Group(Category)'),
        'store_id':fields.many2one('magerp.storeviews', 'Store'),
        'website_id':fields.many2one('external.shop.group', 'Website'),
        'created_in':fields.char('Created in', size=100),
        'created_at':fields.datetime('Created Date'),
        'updated_at':fields.datetime('Updated At'),
        'emailid':fields.char('Email ID', size=100),
        'instance':fields.many2one('external.referential', 'Magento Instance', readonly=True, store=True),
                }
    _mapping = {
        'customer_id':('magento_id', int),
        'group_id':('group_id', int, """result=self.pool.get('res.partner.category').mage_to_oe(cr,uid,group_id,instance)\nif result:\n\tresult=result[0]"""),
        'store_id':('store_id', int, """result=self.pool.get('magerp.storeviews').mage_to_oe(cr,uid,store_id,instance)\nif result:\n\tresult=result[0]"""),
        'website_id':('website_id', int, """result=self.pool.get('external.shop.group').mage_to_oe(cr,uid,website_id,instance)\nif result:\n\tresult=result[0]"""),
        'created_in':('created_in', str),
        'created_at':('created_at', str,),
        'updated_at':('created_at', str,),
        #'prefix':(False,str,''),
        'firstname':(False, str, """if firstname:\n\tif 'name' in vals.keys() and vals['name']:\n\t\tresult = [('name',firstname+" "+vals['name'])]\n\telse:\n\t\tresult = [('name',firstname)]"""),
        #'middlename':(False,str,''),
        'lastname':(False, str, """if lastname:\n\tif 'name' in vals.keys() and vals['name']:\n\t\tresult = [('name',vals['name']+" "+lastname)]\n\telse:\n\t\tresult = [('name',lastname)]"""),
        #'suffix':(False,str,''),
        #'default_billing':(False,int,"""result = self.pool.get('res.partner.address').mage_to_oe(cr,uid,default_billing,instance)\nif result:\n\tresult=self.pool.get('res.partner.address').write(cr,uid,result[0],{'type':'default'})"""),
        #'default_shipping':(False,int,"""result = self.pool.get('res.partner.address').mage_to_oe(cr,uid,default_billing,instance)\nif result:\n\tresult=self.pool.get('res.partner.address').write(cr,uid,result[0],{'type':'delivery'})"""),
        'emailid':('emailid', str)
                }
    
    def mage_import(self, cr, uid, ids_or_filter, conn, instance, debug=False, defaults={}, *attrs):
        #first pull all addresses
        ret = super(res_partner, self).mage_import(cr, uid, ids_or_filter, conn, instance, debug)
        result = conn.call(self._LIST_METHOD, ids_or_filter)
        if result:
            cust_ids = []
            for each in result:
                cust_ids.append(each['customer_id'])
            self.pool.get('res.partner.address').mage_import(cr, uid, cust_ids, conn, instance, debug, defaults={})
        return ret
    
    def mage_import_base(self,cr,uid,conn, external_referential_id, defaults={}, context={}):
        #Overwriting customer sync
        ids_or_filter = context.get('ids_or_filter',[])
        ret = super(res_partner, self).mage_import_base(cr,uid,conn, external_referential_id, defaults, context)
        result = conn.call(self._LIST_METHOD, ids_or_filter)
        if result:
            cust_ids = []
            for each in result:
                cust_ids.append(each['customer_id'])
            context['ids_or_filter'] = cust_ids
            self.pool.get('res.partner.address').mage_import_base(cr,uid,conn, external_referential_id, defaults, context)
res_partner()
