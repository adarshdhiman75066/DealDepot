# 🏪 DealDepot 

## 📌 Project Overview
The **Store Management System** is a web-based application designed to **track employee attendance and manage sales records efficiently**. It includes a **role-based login system**, where:

- **Admins** have full control over **attendance tracking, sales management, and report generation**.
- **Employees** can only **mark attendance and process sales transactions** via a POS-like interface.

The system is built using **HTML, CSS, JavaScript, Bootstrap, FastAPI, Python, Pandas and CSV for data storage**.

---

## 🚀 Features

### 🔑 Authentication System (Admin & Employee Login)
- Secure **login system** with role-based access.
- **Admin Features**:
  - Add, edit, or remove employees.
  - View and manage attendance and sales reports.
- **Employee Features**:
  - Mark attendance (validated using JavaScript).
  - Process sales transactions.

### 🕒 Employee Attendance Management
- Employees **mark their attendance** with **JavaScript date-time validation**.
- Attendance records are stored in **`data/attendance.csv`**.
- Admin can view **attendance reports** and **download them in CSV format**.

### 💵 Sales Management (POS System)
- Employees can process **sales transactions** through a **simple POS interface**.
- Sales records are stored in **`data/sales.csv`**.

### 📊 Reports & Data Analysis
- **Employee Attendance Report**:
  - View employee-wise attendance.
  - Export as **CSV file**.
- **Sales Report**:
  - **Monthly Report** – Displays total revenue and transaction count.
  - **Per Employee Report** – Shows sales per employee.
  - Downloadable in **CSV and PDF formats**.

---

## 🛠️ Tech Stack
| Technology  | Usage |
|------------|----------|
| **HTML, CSS, Bootstrap** | Frontend UI Design |
| **JavaScript** | Attendance date-time validation, interactivity |
| **FastAPI (Python)** | Backend API for data management |
| **CSV (Comma-Separated Values)** | Data storage for attendance & sales |
| **PDF Generation (Python Library)** | Exporting reports in PDF format |

---
## 📂 Folder Structure
DealDepot - Inventory Management System/\
├── main.py\
├── data/\
│   ├── attendance.csv\
│   ├── employeedetails.csv\
│   ├── sales.csv\
│   ├── users.csv\
│   └── products.csv\
├── static/\
│   ├── bootstrap/\
│   ├── css/\
│   ├── js/\
│   └── images/\
├── templates/\
│   ├── admin.html\
│   ├── index.html\
│   ├── 404.html\
│   ├── 500.html\
│   ├── emp.html\
│   ├── pos.html\
│   └── pg.html\
└── documents/\
    ├── README.md\
    ├── Project Synposis.pdf\
    └── Project Report.pdf\




