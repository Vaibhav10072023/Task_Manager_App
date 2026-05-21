# Team Task Manager App

A premium, full-stack collaborative project and task management application. Built with a sleek Glassmorphism design system in **React (Vite)** on the frontend and a robust **FastAPI (Python)** REST API backed by **SQLAlchemy** and **TiDB Cloud MySQL** on the backend.

The system features robust role-based authentication (Admin vs. Team Member), isolated collaborative spaces, strict security scoping, and interactive task lifecycle management.

---

## 🚀 Key Features

* **Sleek Glassmorphism UI:** Modern, immersive dashboard designed with a cohesive HSL-based CSS color system, responsive grid layouts, and active feedback loops.
* **Role-Based Access Control (RBAC):**
  * **Administrators:** Can create new projects, assign team members to projects, create and delete tasks, and assign tasks to members.
  * **Team Members:** Can view projects they are added to, view tasks assigned to them, and update their task completion status.
* **Data Isolation & Scoping:** Users can only view projects and tasks they are owners or added members of. Complete confidentiality across different team settings.
* **Interactive Task Tracking:** Real-time state transitions (To Do $\rightarrow$ In Progress $\rightarrow$ Done) with automated overdue alerts based on due dates.
* **Secure Authentication:** JSON Web Token (JWT) based stateless authentication with automatic logout cleanup.

---

## 🛠️ Tech Stack

### Frontend
* **Core:** React 18, Vite (Fast HMR build tool)
* **Icons:** Lucide React
* **Styling:** Custom premium HSL CSS (No bloat, native variables)
* **HTTP Client:** Axios (With custom interceptors to auto-attach JWT auth tokens)

### Backend
* **Core:** FastAPI (High performance Python framework)
* **ORM:** SQLAlchemy (Object Relational Mapping)
* **Database Driver:** PyMySQL (SSL-supported for cloud database connections)
* **Security:** Jose (JWT token encoding/decoding) & Passlib (Bcrypt password hashing)

### Database
* **Production Database:** TiDB Cloud (Serverless MySQL)

---

## 📂 Project Structure

```text
Task-App/
├── backend/                  # FastAPI Application
│   ├── routers/              # API Route Handlers (users, projects, tasks)
│   ├── auth.py               # JWT & Password Encryption Logic
│   ├── database.py           # Database connection & Engine management
│   ├── main.py               # FastAPI Entrypoint & CORS setup
│   ├── models.py             # SQLAlchemy Database Schema Models
│   ├── schemas.py            # Pydantic Request/Response Validation Schemas
│   ├── clean_database.py     # Database reset & initialization utility
│   ├── .env.example          # Safe template for Backend secrets
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # React SPA Application
│   ├── src/
│   │   ├── api/              # Axios configuration
│   │   ├── components/       # Reusable UI Elements (Navbar)
│   │   ├── pages/            # View Pages (Login, Register, Dashboard, ProjectDetails)
│   │   ├── App.jsx           # App Routing and Private Route Scoping
│   │   └── index.css         # Custom HSL design tokens & css system
│   ├── .env.example          # Safe template for Frontend API configuration
│   └── package.json          # Node dependencies
│
├── setup_database.sql        # Database initialization SQL schemas
└── .gitignore                # Root gitignore (protects secrets from GitHub)
```

---

## ⚙️ Local Setup Instructions

Follow these steps to set up and run the project locally.

### Prerequisites
* Python 3.10+ installed
* Node.js (v18+) & npm installed

---

### Step 1: Backend Setup

1. **Navigate to the backend folder:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   * **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   * Copy the template file:
     ```bash
     copy .env.example .env
     ```
   * Open the newly created `.env` file and replace the placeholders with your actual **TiDB Cloud MySQL connection URL** and set a secure `SECRET_KEY`.

5. **Start the FastAPI Backend:**
   ```bash
   python -m uvicorn main:app --reload
   ```
   The backend API documentation will be available at: `http://localhost:8000/docs`

---

### Step 2: Frontend Setup

1. **Open a new terminal and navigate to the frontend folder:**
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies:**
   ```bash
   npm install
   ```

3. **Configure Environment Variables:**
   * Copy the template file:
     ```bash
     copy .env.example .env
     ```
   * The file should contain `VITE_API_URL=http://localhost:8000/api`.

4. **Start the React Frontend:**
   ```bash
   npm run dev
   ```
   Open your browser and navigate to: `http://localhost:5173`

---

## 📋 Database Schema Design

The SQL schema consists of four relational tables:

1. **`users`:** Tracks user accounts, roles (`admin` or `member`), and credentials.
2. **`projects`:** Collaborative spaces managed by an administrator (owner).
3. **`project_members`:** A many-to-many relationship mapping team members to project scopes.
4. **`tasks`:** Individual task action items tied to a specific project and assigned to a specific team member.

---

## 🛡️ Security & Environment Best Practices
To maintain clean security hygiene:
* **Secrets Protection:** The active `.env` files are ignored globally by Git. Only the empty `.env.example` templates are pushed to public/private repositories.
* **Stateless Auth:** User authorization is kept inside local secure state and automatically garbage collected from `localStorage` upon logging out.
