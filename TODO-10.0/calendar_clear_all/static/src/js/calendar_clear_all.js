/* © 2016 ClearCorp
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define("calendar_clear_all", function(require) {
"use strict";

var core = require('web.core');
var widgets = require("web_calendar.widgets");

var QWeb = core.qweb;

widgets.SidebarFilter.include({
    events: _.extend({}, widgets.SidebarFilter.prototype.events, {
        "click a.calendar_clear_all": "filter_clear_click",
    }),

    filter_clear_click: function(e) {
        var self = this;
        var filter_me = _.first(_.values(self.view.all_filters));
        _.forEach(self.view.all_filters, function(filter) {
            if (filter.value != filter_me.value) {
                filter.is_checked = false;
            } else {
                filter.is_checked = true;
            }

        });

        self.$("input:checkbox").not("[value='" + filter_me.value + "']").prop( "checked", false );
        self.$("input:checkbox[value='" + filter_me.value + "']").prop( "checked", true );
        self.view.$calendar.fullCalendar("refetchEvents");
    },
});

});