# Library Management System

A full-featured, Tkinter-based Library Management System written in Python.  It streamlines day-to-day library operations—cataloguing books, registering members, issuing and returning books, calculating fines, and producing real-time statistics—while providing a clean, modern graphical interface and solid security practices.

---

## Key Features

### 1. Secure User Authentication
* BCrypt-hashed passwords 
* Two built-in roles:
  * **Administrator** – full control including librarian management
  * **Librarian** – day-to-day circulation tasks

### 2. Book Management
* Add, edit, withdraw books
* ISBN validation and duplicate detection
* Availability states: **Available · Issued · Maintenance**
* Category tagging and search filters

### 3. Member Management
* Rich member profiles: personal, contact, address, emergency, identification
* Multiple member types (Student, Faculty, Staff, Senior Citizen, General, Premium)
* Automatic borrowing limits and status flags (Active, Suspended, Blocked, Expired)

### 4. Circulation & Fines
* Issue, renew, and return workflows
* Automatic overdue detection and fine calculation
* Member book-limit enforcement

### 5. Dashboard & Reporting
* Real-time tiles for books, members, transactions, and fines
* Quick links to overdue lists, active loans, and recent activity

### 6. Professional GUI
* Responsive Tkinter interface with themed widgets
* Dialog-driven workflows and inline validation
* Keyboard shortcuts and accessibility hints

---

## Project Snapshot

```
library-management-system/
├── src/
│   ├── controllers/      # Application logic
│   ├── models/           # Database models
│   ├── views/            # Tkinter UI components
│   ├── utils/            # Helpers & utilities
│   ├── config/           # Settings
│   └── main.py           # Entry point
├── data/                 # SQLite DB (auto-created)
├── docs/                 # Extra documentation / images
├── tests/                # Pytest test-suite
├── requirements.txt      # Runtime dependencies
├── LICENSE               # MIT License
├── README.md             # You are here
└── .gitignore
```

---

## Quick Start

### 1. Prerequisites
* Python 3.8 or newer
* SQLite 3 (bundled with Python)

### 2. Installation
```bash
# Clone repository
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system

# Optional – create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. First Run
```bash
python src/main.py
```
The first launch will create `data/library_management.db` and seed default users.

### 4. Default Credentials (change immediately!)

| Role | Username | Password |
|------|----------|----------|
| Administrator | `admin` | `admin123` |
| Librarian     | `librarian` | `lib123` |

---

## Usage Overview

1. **Log in** using an admin or librarian account.
2. **Navigate** via the sidebar dashboard:
   * Books → add / edit / withdraw titles
   * Members → register / update / deactivate members
   * Transactions → issue / renew / return books
   * Reports → view statistics and overdue lists
3. **Admins** can open *Settings → Users* to add or disable librarian accounts and change system limits.

For full instructions, screenshots, and troubleshooting, see the `docs/` folder or the project Wiki.

---

## Development

```bash
# Install dev requirements and run tests
pip install -r requirements.txt
pytest -v  # run unit-tests
```
Styling is enforced with *flake8* and *black*; pre-commit hooks are recommended.

### Contributing
Please read **CONTRIBUTING.md** for the pull-request workflow, code style guidelines, and the project Code of Conduct.

---

## License

This project is released under the MIT License—see **LICENSE** for details.

---

## Maintainer

[rishabh](https://github.com/027-rishabh) – feel free to open an issue for support or feature requests.
