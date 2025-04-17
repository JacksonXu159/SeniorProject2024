# 🧠 Thinking Beyond Rich User Interfaces – Senior Project 2024–2025

## 💡 Overview

This project replaces traditional financial platforms with a **Google-like conversational AI** interface. Instead of navigating complex dashboards, users can simply ask questions and receive intelligent, contextual answers.

The system provides:
- Natural-language Q&A over **FAQs**, **account navigation**, and **personal financial data**
- A user-friendly interface designed to **reduce dependency on live support**

---

## ✨ Features

- **Conversational Interface**  
  Ask questions in plain English and get answers instantly.

- **Personalized Insights**  
  Responses are tailored to user data.

- **Efficiency**  
  Skip menus—get straight to the information you need.

---

## 🧠 AI Agents

| Agent              | Role                                                                 |
|-------------------|----------------------------------------------------------------------|
| `FAQ and Navigation` | Answers questions about services or platform navigation             |
| `User Retrieval`     | Provides financial data (e.g., marital status, portfolio numbers)   |
| `Services`           | Answers queries related to what services a user has or can access   |

---

## 🐳 How to Run the App with Docker

This project uses **Docker Compose** to run the backend (FastAPI) and frontend (Vite + React).

### 🧱 Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

### ▶️ Start the App

From the root directory (where `docker-compose.yml` is located), run:
```bash
docker-compose up --build
```

### ⏸️ Stop the App

```bash
docker-compose down
```

### 🌐 Access the App

- Frontend:	http://localhost
- Backend:	http://localhost:8000/docs

### Make sure to change the URL in frontend/src/config.js for local development

