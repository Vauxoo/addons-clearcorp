odoo.define('web.restrict_export_sidebar', function (require) {
    "use strict";

    var core = require('web.core');
    var Sidebar = require('web.Sidebar');
    var _t = core._t;
    var QWeb = core.qweb;

    // Extend Sidebar module, can be found in 'web/static/src/js/widgets/sidebar.js'
    Sidebar.include({
        add_items: function(section_code, items) {
            if (section_code != 'other' || !this.session) {
                return this._super(section_code, items);
            }

            var self = this;
            var _super = self._super;
            var args = arguments;

            $.when(
                // Also allows a special user group "Export" to export data.
                this.session.user_has_group('export_no_allowed.group_export')
            ).done(function(is_user, is_admin, can_export) {
                if (is_user && (can_export || is_admin)) {
                    _super.apply(self, args);
                }
                else {
                    var export_label = _t('Export');
                    for (var i = 0; i < items.length; i++) {
                        if (items[i]['label'] == export_label) {
                            items.splice(i, 1);
                        };
                    };
                    return _super.apply(self, args);
                }
            });

        },

    });
});
