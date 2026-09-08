import os
import json
import datetime
import random
from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from werkzeug.security import generate_password_hash, check_password_hash
import speech_recognition as sr

# -----------------------------
# PATH SETUP
# -----------------------------
DATA_DIR = "data"
USER_DB  = os.path.join(DATA_DIR, "users.json")
MIS_DB   = os.path.join(DATA_DIR, "mis.json")

# -----------------------------
# COLOURS / STYLE CONSTANTS
# -----------------------------
C_BG        = "#F0F4F8"
C_PRIMARY   = "#1565C0"
C_ACCENT    = "#42A5F5"
C_SUCCESS   = "#2E7D32"
C_WARN      = "#F57F17"
C_DANGER    = "#C62828"
C_SIDEBAR   = "#1A237E"
C_SIDEBAR_T = "#FFFFFF"
C_CARD      = "#FFFFFF"
C_TEXT      = "#212121"
C_MUTED     = "#757575"
FONT_H1     = ("Arial", 22, "bold")
FONT_H2     = ("Arial", 16, "bold")
FONT_H3     = ("Arial", 13, "bold")
FONT_BODY   = ("Arial", 12)
FONT_SMALL  = ("Arial", 10)
BTN_CFG     = dict(font=("Arial", 12), relief=FLAT, cursor="hand2", padx=10, pady=6)

# -----------------------------
# LOAD / SAVE HELPERS
# -----------------------------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

users = load_json(USER_DB, {})
mis   = load_json(MIS_DB, {
    "subjects": ["Mathematics", "English", "Physics", "Chemistry", "Computer Science", "Biology"],
    "grades": {},        # {student: {subject: grade}}
    "attendance": {},    # {student: {date: present/absent}}
    "assignments": {},   # {student: [{title, due, submitted, score}]}
    "notices": [],       # [{title, body, date, author}]
    "fees": {},          # {student: {paid, total, history}}
    "classes": {},       # {teacher: [student, ...]}
    "timetable": {},     # {class_name: [{day, time, subject, teacher}]}
    "library": [],       # [{title, author, available, borrower}]
})
current_user = None

def save_all():
    save_json(USER_DB, users)
    save_json(MIS_DB, mis)

# -----------------------------
# UTIL
# -----------------------------
def clear_window():
    for w in root.winfo_children():
        w.destroy()

def simple_input(prompt, title="Input"):
    win = Toplevel(root)
    win.title(title)
    win.geometry("340x120")
    win.configure(bg=C_BG)
    Label(win, text=prompt, font=FONT_BODY, bg=C_BG).pack(pady=8)
    e = Entry(win, font=FONT_BODY, width=28)
    e.pack(pady=4)
    result = []
    def ok():
        result.append(e.get())
        win.destroy()
    Button(win, text="OK", command=ok, bg=C_PRIMARY, fg="white", **BTN_CFG).pack(pady=6)
    root.wait_window(win)
    return result[0] if result else ""

def card_frame(parent, **kw):
    """A styled white card."""
    f = Frame(parent, bg=C_CARD, relief=FLAT, bd=0, highlightthickness=1,
              highlightbackground="#DDEEFF", **kw)
    return f

def section_label(parent, text):
    Label(parent, text=text, font=FONT_H2, bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=20, pady=(16, 4))

def divider(parent):
    Frame(parent, bg="#DDEEFF", height=1).pack(fill=X, padx=20, pady=4)

def today():
    return datetime.date.today().isoformat()

def seed_demo_data():
    """Seed some demo data for a fresh install so the UI has content."""
    if not users:
        demo = [
            ("alice",   "pass123", "student"),
            ("bob",     "pass123", "student"),
            ("mr_john", "teach123", "teacher"),
            ("admin",   "admin123", "admin"),
        ]
        for u, p, r in demo:
            users[u] = {"password": generate_password_hash(p), "role": r,
                        "full_name": u.replace("_", " ").title()}
        save_json(USER_DB, users)

    subjects = mis["subjects"]
    for s in ["alice", "bob"]:
        if s not in mis["grades"]:
            mis["grades"][s] = {sub: random.randint(55, 98) for sub in subjects}
        if s not in mis["attendance"]:
            mis["attendance"][s] = {}
            base = datetime.date.today() - datetime.timedelta(days=14)
            for i in range(14):
                d = (base + datetime.timedelta(days=i)).isoformat()
                mis["attendance"][s][d] = "Present" if random.random() > 0.15 else "Absent"
        if s not in mis["assignments"]:
            mis["assignments"][s] = [
                {"title": "Algebra Homework", "due": "2025-04-10", "submitted": True,  "score": 88},
                {"title": "Essay Writing",    "due": "2025-04-15", "submitted": True,  "score": 76},
                {"title": "Lab Report",       "due": "2025-04-22", "submitted": False, "score": None},
            ]
        if s not in mis["fees"]:
            mis["fees"][s] = {"paid": 45000, "total": 60000,
                              "history": [{"date": "2025-03-01", "amount": 20000, "ref": "KES-001"},
                                          {"date": "2025-04-01", "amount": 25000, "ref": "KES-002"}]}
    if not mis["notices"]:
        mis["notices"] = [
            {"title": "End of Term Exam Schedule",
             "body":  "Exams start May 12. Please check timetable.",
             "date":  "2025-04-20", "author": "admin"},
            {"title": "School Fee Reminder",
             "body":  "Balance fees due by April 30.",
             "date":  "2025-04-18", "author": "admin"},
        ]
    if "mr_john" not in mis["classes"]:
        mis["classes"]["mr_john"] = ["alice", "bob"]
    if not mis["library"]:
        mis["library"] = [
            {"title": "Python Programming", "author": "Guido", "available": True,  "borrower": None},
            {"title": "Data Structures",    "author": "Cormen","available": False, "borrower": "alice"},
            {"title": "Calculus Vol.1",     "author": "Spivak","available": True,  "borrower": None},
            {"title": "English Grammar",    "author": "Murphy","available": True,  "borrower": None},
        ]
    save_all()

