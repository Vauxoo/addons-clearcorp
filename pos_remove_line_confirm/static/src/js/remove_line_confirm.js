/*# -*- coding: utf-8 -*-
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
##############################################################################*/

openerp.pos_price_confirm = function (instance) {
    var module = instance.point_of_sale;
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    module.RemoveLineConfirmPopupWidget = module.PopUpWidget.extend({
        template: 'RemoveLineConfirmPopupWidget',
        show: function(options){
            var self = this;
            this._super();

            this.message = options.message || '';
            this.renderElement();

            this.$('.button.cancel').click(function(){
                self.pos_widget.screen_selector.close_popup();
                if( options.cancel ){
                    options.cancel.call(self);
                }
            });

            this.$('.button.confirm').click(function(){
                var login = self.$(".username")[0].value;
                var password = self.$('.password')[0].value;

                self.pos_widget.screen_selector.close_popup();
                if( options.confirm ){
                    options.confirm.call(self, login, password);
                }
            });
        },
    });

    module.PosWidget = module.PosWidget.extend({
        // Overloaded method to add the new widget
        build_widgets: function() {
            this._super();
            this.remove_line_confirm_popup = new module.RemoveLineConfirmPopupWidget(this, {});
            this.remove_line_confirm_popup.appendTo($(this.$el));
            this.screen_selector.popup_set['remove-line-confirm'] = this.remove_line_confirm_popup;
            // Hide the popup
            this.remove_line_confirm_popup.hide();
        },
    });

    module.NumpadWidget = module.NumpadWidget.extend({
        start: function() {
            this._super();
            this.authRemoveLine = false;
            var self = this;
            var user_model = new instance.web.Model('res.users');
            user_model.call('has_group', ['pos_remove_line_confirm.group_pos_remove']).then(function(result) {
                if (result) {
                   self.authRemoveLine = true;
                } else {
                   self.authRemoveLine = false;
                }
            }, function(error, event){
                event.preventDefault();
                self.pos_widget.screen_selector.show_popup('error',{
                    'message':_t('Error: Could not check your permissions.'),
                    'comment':_t('Your Internet connection is probably down.'),
                });
            });
        },

        clickDeleteLastChar: function() {
            var mode = this.state.get('mode');
            if (mode == 'quantity') {
                if (!this.authRemoveLine) {
                    var _super = this._super.bind(this);
                    var self = this;
                    self.pos.pos_widget.screen_selector.show_popup('remove-line-confirm', {
                        message: _t('Please authenticate as an authorized user.'),
                        confirm: function(login, password){
                            var user_model = new instance.web.Model('res.users');
                            user_model.call('pos_verify_remove_line', [login, password]).then(function(result) {
                                if (result == 'go') {
                                    self.state.set({'buffer': ""})
                                    return _super();
                                } else if (result == 'no-group') {
                                    self.pos_widget.screen_selector.show_popup('error',{
                                        'message':_t('Error: User permissions.'),
                                        'comment':_t('The user is not able to remove lines.'),
                                    });
                                } else {
                                    self.pos_widget.screen_selector.show_popup('error',{
                                        'message':_t('Error: Could not login.'),
                                        'comment':_t('Your user or password is incorrect.'),
                                    });
                                }
                            }, function(error, event){
                                event.preventDefault();
                                self.pos_widget.screen_selector.show_popup('error',{
                                    'message':_t('Error: Could not verify the login.'),
                                    'comment':_t('Your Internet connection is probably down.'),
                                });
                            });
                        },
                    });
                    return false;
                } else {
                    return this._super();
                }
            }
            else {
                return this._super();
            }
        },
    });
};
