# 🎓 EduMIS – Student Management Information System

A multimodal biometric-enabled student information system built with Python and Tkinter. Manage students, teachers, grades, attendance, assignments, fees, library resources, and school notices with an intuitive GUI.

## 📋 Features

### 🔐 Authentication
- **Username/Password Login & Sign Up** – Traditional authentication with hashed passwords
- **Voice Authentication** – Log in using voice passphrase recognition
- **Fingerprint Authentication** – Biometric fingerprint login with PIN-based verification
- **Role-Based Access** – Three user roles: Student, Teacher, and Admin

### 👨‍🎓 Student Dashboard
- **📊 Grades** – View subject-wise grades and overall average
- **📅 Attendance** – Track attendance records with daily status
- **📝 Assignments** – Monitor assignment deadlines and submission status
- **💳 Fee Status** – Check fee balance and payment history
- **📚 Library** – Browse available books and manage borrowing/returns
- **📢 Notices** – Read school announcements and updates
- **🏠 Home** – Quick overview with key metrics

### 👨‍🏫 Teacher Dashboard
- **👨‍🎓 My Students** – List and manage assigned students
- **📝 Mark Grades** – Enter and update student grades by subject
- **📅 Mark Attendance** – Record daily attendance for students
- **📢 Post Notices** – Publish school announcements
- **📚 Library Access** – View and manage library resources

### 🛠 Admin Dashboard
- **👤 Manage Users** – View, delete, and manage all user accounts
- **💳 Fee Management** – Track student fees and record payments
- **📢 Post Notices** – Publish school-wide announcements
- **📚 Library Admin** – Add/manage library books
- **📊 Reports** – Generate school-wide reports with student summaries

### 💾 Data Management
- **JSON-based Storage** – Persistent data storage with automatic serialization
- **Multiple Modules:**
  - Student grades by subject
  - Attendance tracking
  - Assignment submission tracking
  - Fee payments and history
  - Library book inventory
  - School notices and announcements
  - Class-to-teacher mappings

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Required packages (see Installation)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/elvismungai15-maker/Student-MIS.py.git
   cd Student-MIS.py
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or manually install:
   ```bash
   pip install Pillow werkzeug SpeechRecognition
   ```

3. **Run the application:**
   ```bash
   python studentmis.py
   ```

### Demo Credentials
The application seeds demo data on first run. Log in with:

| Username | Password | Role |
|----------|----------|------|
| alice | pass123 | Student |
| bob | pass123 | Student |
| mr_john | teach123 | Teacher |
| admin | admin123 | Admin |

## 📁 Project Structure

```
Student-MIS.py/
├── studentmis.py          # Main application file
├── data/                  # Data directory (auto-created)
│   ├── users.json         # User accounts and credentials
│   └── mis.json           # MIS data (grades, attendance, etc.)
└── README.md              # This file
```

## 🎨 UI Design

- **Modern Color Scheme:** Blue primary colors with intuitive card-based layouts
- **Responsive Layout:** Two-panel design with scrollable content area
- **Sidebar Navigation:** Quick access to all features with role-specific menus
- **Card Components:** Clean presentation of data in styled cards
- **Treeview Tables:** Professional data tables for grades, attendance, students, etc.

## 🔧 Configuration

### Colors & Styling
Colors and fonts can be customized by editing constants at the top of `studentmis.py`:
```python
C_PRIMARY   = "#1565C0"    # Primary blue
C_SUCCESS   = "#2E7D32"    # Green
C_DANGER    = "#C62828"    # Red
C_WARN      = "#F57F17"    # Orange
```

### Data Directory
By default, data is stored in a `data/` folder. Modify the path:
```python
DATA_DIR = "data"
```

## 📊 Core Data Models

### Users
```json
{
  "username": {
    "password": "hashed_password",
    "role": "student|teacher|admin",
    "full_name": "Full Name",
    "voice": "optional_voice_passphrase",
    "fingerprint": "optional_hashed_fingerprint"
  }
}
```

### MIS
```json
{
  "subjects": ["Mathematics", "English", ...],
  "grades": { "student": { "subject": score } },
  "attendance": { "student": { "date": "Present|Absent" } },
  "assignments": { "student": [{ "title", "due", "submitted", "score" }] },
  "notices": [{ "title", "body", "date", "author" }],
  "fees": { "student": { "paid", "total", "history" } },
  "classes": { "teacher": ["student1", "student2"] },
  "library": [{ "title", "author", "available", "borrower" }]
}
```

## 🔒 Security

- **Password Hashing:** Uses `werkzeug.security` for secure password storage
- **Voice Passphrase:** Simple text-based voice matching (can be enhanced)
- **Fingerprint PIN:** Hashed PIN verification for fingerprint authentication
- **Role-Based Access Control:** Different features based on user role

*Note: This is a demo application. For production use, implement stronger security measures and database encryption.*

## 🎤 Voice & Biometric Features

- **Voice Recognition:** Powered by `SpeechRecognition` library with Google API
- **Voice Login:** Users can log in by speaking their registered passphrase
- **Fingerprint Setup:** PIN-based fingerprint registration
- **Biometric Fallback:** Users can fall back to traditional login if biometric fails

## 🐛 Known Limitations

- Voice recognition requires internet connection (uses Google API)
- Fingerprint uses PIN simulation rather than true biometric hardware
- Single-user instance (no concurrent user support)
- No database backend (JSON-based storage for demo purposes)

## 🚧 Future Enhancements

- [ ] Database backend (PostgreSQL/MySQL)
- [ ] Real fingerprint scanner integration
- [ ] Email notifications for fees/assignments
- [ ] Mobile app integration
- [ ] Advanced reporting and analytics
- [ ] Student portal for self-service features
- [ ] Timetable management
- [ ] Exam scheduling system

## 📄 License

This project is open-source. Feel free to use and modify it for educational purposes.

## 👨‍💻 Author

**Elvis Mungai**  
GitHub: [@elvismungai15-maker](https://github.com/elvismungai15-maker)

## 📞 Support

For issues, feature requests, or questions, please open an issue on GitHub.

---

**Made with ❤️ for educational management systems**