seed_demo_data()

# ===========================================================
# BIOMETRIC  (unchanged logic, kept intact)
# ===========================================================

def record_voice(username):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Voice", "Say your passphrase")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio).lower()
            users[username]["voice"] = text
            save_json(USER_DB, users)
            messagebox.showinfo("Saved", f"Voice saved: {text}")
        except:
            messagebox.showerror("Error", "Voice capture failed")

def voice_login():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Voice Login", "Speak to login")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio).lower()
            for u in users:
                if users[u].get("voice") == text:
                    login_success(u)
                    return
        except:
            pass
    messagebox.showerror("Error", "Voice not recognized")

def fingerprint_login():
    username = entry_user.get().strip()

    if username not in users:
        messagebox.showerror("Error", "Enter username first")
        return

    if "fingerprint" not in users[username]:
        messagebox.showerror("Error", "No fingerprint registered")
        return

    pin = simple_input("Scan fingerprint (enter PIN):", "Fingerprint Login")

    if check_password_hash(users[username]["fingerprint"], pin):
        messagebox.showinfo("Success", "Fingerprint accepted")
        login_success(username)
    else:
        messagebox.showerror("Error", "Fingerprint failed")

def register_fingerprint(username):
    pin = simple_input("Set your fingerprint PIN:", "Fingerprint Setup")
    if not pin:
        messagebox.showerror("Error", "PIN cannot be empty")
        return

    users[username]["fingerprint"] = generate_password_hash(pin)
    save_json(USER_DB, users)
    messagebox.showinfo("Success", "Fingerprint registered!")

# ===========================================================
# LOGIN / SIGNUP
# ===========================================================
def signup():
    u = entry_user.get().strip()
    p = entry_pass.get().strip()
    role = role_var.get()
    if not u or not p:
        messagebox.showerror("Error", "Username and password required"); return
    if u in users:
        messagebox.showerror("Error", "User already exists"); return
    users[u] = {"password": generate_password_hash(p), "role": role,
                "full_name": u.replace("_", " ").title()}
    save_json(USER_DB, users)
    messagebox.showinfo("Success", f"Account created for {u} as {role}!")

def login():
    u = entry_user.get().strip()
    p = entry_pass.get().strip()
    if u in users and check_password_hash(users[u]["password"], p):
        login_success(u)
    else:
        messagebox.showerror("Error", "Invalid credentials")

def login_success(username):
    global current_user
    current_user = username
    show_dashboard()

# ===========================================================
# SHARED DASHBOARD SHELL  (sidebar + content area)
# ===========================================================
content_frame = None   # global reference to right panel

