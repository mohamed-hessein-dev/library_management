from odoo import models, fields, api


class WizardSendReminder(models.TransientModel):
    _name = "wizard.send.reminder"
    _description = "Send Reminder Wizard"

    member_ids = fields.Many2many(
        'library.member',
        string="Members",
        required=True
    )

    message = fields.Text(
        string="Message",
        required=True,
        default="This is a reminder that you have overdue books. "
                "Please return them as soon as possible to avoid additional fines."
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            res['member_ids'] = [(6, 0, active_ids)]
        return res

    def action_send_email(self):
        self.ensure_one()

        mail_values_list = []
        for member in self.member_ids:
            if not member.email:
                continue
            mail_values_list.append({
                'subject': 'Library Reminder',
                'body_html': '<p>%s</p>' % self.message,
                'email_to': member.email,
                'auto_delete': True,
            })

        if mail_values_list:
            self.env['mail.mail'].create(mail_values_list).send()

        return {'type': 'ir.actions.act_window_close'}