# MiniFlow – Text Workflow Automation Tool

## About the Project

MiniFlow is a small Python project I built to understand how automation works in real life.

The idea is simple: instead of manually cleaning text and checking its details, MiniFlow does these tasks for me. I created a simple web dashboard where I can enter text, run the workflow, and view the results.

While building this project, I also got to practise Python, file handling, regular expressions, and connecting a web interface with a Python backend.

## What Can MiniFlow Do?

- **Clean Text:** Removes extra spaces and unnecessary blank lines.
- **Analyze Text:** Counts words, characters, and lines.
- **Generate Reports:** Creates a report with the analysis results.
- **Save Input:** Stores the original text in a separate file.
- **Track History:** Saves successful workflow runs so I can check them later.
- **Web Dashboard:** Provides a simple interface to run workflows and view reports.

## Example

Suppose I enter this text:

```text
Hello     World!


I am learning Python.
```

MiniFlow cleans it into:

```text
Hello World!

I am learning Python.
```

It then analyzes the cleaned text and generates a report containing details such as the word count, character count, and number of lines.

## Technologies Used

- Python
- HTML
- CSS
- JavaScript
- Regular Expressions (`re`)
- JSON and text files
- Python's built-in HTTP server

## How to Run the Project

**1. Clone the repository**

```bash
git clone YOUR_REPOSITORY_URL
```

Replace `YOUR_REPOSITORY_URL` with your GitHub repository URL.

**2. Open the project folder**

```bash
cd MiniFlow
```

**3. Run the Python file**

```bash
python mini_flow.py
```

**4. Open the dashboard**

Open your browser and visit:

```text
http://127.0.0.1:8001
```

You can now enter text and try the workflow.

## Files Generated

When you run the workflow, MiniFlow creates or updates these files:

- `input.txt` – stores the original input text.
- `report.txt` – contains the analysis report.
- `execution_history.json` – stores the history of successful runs.

These files help me understand how Python can save data and manage workflow results.

## What I Learned

Building MiniFlow helped me practise:

- Writing and connecting Python functions.
- Reading, cleaning, and writing text files.
- Using regular expressions to process text.
- Working with JSON data.
- Connecting a browser dashboard to Python using HTTP requests.
- Organizing multiple steps into one automated workflow.

I also learned that even a small project involves several parts working together, and understanding how they connect is just as important as writing the code.

## Future Improvements

I would like to improve MiniFlow by adding more text-processing options, better error handling, and more ways to view workflow results.

---

**MiniFlow is a learning project built to practise Python and understand the basics of workflow automation.**
