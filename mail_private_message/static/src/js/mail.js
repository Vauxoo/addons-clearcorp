openerp.mail_private_message = function(session) {

    session.mail.ThreadComposeMessage.include({
        bind_events: function () {
            var self = this;
            this.$('.oe_post_private').on('click', self.on_message_post_private);
            this._super();
        },

        on_message_post_private: function (event) {
            var self = this;
            if (self.flag_post) {
                return;
            }
            if (this.do_check_attachment_upload() && (this.attachment_ids.length || this.$('textarea').val().match(/\S+/))) {
                self.flag_post = true;
                if (this.is_log) {
                    this.do_send_message_post([], this.is_log);
                }
                else {
                    this.check_recipient_partners().done(function (partner_ids) {
                        self.do_send_message_post_private(partner_ids, self.is_log);
                    });
                }
            }
        },

        do_send_message_post_private: function (partner_ids, log) {
            var self = this;
            var values = {
                'body': this.$('textarea').val(),
                'subject': false,
                'parent_id': this.context.default_parent_id,
                'attachment_ids': _.map(this.attachment_ids, function (file) {return file.id;}),
                'partner_ids': partner_ids,
                'context': _.extend(this.parent_thread.context, {
                    'mail_post_autofollow': true,
                    'mail_post_autofollow_partner_ids': partner_ids,
                }),
                'type': 'comment',
                'content_subtype': 'plaintext',
                'privacity': 'private',
            };
            if (log) {
                values['subtype'] = false;
            }
            else {
                values['subtype'] = 'mail.mt_comment';
            }
            this.parent_thread.ds_thread._model.call('message_post', [this.context.default_res_id], values).done(function (message_id) {
                var thread = self.parent_thread;
                var root = thread == self.options.root_thread;
                if (self.options.display_indented_thread < self.thread_level && thread.parent_message) {
                    var thread = thread.parent_message.parent_thread;
                }
                // create object and attach to the thread object
                thread.message_fetch([["id", "=", message_id]], false, [message_id], function (arg, data) {
                    var message = thread.create_message_object( data.slice(-1)[0] );
                    // insert the message on dom
                    thread.insert_message( message, root ? undefined : self.$el, root );
                });
                self.on_cancel();
                self.flag_post = false;
            });
        },
    });
}