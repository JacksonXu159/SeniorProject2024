# Thinking Beyond Rich User Interfaces - Senior Project 2024

## Overview

This project focuses on replacing traditional financial platforms that have rich, detailed user interfaces with a Google-like search interface/conversational AI tool.
The goal is to allow clients to ask questions and receive answers directly from their financial data. This approach aims to improve user experience and reduce dependency on live support agents.

## Features

-   **Conversational Interface**: Clients can ask questions in natural language and receive clear, detailed answers.
-   **Personalized Insights**: Provides tailored answers based on user information.
-   **Efficiency**: Reduces time spent navigating websites by focusing on delivering answers quickly.

## Setup

1. Clone repo
2. Cd into ./backend
3. Start a python virtual env `python -m venv ./myvenv`
4. Acitvate venv `./myvenv/Scripts/activate`
    - For macOS/Linux (zsh or bash) `source myvenv/bin/activate`
    - For For Windows (Git Bash or WSL) `source myvenv/Scripts/activate`
5. Install dependencies `pip install -r requirements.txt`
6. Run `uvicorn server:app --reload` to start server
7. In a different terminal, cd into ./frontend and install dependencies `npm i `
8. Open a new terminal
9. Cd into ./frontend
10. To Test locally: Open useGenAI.js and change const url to `http://127.0.0.1:8000/message`
    - Make sure to change it back to what it was originally when you're done
11. Run `npm i`
12. Run `npm run dev`
