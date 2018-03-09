/* © 2014 ClearCorp
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 * Code inspired in Odoo report module */

odoo.define('report_xls_template.report', function (require){

var Report = require('report.report');
var ActionManager = require('web.ActionManager');
var Core = require('web.core');
var CrashManager = require('web.crash_manager');
var Framework = require('web.framework');

var trigger_xls_download = function(session, response, c, action, options) {
    session.get_file({
        url: '/reportxlstemplate/download',
        data: {data: JSON.stringify(response)},
        complete: Framework.unblockUI,
        error: c.rpc_error.bind(c),
        success: function(){
            if (action && options && !action.dialog) {
                options.on_close();
            }
        },
    });
};

ActionManager.include({
    ir_actions_report_xml: function(action, options) {
        var self = this;
        Framework.blockUI();
        action = _.clone(action);
        _t =  Core._t;

        // xlsx QWeb reports
        if ('report_type' in action && (action.report_type == 'qweb-xls' || action.report_type == 'qweb-ods')) {
            var report_url = '';
            switch (action.report_type) {
                case 'qweb-xls':
                    report_url = '/reportxlstemplate/xls/' + action.report_name;
                    break;
                case 'qweb-ods':
                    report_url = '/reportxlstemplate/ods/' + action.report_name;
                    break;
                default:
                    report_url = '/reportxlstemplate/xls/' + action.report_name;
                    break;
            }

            // generic report: no query string
            // particular: query string of action.data.form and context
            if (!('data' in action) || !(action.data)) {
                if ('active_ids' in action.context) {
                    report_url += "/" + action.context.active_ids.join(',') + "?enable_editor=1";
                }
            } else {
                report_url += "?enable_editor=1";
                report_url += "&options=" + encodeURIComponent(JSON.stringify(action.data));
                report_url += "&context=" + encodeURIComponent(JSON.stringify(action.context));
            }

            var response = new Array();
            response[0] = report_url;
            response[1] = action.report_type;
            var c = CrashManager;

            return trigger_xls_download(self.session, response, c, action, options);

        } else {
            return self._super(action, options);
        }
    }
});

});