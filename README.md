# AI-Driven Code Reviewer – Milestone 1

## 📌 Project Overview
This project is part of the development of an AI-Driven Code Reviewer.
Milestone-1 focuses on building the Code Parsing & Preprocessing module using Python's AST (Abstract Syntax Tree).

The system reads student Python code, understands its structure,
and prepares it for AI-based feedback in later stages.

---

## ⚙️ Features Implemented

✔ Accepts Python code as input  
✔ Parses code using Python AST (ast.parse)  
✔ Displays AST structure (ast.dump)  
✔ Analyzes code using NodeVisitor  
✔ Reformats code automatically (ast.unparse)  
✔ Secure API key handling using `.env`

---

## 🧠 Technologies Used

- Python 3
- AST (Abstract Syntax Tree)
- LangChain (prepared for next milestone)
- Groq API (for future integration)
- python-dotenv

---

## 🚀 How to Run This Project

1️⃣ Create virtual environment:
python -m venv venv

2️⃣ Activate environment:
venv\Scripts\activate

3️⃣ Install dependencies:
pip install -r requirements.txt

4️⃣ Add your GROQ API key inside `.env`:
GROQ_API_KEY="your_api_key_here"

5️⃣ Run the program:
python code_parser.py

---

## 📊 What This Module Does

The program:
- Reads Python code from the user
- Converts it into AST
- Analyzes structure
- Displays formatted code

---

## 🔜 Next Step

Milestone-2 will integrate Groq AI using LangChain to provide automated feedback.
