/* © 2016 ClearCorp
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
odoo.define('account.reconciliation_filter', function (require) {
    "use strict";

    var core = require('web.core');
    var reconcil = require('account.reconciliation');
    var FieldMany2One = core.form_widget_registry.get('many2one');
    var _t = core._t;
    var QWeb = core.qweb;
    var Reconcilation = reconcil.bankStatementReconciliationLine.include({

            createFormWidgets: function() {
                var self = this;
                this._super();
                 self.$(".oe_form_field_many2one.oe_form_field_with_button").attr("style","display:none");
                // generate the change partner "form"
                var change_partner_field = {
                    relation: "res.partner",
                    string: _t("Partner"),
                    type: "many2one",
                    domain: ['|', ['customer','=',true], ['supplier','=',true]],
                    help: "",
                    readonly: false,
                    required: true,
                    selectable: true,
                    states: {},
                    views: {},
                    context: {},
                };
                var change_partner_node = {
                    tag: "field",
                    children: [],
                    required: true,
                    attrs: {
                        invisible: "False",
                        modifiers: '',
                        name: "change_partner",
                        nolabel: "True",
                    }
                };
                self.field_manager.fields_view.fields["change_partner"] = change_partner_field;
                self.change_partner_field = new FieldMany2One(self.field_manager, change_partner_node);
                self.change_partner_field.appendTo(self.$(".change_partner_container"));
                self.change_partner_field.on("change:value", self.change_partner_field, function() {
                    self.changePartner(this.get_value());
                });
                self.change_partner_field.$el.find("input").attr("placeholder", self.st_line.communication_partner_name || _t("Select Partner"));
            }
    });
});