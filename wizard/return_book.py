from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizardReturnBook(models.TransientModel):
    _name = "wizard.return.book"
    _description = "Return Book Wizard"

    borrowing_id = fields.Many2one(
        'library.borrowing',
        string="Borrowing",
        required=True
    )

    return_date = fields.Date(
        string="Return Date",
        default=fields.Date.today,
        required=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            res['borrowing_id'] = active_id
        return res

    def action_confirm_return(self):
        self.ensure_one()

        if self.borrowing_id.status == 'returned':
            raise ValidationError("This book has already been returned.")

        self.borrowing_id.write({
            'return_date': self.return_date,
        })
        self.borrowing_id.action_return()

        return {'type': 'ir.actions.act_window_close'}