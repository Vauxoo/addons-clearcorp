
openerp.document_open_attachment = function(instance) {

instance.web.Sidebar.include({

    on_attachments_loaded: function(attachments) {
        this._super(attachments);
        this.$el.find('.oe_sidebar_edit_item').click(this.on_attachment_edit);
    },
    on_attachment_edit: function(e) {
        e.preventDefault();
        e.stopPropagation();
        var self = this;
        var $e = $(e.currentTarget);
        if (confirm(_t("Do you really want to edit this attachment?"))) {
            self.do_action({
                views: [[false, 'form']],
                view_type: 'form',
                view_mode: 'form',
                res_model: 'ir.attachment',
                type: 'ir.actions.act_window',
                target: 'current',
                res_id: parseInt($e.attr('data-id'), 10),
            });
        }
    }

});

};