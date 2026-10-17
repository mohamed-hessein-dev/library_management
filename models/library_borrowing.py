from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class LibraryBorrowing(models.Model):
    _name = "library.borrowing"
    _description = "Library Borrowing"
    _rec_name = "name"
    _order = "borrow_date desc"

    name = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default='New'
    )

    book_id = fields.Many2one(
        'library.book',
        string="Book",
        required=True
    )

    member_id = fields.Many2one(
        'library.member',
        string="Member",
        required=True
    )

    borrow_date = fields.Date(
        string="Borrow Date",
        default=fields.Date.today
    )

    due_date = fields.Date(
        string="Due Date",
        compute='_compute_due_date',
        store=True
    )

    return_date = fields.Date(string="Return Date")

    status = fields.Selection([
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ], string="Status", default='borrowed', tracking=True)

    fine_amount = fields.Float(
        string="Fine Amount",
        compute='_compute_fine_amount',
        store=True
    )

    notes = fields.Text(string="Notes")

    @api.depends('borrow_date')
    def _compute_due_date(self):
        for rec in self:
            if rec.borrow_date:
                rec.due_date = rec.borrow_date + timedelta(days=14)
            else:
                rec.due_date = False

    @api.depends('status', 'due_date')
    def _compute_fine_amount(self):
        today = fields.Date.today()
        for rec in self:
            if rec.status == 'overdue' and rec.due_date and today > rec.due_date:
                days_overdue = (today - rec.due_date).days
                rec.fine_amount = days_overdue * 5.0
            else:
                rec.fine_amount = 0.0


    @api.onchange('member_id')
    def _onchange_member_id(self):
        if self.member_id:
            if self.member_id.status == 'suspended':
                return {
                    'warning': {
                        'title': "Suspended Member",
                        'message': "This member is suspended and cannot borrow books."
                    }
                }
            elif self.member_id.status != 'active':
                return {
                    'warning': {
                        'title': "Inactive Member",
                        'message': "This member is not currently active."
                    }
                }

    @api.onchange('book_id')
    def _onchange_book_id(self):
        if self.book_id:
            if self.book_id.available_copies <= 0:
                return {
                    'warning': {
                        'title': "Book Not Available",
                        'message': "There are no available copies of this book."
                    }
                }

    @api.constrains('book_id', 'member_id', 'status')
    def _check_duplicate_borrowing(self):
        for rec in self:
            if rec.status == 'borrowed':
                duplicate = self.search([
                    ('id', '!=', rec.id),
                    ('book_id', '=', rec.book_id.id),
                    ('member_id', '=', rec.member_id.id),
                    ('status', '=', 'borrowed'),
                ])
                if duplicate:
                    raise ValidationError(
                        "This member already has an active borrowing for this book."
                    )

    @api.constrains('member_id', 'status')
    def _check_member_max_books(self):
        for rec in self:
            if rec.status == 'borrowed':
                if rec.member_id.current_borrowed > rec.member_id.max_books:
                    raise ValidationError(
                        "Member has exceeded the maximum allowed books (%s)."
                        % rec.member_id.max_books
                    )

    @api.constrains('book_id', 'status')
    def _check_book_availability(self):
        for rec in self:
            if rec.status == 'borrowed':
                other_active = self.search_count([
                    ('id', '!=', rec.id),
                    ('book_id', '=', rec.book_id.id),
                    ('status', '=', 'borrowed'),
                ])
                if rec.book_id.total_copies - other_active <= 0:
                    raise ValidationError(
                        "There are no available copies of this book to borrow."
                    )


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'library.borrowing'
                ) or 'New'
        return super().create(vals_list)


    def action_return(self):
        for rec in self:
            if rec.status == 'returned':
                raise ValidationError("This book has already been returned.")
            rec.write({
                'status': 'returned',
                'return_date': fields.Date.today(),
            })
        return True

    @api.model
    def action_mark_overdue(self):
        """Called daily by the cron job"""
        today = fields.Date.today()
        overdue_borrowings = self.search([
            ('status', '=', 'borrowed'),
            ('due_date', '<', today),
        ])
        overdue_borrowings.write({'status': 'overdue'})

        for rec in overdue_borrowings:
            pass

        return True
