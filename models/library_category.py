from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryCategory(models.Model):
    _name = "library.category"
    _description = "Library Category"

    name = fields.Char(string="Category Name", required=True)

    code = fields.Char(
        string="Category Code",
        required=True
    )

    parent_id = fields.Many2one(
        'library.category',
        string="Parent Category"
    )

    child_ids = fields.One2many(
        'library.category',
        'parent_id',
        string="Sub-categories"
    )

    book_ids = fields.One2many(
        'library.book',
        'category_id',
        string="Books"
    )

    book_count = fields.Integer(
        string="Book Count",
        compute='_compute_book_count'
    )

    description = fields.Text(string="Description")

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Category code must be unique!'),
    ]

    @api.depends('book_ids')
    def _compute_book_count(self):
        for rec in self:
            rec.book_count = len(rec.book_ids)

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(
                "You cannot create recursive categories (a category cannot be its own parent/ancestor)."
            )