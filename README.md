# AI-Driven Code Reviewer 

## 📌 Project Overview

This project focuses on building the Code Parsing & Preprocessing module using Python’s Abstract Syntax Tree (AST).
It takes Python code as input, analyzes its structure, and prepares it for AI-based feedback.

---

## ⚙️ Features Implemented

✔ Accepts Python code as input
✔ Parses code using AST (`ast.parse`)
✔ Displays AST structure (`ast.dump`)
✔ Performs structural analysis using NodeVisitor
✔ Reformats code using `ast.unparse`
✔ Detects syntax errors
✔ Secure API key handling using `.env`

---

## 🧠 Technologies Used

* Python 3
* AST (Abstract Syntax Tree)
* LangChain (for future use)
* Groq API (for AI suggestions)
* python-dotenv

---

## 🚀 How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python code_parser.py
```

---

## 🔜 Future Scope

* AI-based code suggestions
* Real-time web interface
* Multi-language support

---

## 📁 Project Structure

AI_CODE_REVIEWER/
│
├── ai_code_reviewer/
├── app.py
├── README.md
├── requirements.txt
├── rxconfig.py
