from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Library Book"

    name = fields.Char(string="Book Title", required=True)
    isbn = fields.Char(string="ISBN", required=True)

    author_id = fields.Many2one(
        'res.partner',
        string="Author",
        required=True,
        domain=[('is_company', '=', False)]
    )

    category_id = fields.Many2one(
        'library.category',
        string="Category"
    )

    publication_date = fields.Date(string="Publication Date")
    pages = fields.Integer(string="Pages")

    total_copies = fields.Integer(
        string="Total Copies",
        default=1
    )

    available_copies = fields.Integer(
        string="Available Copies",
        compute="_compute_available_copies",
        store=True,
        default=0
    )

    active_borrowing_count = fields.Integer(
        string="Active Borrowings",
        compute="_compute_active_borrowing_count"
    )

    description = fields.Text(string="Description")
    cover_image = fields.Binary(string="Cover Image")

    status = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged')
    ], string="Status", default='available')

    borrowing_ids = fields.One2many(
        'library.borrowing',
        'book_id',
        string="Borrowings"
    )

    _sql_constraints = [
        (
            'isbn_unique',
            'unique(isbn)',
            'ISBN must be unique. This book already exists.'
        )
    ]

    # @api.depends('total_copies', 'borrowing_ids.status')
    # def _compute_available_copies(self):
    #     for rec in self:
    #         active_borrowings = len(
    #             rec.borrowing_ids.filtered(
    #                 lambda b: b.status == 'borrowed'
    #             )
    #         )
    #         rec.available_copies = (
    #             rec.total_copies - active_borrowings
    #         )
    # 
    # @api.depends('borrowing_ids.status')
    # def _compute_active_borrowing_count(self):
    #     for rec in self:
    #         rec.active_borrowing_count = len(
    #             rec.borrowing_ids.filtered(
    #                 lambda b: b.status == 'borrowed'
    #             )
    #         )


    def action_view_active_borrowings(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Borrowings',
            'res_model': 'library.borrowing',
            'view_mode': 'tree,form',
            'domain': [
                ('book_id', '=', self.id),
                ('status', '=', 'borrowed'),
            ],
            'context': {
                'default_book_id': self.id,
            },
        }

    @api.constrains('available_copies')
    def _check_available_copies(self):
        for rec in self:
            if rec.available_copies < 0:
                raise ValidationError(
                    "Available copies cannot be negative. "
                    "Please check the total copies or active borrowings."
                )

    @api.constrains('total_copies')
    def _check_total_copies(self):
        for rec in self:
            if rec.total_copies < 1:
                raise ValidationError(
                    "Total copies must be at least 1."
                )