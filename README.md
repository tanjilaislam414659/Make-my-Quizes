# AI Quiz Generator from Study Material

This project is a small prototype that **generates quiz questions from study material** (e.g. lecture notes in PDF or text form) using an **open-source language model**.

It automatically:
- Reads a PDF / text file containing course content
- Extracts and cleans the text
- Splits the content into smaller segments
- Uses a local LLM to generate quiz questions from each segment
- Saves all generated questions into a single Markdown file (`generated_quiz.md`)

The goal is to explore how AI tools can **support teaching and learning** by helping to create practice questions from existing materials.

---

## Features

- 📄 **PDF/Text input**: place a `.pdf` or `.txt` file in the `data/` folder
- 🔧 **Automatic text extraction** using `pdfplumber` (for PDFs)
- ✂️ **Chunking**: long text is split into segments so the model can handle it
- 🤖 **Question generation** using an open-source LLM  
  (e.g. `TinyLlama/TinyLlama-1.1B-Chat-v1.0` via Hugging Face `transformers`)
- 📝 **Markdown output**: all questions are saved to `generated_quiz.md` for easy viewing/editing

> ⚠️ Note: The quality of the generated questions depends on the open-source model.
> This project is intended as a **prototype** and not a production system.

---

## Project Structure

```text
Quiz-Generator/
├── Data/
│   └── lecture_notes.pdf       # or any other PDF/TXT file
├── quiz_generator.py           # main script
├── requirements.txt            # Python dependencies
└── README.md                   # project documentation
