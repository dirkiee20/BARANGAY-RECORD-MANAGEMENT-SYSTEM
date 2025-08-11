record_management_system/
│
├── app/                     # Main application
│   ├── __init__.py           # Initialize Flask app & extensions
│   ├── routes.py             # All routes/endpoints
│   ├── models.py             # Database models (SQLAlchemy)
│   ├── forms.py              # Forms (WTForms or Flask-WTF)
│   ├── utils.py              # Helper functions
│   ├── static/               # CSS, JS, Images
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/            # HTML templates (Jinja2)
│       ├── base.html
│       ├── dashboard.html
│       └── records.html
│
├── migrations/               # Database migration files (Flask-Migrate)
├── config.py                  # Config settings (DB URL, secret key, etc.)
├── run.py                     # Entry point to run Flask app
├── requirements.txt           # Dependencies
└── README.md