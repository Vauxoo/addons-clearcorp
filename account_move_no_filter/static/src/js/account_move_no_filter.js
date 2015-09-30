openerp.account_move_no_filter = function(instance) {

    instance.web.account.QuickAddListView.include({
        start:function(){
            var self = this;
            return this._super().done(function (result) {
                self.current_period = null;
                self.current_journal = null;
            });
        },
    });
};