def build_shell(menu_items):
    """
    Builds a two-panel layout: left sidebar with menu buttons,
    right scrollable content area.
    menu_items: list of (label, command_fn)
    """
    global content_frame
    clear_window()
    root.configure(bg=C_SIDEBAR)

    # ---- Sidebar ----
    sidebar = Frame(root, bg=C_SIDEBAR, width=170)
    sidebar.pack(side=LEFT, fill=Y)
    sidebar.pack_propagate(False)

    role = users[current_user]["role"].upper()
    Label(sidebar, text="🎓 EduMIS", font=("Arial", 15, "bold"),
          bg=C_SIDEBAR, fg="#90CAF9").pack(pady=(20, 4))
    Label(sidebar, text=role, font=FONT_SMALL, bg=C_SIDEBAR, fg="#B0BEC5").pack()
    Frame(sidebar, bg="#3949AB", height=1).pack(fill=X, padx=10, pady=10)

    name = users[current_user].get("full_name", current_user)
    Label(sidebar, text=name[:18], font=FONT_SMALL, bg=C_SIDEBAR,
          fg="#E3F2FD", wraplength=150).pack(padx=8)
    Frame(sidebar, bg="#3949AB", height=1).pack(fill=X, padx=10, pady=10)

    for label, cmd in menu_items:
        btn = Button(sidebar, text=label, command=cmd,
                     bg=C_SIDEBAR, fg=C_SIDEBAR_T, activebackground="#283593",
                     activeforeground="white", font=("Arial", 11),
                     relief=FLAT, anchor="w", padx=14, pady=8, cursor="hand2")
        btn.pack(fill=X)

    Frame(sidebar, bg="#3949AB", height=1).pack(fill=X, padx=10, pady=10)
    Button(sidebar, text="⬅  Logout", command=main_screen,
           bg="#C62828", fg="white", font=("Arial", 11),
           relief=FLAT, anchor="w", padx=14, pady=8, cursor="hand2").pack(fill=X)

    # ---- Content area ----
    outer = Frame(root, bg=C_BG)
    outer.pack(side=LEFT, fill=BOTH, expand=True)

    canvas = Canvas(outer, bg=C_BG, highlightthickness=0)
    vsb = Scrollbar(outer, orient=VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    content_frame = Frame(canvas, bg=C_BG)
    win_id = canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def on_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(win_id, width=canvas.winfo_width())

    content_frame.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

    # Mouse-wheel scrolling
    def on_mousewheel(e):
        canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

def clear_content():
    for w in content_frame.winfo_children():
        w.destroy()

# ===========================================================
# STUDENT DASHBOARD
# ===========================================================
def show_dashboard():
    role = users[current_user]["role"]
    if role == "student":
        show_student_dashboard()
    elif role == "teacher":
        show_teacher_dashboard()
    else:
        show_admin_dashboard()

# ---- Student ----
def show_student_dashboard():
    menu = [
        ("🏠  Home",        s_home),
        ("📊  My Grades",   s_grades),
        ("📅  Attendance",  s_attendance),
        ("📝  Assignments", s_assignments),
        ("💳  Fee Status",  s_fees),
        ("📚  Library",     s_library),
        ("📢  Notices",     s_notices),
    ]
    build_shell(menu)
    s_home()

def s_home():
    clear_content()
    name = users[current_user].get("full_name", current_user)
    Label(content_frame, text=f"Welcome back, {name} 👋",
          font=FONT_H1, bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=20, pady=(20, 2))
    Label(content_frame, text=today(), font=FONT_SMALL, bg=C_BG, fg=C_MUTED).pack(anchor="w", padx=20)
    divider(content_frame)

    # Summary cards
    cards_row = Frame(content_frame, bg=C_BG)
    cards_row.pack(fill=X, padx=20, pady=10)

    grades = mis["grades"].get(current_user, {})
    avg = round(sum(grades.values()) / len(grades)) if grades else 0

    att = mis["attendance"].get(current_user, {})
    present = sum(1 for v in att.values() if v == "Present")
    att_pct = round(present / len(att) * 100) if att else 0

    assignments = mis["assignments"].get(current_user, [])
    pending = sum(1 for a in assignments if not a["submitted"])

    fee_data = mis["fees"].get(current_user, {"paid": 0, "total": 0})
    balance  = fee_data["total"] - fee_data["paid"]

    def stat_card(parent, label, value, color, sub=""):
        c = card_frame(parent)
        c.pack(side=LEFT, expand=True, fill=BOTH, padx=6, pady=4)
        Label(c, text=label, font=FONT_SMALL, bg=C_CARD, fg=C_MUTED).pack(padx=12, pady=(10, 0), anchor="w")
        Label(c, text=str(value), font=("Arial", 26, "bold"), bg=C_CARD, fg=color).pack(padx=12, anchor="w")
        if sub:
            Label(c, text=sub, font=FONT_SMALL, bg=C_CARD, fg=C_MUTED).pack(padx=12, pady=(0, 10), anchor="w")
        else:
            Label(c, text=" ", font=FONT_SMALL, bg=C_CARD).pack(padx=12, pady=(0, 10))

    stat_card(cards_row, "Average Grade",  f"{avg}%",    C_PRIMARY,  "across all subjects")
    stat_card(cards_row, "Attendance",     f"{att_pct}%",C_SUCCESS,  f"{present}/{len(att)} days")
    stat_card(cards_row, "Pending Tasks",  pending,       C_WARN,     "assignments due")
    stat_card(cards_row, "Fee Balance",    f"KES {balance:,}", C_DANGER, "outstanding")

    # Recent notices
    section_label(content_frame, "📢 Recent Notices")
    for n in mis["notices"][:3]:
        c = card_frame(content_frame)
        c.pack(fill=X, padx=20, pady=4)
        Label(c, text=n["title"], font=FONT_H3, bg=C_CARD, fg=C_PRIMARY).pack(anchor="w", padx=12, pady=(8, 0))
        Label(c, text=n["body"],  font=FONT_BODY, bg=C_CARD, fg=C_TEXT, wraplength=540, justify=LEFT).pack(anchor="w", padx=12)
        Label(c, text=f"Posted: {n['date']} by {n['author']}", font=FONT_SMALL, bg=C_CARD, fg=C_MUTED).pack(anchor="w", padx=12, pady=(0, 8))

def s_grades():
    clear_content()
    section_label(content_frame, "📊 My Grades")
    divider(content_frame)
    grades = mis["grades"].get(current_user, {})
    if not grades:
        Label(content_frame, text="No grades recorded yet.", font=FONT_BODY, bg=C_BG, fg=C_MUTED).pack(padx=20, pady=10)
        return

    # Table
    c = card_frame(content_frame)
    c.pack(fill=X, padx=20, pady=10)
    cols = ("Subject", "Grade (%)", "Remark")
    tv = ttk.Treeview(c, columns=cols, show="headings", height=len(grades))
    for col in cols:
        tv.heading(col, text=col)
        tv.column(col, width=160, anchor="center")
    for sub, g in grades.items():
        remark = "Excellent" if g >= 80 else "Good" if g >= 65 else "Average" if g >= 50 else "Fail"
        tv.insert("", END, values=(sub, g, remark))
    tv.pack(fill=X, padx=10, pady=10)

    avg = round(sum(grades.values()) / len(grades))
    Label(c, text=f"Overall Average: {avg}%", font=FONT_H3, bg=C_CARD, fg=C_PRIMARY).pack(anchor="e", padx=16, pady=(0, 10))

def s_attendance():
    clear_content()
    section_label(content_frame, "📅 Attendance Record")
    divider(content_frame)
    att = mis["attendance"].get(current_user, {})
    present = sum(1 for v in att.values() if v == "Present")
    pct = round(present / len(att) * 100) if att else 0

    row = Frame(content_frame, bg=C_BG)
    row.pack(padx=20, pady=6)
    for lbl, val, col in [("Total Days", len(att), C_PRIMARY),
                           ("Present",    present,  C_SUCCESS),
                           ("Absent",     len(att)-present, C_DANGER),
                           ("Rate",       f"{pct}%", C_WARN)]:
        c = card_frame(row)
        c.pack(side=LEFT, padx=8)
        Label(c, text=lbl, font=FONT_SMALL, bg=C_CARD, fg=C_MUTED).pack(padx=16, pady=(8, 0))
        Label(c, text=str(val), font=("Arial", 22, "bold"), bg=C_CARD, fg=col).pack(padx=16, pady=(0, 8))

    c2 = card_frame(content_frame)
    c2.pack(fill=X, padx=20, pady=10)
    cols = ("Date", "Status")
    tv = ttk.Treeview(c2, columns=cols, show="headings", height=min(15, len(att)))
    for col in cols:
        tv.heading(col, text=col)
        tv.column(col, width=200, anchor="center")
    for d, st in sorted(att.items(), reverse=True):
        tv.insert("", END, values=(d, st),
                  tags=(st.lower(),))
    tv.tag_configure("absent", foreground=C_DANGER)
    tv.tag_configure("present", foreground=C_SUCCESS)
    tv.pack(fill=X, padx=10, pady=10)

def s_assignments():
    clear_content()
    section_label(content_frame, "📝 Assignments")
    divider(content_frame)
    assignments = mis["assignments"].get(current_user, [])
    if not assignments:
        Label(content_frame, text="No assignments found.", font=FONT_BODY, bg=C_BG, fg=C_MUTED).pack(padx=20, pady=10)
        return
    for a in assignments:
        c = card_frame(content_frame)
        c.pack(fill=X, padx=20, pady=6)
        status_col = C_SUCCESS if a["submitted"] else C_WARN
        status_txt = f"Submitted  •  Score: {a['score']}%" if a["submitted"] else "⏳ Pending"
        Label(c, text=a["title"], font=FONT_H3, bg=C_CARD, fg=C_TEXT).pack(anchor="w", padx=12, pady=(8, 0))
        Label(c, text=f"Due: {a['due']}", font=FONT_SMALL, bg=C_CARD, fg=C_MUTED).pack(anchor="w", padx=12)
        Label(c, text=status_txt, font=FONT_BODY, bg=C_CARD, fg=status_col).pack(anchor="w", padx=12, pady=(0, 8))

def s_fees():
    clear_content()
    section_label(content_frame, "💳 Fee Statement")
    divider(content_frame)
    fee = mis["fees"].get(current_user, {"paid": 0, "total": 0, "history": []})
    balance = fee["total"] - fee["paid"]
    pct = round(fee["paid"] / fee["total"] * 100) if fee["total"] else 0

    row = Frame(content_frame, bg=C_BG)
    row.pack(padx=20, pady=10)
    for lbl, val, col in [("Total Fees",  f"KES {fee['total']:,}",   C_TEXT),
                           ("Paid",        f"KES {fee['paid']:,}",    C_SUCCESS),
                           ("Balance Due", f"KES {balance:,}",        C_DANGER),
                           ("Paid %",      f"{pct}%",                  C_PRIMARY)]:
        c = card_frame(row)
        c.pack(side=LEFT, padx=8)
        Label(c, text=lbl, font=FONT_SMALL, bg=C_CARD, fg=C_MUTED).pack(padx=16, pady=(8, 0))
        Label(c, text=val, font=("Arial", 16, "bold"), bg=C_CARD, fg=col).pack(padx=16, pady=(0, 8))

    section_label(content_frame, "Payment History")
    c2 = card_frame(content_frame)
    c2.pack(fill=X, padx=20, pady=6)
    cols = ("Date", "Amount (KES)", "Reference")
    tv = ttk.Treeview(c2, columns=cols, show="headings", height=len(fee["history"]))
    for col in cols:
        tv.heading(col, text=col); tv.column(col, width=160, anchor="center")
    for h in fee["history"]:
        tv.insert("", END, values=(h["date"], f"{h['amount']:,}", h["ref"]))
    tv.pack(fill=X, padx=10, pady=10)

def s_library():
    clear_content()
    section_label(content_frame, "📚 Library")
    divider(content_frame)

    c = card_frame(content_frame)
    c.pack(fill=X, padx=20, pady=10)
    cols = ("Title", "Author", "Status", "Borrower")
    tv = ttk.Treeview(c, columns=cols, show="headings", height=len(mis["library"]))
    for col in cols:
        tv.heading(col, text=col)
        tv.column(col, width=140, anchor="center")
    for b in mis["library"]:
        status  = "Available" if b["available"] else "Borrowed"
        borrower = b["borrower"] or "-"
        tv.insert("", END, values=(b["title"], b["author"], status, borrower),
                  tags=("avail" if b["available"] else "borrowed",))
    tv.tag_configure("avail",    foreground=C_SUCCESS)
    tv.tag_configure("borrowed", foreground=C_DANGER)
    tv.pack(fill=X, padx=10, pady=10)

    # Borrow / return button
    def borrow_return():
        sel = tv.focus()
        if not sel:
            messagebox.showwarning("Select", "Please select a book first."); return
        vals = tv.item(sel)["values"]
        title = vals[0]
        for b in mis["library"]:
            if b["title"] == title:
                if b["available"]:
                    b["available"] = False
                    b["borrower"]  = current_user
                    messagebox.showinfo("Success", f"You borrowed '{title}'")
                elif b["borrower"] == current_user:
                    b["available"] = True
                    b["borrower"]  = None
                    messagebox.showinfo("Success", f"You returned '{title}'")
                else:
                    messagebox.showwarning("Unavailable", "Book is borrowed by someone else.")
                    return
                save_all()
                s_library()
                return

    Button(content_frame, text="Borrow / Return Selected", command=borrow_return,
           bg=C_PRIMARY, fg="white", **BTN_CFG).pack(padx=20, pady=6, anchor="w")

def s_notices():
    clear_content()
    section_label(content_frame, "📢 School Notices")
    divider(content_frame)
    if not mis["notices"]:
        Label(content_frame, text="No notices at the moment.", font=FONT_BODY, bg=C_BG, fg=C_MUTED).pack(padx=20)
        return
    for n in mis["notices"]:
        c = card_frame(content_frame)
        c.pack(fill=X, padx=20, pady=6)
        Label(c, text=n["title"], font=FONT_H3, bg=C_CARD, fg=C_PRIMARY).pack(anchor="w", padx=12, pady=(10, 0))
        Label(c, text=n["body"],  font=FONT_BODY, bg=C_CARD, fg=C_TEXT,
              wraplength=540, justify=LEFT).pack(anchor="w", padx=12, pady=4)
        Label(c, text=f"📅 {n['date']}  |  {n['author']}", font=FONT_SMALL,
              bg=C_CARD, fg=C_MUTED).pack(anchor="w", padx=12, pady=(0, 10))

# ===========================================================
# TEACHER DASHBOARD
# ===========================================================
def show_teacher_dashboard():
    menu = [
        ("🏠  Home",           t_home),
        ("👨‍🎓  My Students",    t_students),
        ("📝  Mark Grades",     t_mark_grades),
        ("📅  Mark Attendance", t_mark_attendance),
        ("📢  Post Notice",     t_post_notice),
        ("📚  Library",         s_library),
        ("📢  Notices",         s_notices),
    ]
    build_shell(menu)
    t_home()

def t_home():
    clear_content()
    name = users[current_user].get("full_name", current_user)
    Label(content_frame, text=f"Hello, {name} 👋",
          font=FONT_H1, bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=20, pady=(20, 2))
    Label(content_frame, text=today(), font=FONT_SMALL, bg=C_BG, fg=C_MUTED).pack(anchor="w", padx=20)
    divider(content_frame)

    my_students = mis["classes"].get(current_user, [])
    row = Frame(content_frame, bg=C_BG)
    row.pack(padx=20, pady=10)
    for lbl, val, col in [("My Students", len(my_students), C_PRIMARY),
                           ("Subjects", len(mis["subjects"]), C_SUCCESS),
                           ("Notices Posted",
                            sum(1 for n in mis["notices"] if n["author"] == current_user),
                            C_WARN)]:
        c = card_frame(row)
        c.pack(side=LEFT, padx=8)
        Label(c, text=lbl, font=FONT_SMALL, bg=C_CARD, fg=C_MUTED).pack(padx=16, pady=(8, 0))
        Label(c, text=str(val), font=("Arial", 26, "bold"), bg=C_CARD, fg=col).pack(padx=16, pady=(0, 8))

    section_label(content_frame, "My Students")
    for s in my_students:
        c = card_frame(content_frame)
        c.pack(fill=X, padx=20, pady=4)
        sname = users.get(s, {}).get("full_name", s)
        grades = mis["grades"].get(s, {})
        avg    = round(sum(grades.values()) / len(grades)) if grades else "—"
        att    = mis["attendance"].get(s, {})
        pct    = round(sum(1 for v in att.values() if v=="Present") / len(att)*100) if att else "—"
        Label(c, text=f"👤  {sname}", font=FONT_H3, bg=C_CARD, fg=C_TEXT).pack(side=LEFT, padx=12, pady=8)
        Label(c, text=f"Avg: {avg}%   Att: {pct}%", font=FONT_BODY, bg=C_CARD, fg=C_MUTED).pack(side=RIGHT, padx=12)

def t_students():
    clear_content()
    section_label(content_frame, "👨‍🎓 My Students")
    divider(content_frame)
    my_students = mis["classes"].get(current_user, [])
    c = card_frame(content_frame)
    c.pack(fill=X, padx=20, pady=10)
    cols = ("Username", "Full Name", "Avg Grade", "Attendance %")
    tv = ttk.Treeview(c, columns=cols, show="headings", height=max(5, len(my_students)))
    for col in cols:
        tv.heading(col, text=col); tv.column(col, width=150, anchor="center")
    for s in my_students:
        sname  = users.get(s, {}).get("full_name", s)
        grades = mis["grades"].get(s, {})
        avg    = round(sum(grades.values()) / len(grades)) if grades else 0
        att    = mis["attendance"].get(s, {})
        pct    = round(sum(1 for v in att.values() if v=="Present") / len(att)*100) if att else 0
        tv.insert("", END, values=(s, sname, f"{avg}%", f"{pct}%"))
    tv.pack(fill=X, padx=10, pady=10)

def t_mark_grades():
    clear_content()
    section_label(content_frame, "📝 Mark / Update Grades")
    divider(content_frame)
    my_students = mis["classes"].get(current_user, [])

    Label(content_frame, text="Select student:", font=FONT_BODY, bg=C_BG, fg=C_TEXT).pack(anchor="w", padx=20, pady=(8, 0))
    stu_var = StringVar(value=my_students[0] if my_students else "")
    OptionMenu(content_frame, stu_var, *my_students).pack(anchor="w", padx=20, pady=4)

    Label(content_frame, text="Select subject:", font=FONT_BODY, bg=C_BG, fg=C_TEXT).pack(anchor="w", padx=20, pady=(8, 0))
    sub_var = StringVar(value=mis["subjects"][0])
    OptionMenu(content_frame, sub_var, *mis["subjects"]).pack(anchor="w", padx=20, pady=4)

    Label(content_frame, text="Enter grade (0–100):", font=FONT_BODY, bg=C_BG, fg=C_TEXT).pack(anchor="w", padx=20, pady=(8, 0))
    grade_entry = Entry(content_frame, font=FONT_BODY, width=10)
    grade_entry.pack(anchor="w", padx=20, pady=4)

    def save_grade():
        try:
            g = int(grade_entry.get())
            assert 0 <= g <= 100
        except:
            messagebox.showerror("Error", "Enter a valid grade 0–100"); return
        s = stu_var.get()
        sub = sub_var.get()
        mis["grades"].setdefault(s, {})[sub] = g
        save_all()
        messagebox.showinfo("Saved", f"Grade {g} saved for {s} in {sub}")

    Button(content_frame, text="💾 Save Grade", command=save_grade,
           bg=C_SUCCESS, fg="white", **BTN_CFG).pack(anchor="w", padx=20, pady=10)

def t_mark_attendance():
    clear_content()
    section_label(content_frame, "📅 Mark Attendance")
    divider(content_frame)
    my_students = mis["classes"].get(current_user, [])
    Label(content_frame, text=f"Date: {today()}", font=FONT_BODY, bg=C_BG, fg=C_MUTED).pack(anchor="w", padx=20, pady=4)

    vars_map = {}
    for s in my_students:
        sname = users.get(s, {}).get("full_name", s)
        row = Frame(content_frame, bg=C_BG)
        row.pack(fill=X, padx=20, pady=3)
        Label(row, text=sname, font=FONT_BODY, bg=C_BG, fg=C_TEXT, width=20, anchor="w").pack(side=LEFT)
        v = StringVar(value="Present")
        vars_map[s] = v
        OptionMenu(row, v, "Present", "Absent").pack(side=LEFT, padx=8)

    def save_attendance():
        for s, v in vars_map.items():
            mis["attendance"].setdefault(s, {})[today()] = v.get()
        save_all()
        messagebox.showinfo("Saved", "Attendance saved for today!")

    Button(content_frame, text="💾 Save Attendance", command=save_attendance,
           bg=C_SUCCESS, fg="white", **BTN_CFG).pack(anchor="w", padx=20, pady=12)

def t_post_notice():
    clear_content()
    section_label(content_frame, "📢 Post a Notice")
    divider(content_frame)
    Label(content_frame, text="Title:", font=FONT_BODY, bg=C_BG).pack(anchor="w", padx=20, pady=(8, 0))
    title_e = Entry(content_frame, font=FONT_BODY, width=50)
    title_e.pack(anchor="w", padx=20, pady=4)
    Label(content_frame, text="Body:", font=FONT_BODY, bg=C_BG).pack(anchor="w", padx=20, pady=(8, 0))
    body_e = Text(content_frame, font=FONT_BODY, width=52, height=5)
    body_e.pack(anchor="w", padx=20, pady=4)

    def post():
        t = title_e.get().strip()
        b = body_e.get("1.0", END).strip()
        if not t or not b:
            messagebox.showerror("Error", "Title and body required"); return
        mis["notices"].insert(0, {"title": t, "body": b, "date": today(), "author": current_user})
        save_all()
        messagebox.showinfo("Posted", "Notice posted successfully!")
        title_e.delete(0, END)
        body_e.delete("1.0", END)

    Button(content_frame, text="📢 Post Notice", command=post,
           bg=C_PRIMARY, fg="white", **BTN_CFG).pack(anchor="w", padx=20, pady=10)

# ===========================================================
# ADMIN DASHBOARD
# ===========================================================
def show_admin_dashboard():
    menu = [
        ("🏠  Home",           a_home),
        ("👤  Manage Users",   a_manage_users),
        ("💳  Fee Management", a_fees),
        ("📢  Post Notice",    t_post_notice),
        ("📚  Library Admin",  a_library),
        ("📊  Reports",        a_reports),
        ("📢  Notices",        s_notices),
    ]
    build_shell(menu)
    a_home()

def a_home():
    clear_content()
    Label(content_frame, text="Admin Control Panel",
          font=FONT_H1, bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=20, pady=(20, 2))
    Label(content_frame, text=today(), font=FONT_SMALL, bg=C_BG, fg=C_MUTED).pack(anchor="w", padx=20)
    divider(content_frame)

    students = [u for u, d in users.items() if d["role"] == "student"]
    teachers = [u for u, d in users.items() if d["role"] == "teacher"]
    total_fees_due  = sum(mis["fees"].get(s, {}).get("total", 0) - mis["fees"].get(s, {}).get("paid", 0) for s in students)
    books_out       = sum(1 for b in mis["library"] if not b["available"])

    row = Frame(content_frame, bg=C_BG)
    row.pack(padx=20, pady=10)
    for lbl, val, col in [("Students",      len(students),        C_PRIMARY),
                           ("Teachers",      len(teachers),        C_SUCCESS),
                           ("Fee Balance",   f"KES {total_fees_due:,}", C_DANGER),
                           ("Books Out",     books_out,            C_WARN)]:
        c = card_frame(row)
        c.pack(side=LEFT, padx=6)
        Label(c, text=lbl, font=FONT_SMALL, bg=C_CARD, fg=C_MUTED).pack(padx=14, pady=(8, 0))
        Label(c, text=str(val), font=("Arial", 22, "bold"), bg=C_CARD, fg=col).pack(padx=14, pady=(0, 8))

    section_label(content_frame, "All Users")
    c2 = card_frame(content_frame)
    c2.pack(fill=X, padx=20, pady=6)
    cols = ("Username", "Full Name", "Role")
    tv = ttk.Treeview(c2, columns=cols, show="headings", height=min(10, len(users)))
    for col in cols:
        tv.heading(col, text=col); tv.column(col, width=160, anchor="center")
    for u, d in users.items():
        tv.insert("", END, values=(u, d.get("full_name", u), d["role"]))
    tv.pack(fill=X, padx=10, pady=10)

def a_manage_users():
    clear_content()
    section_label(content_frame, "👤 Manage Users")
    divider(content_frame)
    c = card_frame(content_frame)
    c.pack(fill=X, padx=20, pady=10)
    cols = ("Username", "Full Name", "Role", "Voice")
    tv = ttk.Treeview(c, columns=cols, show="headings", height=max(5, len(users)))
    widths = [120, 160, 80, 60, 60]
    for col, w in zip(cols, widths):
        tv.heading(col, text=col); tv.column(col, width=w, anchor="center")
    for u, d in users.items():
        has_voice = "✓" if d.get("voice") else "✗"
        tv.insert("", END, values=(u, d.get("full_name", u), d["role"], has_voice))
    tv.pack(fill=X, padx=10, pady=10)

    def delete_user():
        sel = tv.focus()
        if not sel: return
        u = tv.item(sel)["values"][0]
        if u == current_user:
            messagebox.showerror("Error", "Cannot delete yourself"); return
        if messagebox.askyesno("Confirm", f"Delete user '{u}'?"):
            del users[u]
            save_json(USER_DB, users)
            a_manage_users()

    Button(content_frame, text="🗑 Delete Selected User", command=delete_user,
           bg=C_DANGER, fg="white", **BTN_CFG).pack(anchor="w", padx=20, pady=6)

def a_fees():
    clear_content()
    section_label(content_frame, "💳 Fee Management")
    divider(content_frame)
    students = [u for u, d in users.items() if d["role"] == "student"]
    c = card_frame(content_frame)
    c.pack(fill=X, padx=20, pady=10)
    cols = ("Student", "Total (KES)", "Paid (KES)", "Balance (KES)", "Status")
    tv = ttk.Treeview(c, columns=cols, show="headings", height=max(5, len(students)))
    for col in cols:
        tv.heading(col, text=col); tv.column(col, width=130, anchor="center")
    for s in students:
        fee = mis["fees"].get(s, {"paid": 0, "total": 0})
        bal = fee["total"] - fee["paid"]
        status = "Cleared" if bal == 0 else "Pending"
        tv.insert("", END, values=(s, f"{fee['total']:,}", f"{fee['paid']:,}", f"{bal:,}", status),
                  tags=("clear" if bal == 0 else "pend",))
    tv.tag_configure("clear", foreground=C_SUCCESS)
    tv.tag_configure("pend",  foreground=C_DANGER)
    tv.pack(fill=X, padx=10, pady=10)

    # Record payment
    section_label(content_frame, "Record Payment")
    row = Frame(content_frame, bg=C_BG)
    row.pack(padx=20, pady=6, anchor="w")
    Label(row, text="Student:", font=FONT_BODY, bg=C_BG).pack(side=LEFT)
    stu_v = StringVar(value=students[0] if students else "")
    OptionMenu(row, stu_v, *students).pack(side=LEFT, padx=6)
    Label(row, text="Amount (KES):", font=FONT_BODY, bg=C_BG).pack(side=LEFT, padx=(12, 0))
    amt_e = Entry(row, font=FONT_BODY, width=10)
    amt_e.pack(side=LEFT, padx=6)

    def record_payment():
        try:
            amt = int(amt_e.get())
            assert amt > 0
        except:
            messagebox.showerror("Error", "Enter a valid amount"); return
        s = stu_v.get()
        mis["fees"].setdefault(s, {"paid": 0, "total": 60000, "history": []})
        mis["fees"][s]["paid"] += amt
        ref = f"KES-{random.randint(100,999)}"
        mis["fees"][s]["history"].append({"date": today(), "amount": amt, "ref": ref})
        save_all()
        messagebox.showinfo("Recorded", f"Payment of KES {amt:,} recorded for {s}  (Ref: {ref})")
        a_fees()

    Button(row, text="💾 Record", command=record_payment,
           bg=C_SUCCESS, fg="white", **BTN_CFG).pack(side=LEFT, padx=6)

def a_library():
    clear_content()
    section_label(content_frame, "📚 Library Admin")
    divider(content_frame)
    s_library()   # reuse student library view

    # Add new book
    section_label(content_frame, "Add New Book")
    rf = Frame(content_frame, bg=C_BG)
    rf.pack(padx=20, pady=6, anchor="w")
    for lbl in ["Title:", "Author:"]:
        Label(rf, text=lbl, font=FONT_BODY, bg=C_BG).pack(side=LEFT)
        Entry(rf, font=FONT_BODY, width=16).pack(side=LEFT, padx=4)

    def add_book():
        widgets = [w for w in rf.winfo_children() if isinstance(w, Entry)]
        title  = widgets[0].get().strip()
        author = widgets[1].get().strip()
        if not title:
            messagebox.showerror("Error", "Title required"); return
        mis["library"].append({"title": title, "author": author, "available": True, "borrower": None})
        save_all()
        messagebox.showinfo("Added", f"Book '{title}' added.")
        a_library()

    Button(rf, text="➕ Add Book", command=add_book,
           bg=C_PRIMARY, fg="white", **BTN_CFG).pack(side=LEFT, padx=8)

def a_reports():
    clear_content()
    section_label(content_frame, "📊 School Reports")
    divider(content_frame)
    students = [u for u, d in users.items() if d["role"] == "student"]
    c = card_frame(content_frame)
    c.pack(fill=X, padx=20, pady=10)
    cols = ("Student", "Avg Grade", "Attendance %", "Fee Balance", "Books Borrowed")
    tv = ttk.Treeview(c, columns=cols, show="headings", height=max(5, len(students)))
    for col in cols:
        tv.heading(col, text=col); tv.column(col, width=130, anchor="center")
    for s in students:
        grades = mis["grades"].get(s, {})
        avg    = round(sum(grades.values()) / len(grades)) if grades else 0
        att    = mis["attendance"].get(s, {})
        pct    = round(sum(1 for v in att.values() if v=="Present") / len(att)*100) if att else 0
        fee    = mis["fees"].get(s, {"paid": 0, "total": 0})
        bal    = fee["total"] - fee["paid"]
        books  = sum(1 for b in mis["library"] if b["borrower"] == s)
        tv.insert("", END, values=(s, f"{avg}%", f"{pct}%", f"KES {bal:,}", books))
    tv.pack(fill=X, padx=10, pady=10)

# ===========================================================
# MAIN LOGIN SCREEN  (original design preserved)
# ===========================================================
def main_screen():
    global entry_user, entry_pass, role_var
    clear_window()
    root.configure(bg=C_BG)
    root.geometry("480x720")

    Label(root, text="🎓 EduMIS", font=("Arial", 28, "bold"), fg=C_PRIMARY, bg=C_BG).pack(pady=(30, 2))
    Label(root, text="Multimodal Biometric Student System", font=FONT_SMALL, fg=C_MUTED, bg=C_BG).pack()
    Frame(root, bg=C_PRIMARY, height=2).pack(fill=X, padx=40, pady=14)

    entry_user = Entry(root, font=("Arial", 14), width=28)
    entry_user.pack(pady=6)
    entry_user.insert(0, "Username")

    entry_pass = Entry(root, show="*", font=("Arial", 14), width=28)
    entry_pass.pack(pady=6)
    entry_pass.insert(0, "Password")

    role_var = StringVar(value="student")
    OptionMenu(root, role_var, "student", "teacher", "admin").pack(pady=6)

    btn_row = Frame(root, bg=C_BG)
    btn_row.pack(pady=6)
    Button(btn_row, text="Sign Up", command=signup,
           bg=C_SUCCESS, fg="white", font=("Arial", 13), width=12, pady=6, cursor="hand2").pack(side=LEFT, padx=8)
    Button(btn_row, text="Log In", command=login,
           bg=C_PRIMARY, fg="white", font=("Arial", 13), width=12, pady=6, cursor="hand2").pack(side=LEFT, padx=8)

    Frame(root, bg="#BBDEFB", height=1).pack(fill=X, padx=40, pady=14)
    Label(root, text="— Biometric Authentication —", font=FONT_SMALL, fg=C_MUTED, bg=C_BG).pack()

    bio_frame = Frame(root, bg=C_BG)
    bio_frame.pack(pady=8)
    bio_buttons = [
        ("🎙  Voice Login",       voice_login,  "#7B1FA2"),
        ("🔒  Fingerprint Login", fingerprint_login, "#1565C0"),
        ("🔑 Register Fingerprint", lambda: register_fingerprint(entry_user.get()), "#00897B"),
        ("🎤  Record Voice",      lambda: record_voice(entry_user.get()), "#00695C"),
    ]
    for label, cmd, color in bio_buttons:
        Button(bio_frame, text=label, command=cmd,
               bg=color, fg="white", font=("Arial", 12),
               width=26, pady=5, cursor="hand2", relief=FLAT).pack(pady=3)

    Label(root, text="Demo: alice/pass123 (student) • mr_john/teach123 (teacher) • admin/admin123",
          font=("Arial", 9), fg=C_MUTED, bg=C_BG, wraplength=420).pack(pady=(10, 0))

# ===========================================================
# RUN
# ===========================================================
root = Tk()
root.title("EduMIS – Biometric Student Information System")
root.geometry("480x720")
root.configure(bg=C_BG)

main_screen()
root.mainloop()