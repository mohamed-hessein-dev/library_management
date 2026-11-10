# 📚 Library Management System for Odoo 17

A complete library management module for Odoo 17: books, categories, members, borrowing workflow, automated overdue handling, fines, and PDF reports.

## ✨ Features

- 📖 **Book Management**: ISBN-unique catalog, author (linked to partners), category, pages, cover image, copies tracking (total / available), and status (available, borrowed, lost, damaged)
- 🗂 **Hierarchical Categories**: parent/child categories with unique codes and recursion protection
- 👥 **Member Management**: Regular, Premium and Student memberships with automatic borrowing limits (3 / 5 / 2 books), auto-generated membership IDs, and a welcome email on registration
- 🔄 **Borrowing Workflow**: auto-generated references, 14-day due dates, return handling, and status tracking (borrowed, returned, overdue)
- 💰 **Fines**: automatic fine calculation for overdue books (5 per day)
- ⏰ **Scheduled Action**: daily cron job that marks overdue borrowings
- ✅ **Validations**: duplicate borrowing prevention, max-books limit, book availability checks, and warnings for suspended or inactive members
- 🧙 **Wizard** and 📄 **PDF Reports**: borrowing card and overdue books report
- 🔐 **Security**: access rights and user groups

## 🛠 Tech Stack

| Technology | Usage |
|------------|-------|
| Odoo 17 | ERP framework |
| Python 3.10 | Business logic (ORM models, constraints, computed fields) |
| PostgreSQL | Database |
| XML / QWeb | Views, security, cron, and reports |

## 📁 Module Structure

```
library_management/
├── data/          # Sequences, cron job, email templates
├── models/        # Book, Category, Member, Borrowing
├── report/        # QWeb PDF reports
├── security/      # Groups and access rights
├── view/          # List, form views and menus
├── wizard/        # Wizards
├── __init__.py
└── __manifest__.py
```

## 🚀 Installation

1. Clone into your custom addons folder:
   ```bash
   git clone https://github.com/mohamed-hessein-dev/library_management.git
   ```
2. Add the path to `addons_path` in `odoo.conf`.
3. Restart the Odoo server.
4. Enable **Developer Mode**, go to **Apps → Update Apps List**.
5. Search for **Library Management** and click **Install**.

**Dependencies:** `base`, `mail`

## 📸 Screenshots
<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/ace76baf-692f-45d9-ad8a-10650bd78af3" />
<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/cdbfe1a1-3864-4bd1-9cf9-21b5499f44ea" />
<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/2a2d07f5-a10f-40c2-8fb0-a4aa28aa59da" />
<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/02cb5dcc-f312-42d8-9332-5681a72bb004" />


## 👨‍💻 Author

**Mohamed Hessein**
- GitHub: [@mohamed-hessein-dev](https://github.com/mohamed-hessein-dev)
- LinkedIn: https://www.linkedin.com/in/mohammed-hessein-el-roby/

## 📄 License

LGPL-3
