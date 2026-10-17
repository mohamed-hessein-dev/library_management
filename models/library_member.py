from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryMember(models.Model):
    _name = "library.member"
    _description = "Library Member"

    name = fields.Char(string="Member Name", required=True)
    email = fields.Char(string="Email", required=True)
    phone = fields.Char(string="Phone")
    user_id = fields.Many2one('res.users', string="Related User")

    membership_id = fields.Char(
        string="Membership ID",
        readonly=True,
        copy=False,
        default='New'
    )

    membership_date = fields.Date(
        string="Membership Date",
        default=fields.Date.today
    )

    membership_type = fields.Selection([
        ('regular', 'Regular'),
        ('premium', 'Premium'),
        ('student', 'Student')
    ], string="Membership Type", default='regular', required=True)

    status = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired')
    ], string="Status", default='active')

    max_books = fields.Integer(
        string="Max Books Allowed",
        compute="_compute_max_books",
        store=True
    )

    current_borrowed = fields.Integer(
        string="Currently Borrowed",
        compute="_compute_current_borrowed",
        store=True
    )

    fine_amount = fields.Float(
        string="Total Fines",
        default=0.0
    )

    borrowing_ids = fields.One2many(
        'library.borrowing',
        'member_id',
        string="Borrowing History"
    )


    @api.depends('membership_type')
    def _compute_max_books(self):
        limits = {
            'regular': 3,
            'premium': 5,
            'student': 2,
        }
        for rec in self:
            rec.max_books = limits.get(rec.membership_type, 0)

    @api.depends('borrowing_ids.status')
    def _compute_current_borrowed(self):
        for rec in self:
            rec.current_borrowed = len(
                rec.borrowing_ids.filtered(lambda b: b.status == 'borrowed')
            )


    @api.constrains('current_borrowed', 'max_books')
    def _check_max_books_limit(self):
        for rec in self:
            if rec.current_borrowed > rec.max_books:
                raise ValidationError(
                    "This member has reached the maximum number of books allowed (%s)." % rec.max_books
                )


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('membership_id', 'New') == 'New':
                vals['membership_id'] = self.env['ir.sequence'].next_by_code(
                    'library.member.sequence'
                ) or 'New'

        members = super().create(vals_list)

        for member in members:
            member._send_welcome_email()

        return members

    def write(self, vals):
        res = super().write(vals)
        if vals.get('status') == 'suspended':
            for member in self:
                active_borrowings = member.borrowing_ids.filtered(
                    lambda b: b.status == 'borrowed'
                )
                if active_borrowings:
                    active_borrowings.action_return()
        return res


    def action_view_borrowings(self):
        """يفتح لست بكل الاستعارات (borrowings) الخاصة بالعضو ده، بيتم استدعاؤها من الـ stat button في الـ form view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Borrowings',
            'res_model': 'library.borrowing',
            'view_mode': 'list,form',
            'domain': [('member_id', '=', self.id)],
            'context': {'default_member_id': self.id},
        }

    def action_view_fines(self):
        """يفتح لست بكل الاستعارات اللي عليها غرامة (fine) للعضو ده."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fines',
            'res_model': 'library.borrowing',
            'view_mode': 'list,form',
            'domain': [('member_id', '=', self.id), ('fine_amount', '>', 0)],
            'context': {'default_member_id': self.id},
        }


    def _send_welcome_email(self):
        self.ensure_one()
        template = self.env.ref(
            'library_management.email_template_welcome_member',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=True)