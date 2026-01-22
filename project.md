# Building a CLI Local Search Engine with Python

This guide details every step required to build a local file search engine. It uses **Python** for logic, **Rich** for the visual display, and **Inquirer** for interactive user input.

## 1. Project Overview

**What we are building:** A script that scans a specific folder on your computer, creates an "index" of words found in text files, and allows you to search and preview those files via a terminal interface.

**The Tech Stack:**
* **Python (3.8+):** The programming language.
* **Rich:** For beautiful tables, colors, and syntax highlighting.
* **Inquirer:** For interactive menus (arrow key selection).

---

## 2. Prerequisites & Installation

Before writing code, ensure your environment is ready.

### A. Environment Setup
It is best practice to create a virtual environment so these libraries don't mess with your system Python.

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
