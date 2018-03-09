/* © 2016 ClearCorp
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
odoo.define('account.reconciliation_filter', function (require) {
    "use strict";

    var reconcile = require('account.reconciliation');
    var Reconciliation = reconcile.bankStatementReconciliationLine.include({

            createFormWidgets: function() {
                this._super();
                this.field_manager.fields_view.fields.change_partner.domain = ['|', ['customer','=',true], ['supplier','=',true]];
            }
    });
});