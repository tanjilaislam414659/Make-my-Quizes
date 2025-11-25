
# 📘 AI Quiz Generator — PDF → MCQs

This project is a prototype system that automatically generates **multiple-choice questions (MCQs)** from lecture materials such as PDFs or text files. It uses a fully local, open-source Large Language Model (**Qwen2.5-3B-Instruct**) to analyze content and generate structured quiz questions.

---

## 🚀 Features

- **PDF & TXT input support** using `pdfplumber`
- **Text chunking/segmentation** for focused AI reasoning  
- **AI-generated MCQs** (A–D options with correct answer)
- **Fully local** — no API keys, no online calls
- **Markdown output** into `generated_quiz.md`

---

## 📂 Project Structure

```
AI-Quiz-Generator/
├── Data/                    # Place your PDF/TXT files here
│   └── example.pdf
├── quiz_generator.py        # Main script
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

---

## 🧠 How It Works

1. **Parse PDF/Text** → extract content  
2. **Segment text** → chunks ~900 characters  
3. **Generate MCQs** → Qwen2.5 processes each segment  
4. **Save results** → Markdown quiz output  

---

## ▶️ Setup & Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your study file
Place your `.pdf` or `.txt` into:
```
Data/
```

### 3. Run the generator
```bash
python quiz_generator.py
```

### 4. Open generated quiz
```
generated_quiz.md
```

---

## 🤖 Why Qwen2.5-3B?

| Model | Result |
|-------|--------|
| TinyLlama-1.1B | Weak / unstable MCQs |
| Phi-2 | Inconsistent formatting |
| Gemma 2B | Gated, requires login |
| **Qwen2.5-3B** | ⭐ Best offline instruction-following, stable MCQs |

---

## 🔮 Future Improvements

- LMS export formats (Moodle GIFT, ILIAS XML)
- Difficulty levels
- GUI using Streamlit
- Better distractor generation
- Self-evaluation using second model

---

## 🧑‍💻 Author

Created by **Tanjila Islam**  
A demonstration of integrating open-source AI tools into educational workflows.
