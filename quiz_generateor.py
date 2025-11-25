import os
import pdfplumber
from transformers import AutoTokenizer, AutoModelForCausalLM

# ============================
# Configuration
# ============================

# Accept either "Data" or "data" as the folder name
POSSIBLE_DATA_FOLDERS = ["Data", "data"]

OUTPUT_FILE = "generated_quiz.md"

MAX_SEGMENT_LENGTH = 900      # characters per segment
MAX_SEGMENTS = 4              # only first N segments (MCQs are heavier)
QUESTIONS_PER_SEGMENT = 2     # MCQs per segment

# Qwen2.5-3B-Instruct model
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"


# ============================
# Data folder + file helpers
# ============================

def find_data_folder() -> str:
    """Find an existing data folder: 'Data' or 'data'."""
    for folder in POSSIBLE_DATA_FOLDERS:
        if os.path.isdir(folder):
            print(f"[INFO] Using data folder: {folder}")
            return folder
    raise FileNotFoundError(
        "No data folder found. Please create a folder named 'Data' or 'data' "
        "and put a PDF or TXT file inside."
    )


def pick_study_file(folder: str) -> str:
    """Pick the first PDF or TXT file from the data folder."""
    files = [f for f in os.listdir(folder)
             if f.lower().endswith(".pdf") or f.lower().endswith(".txt")]
    if not files:
        raise FileNotFoundError(
            f"No .pdf or .txt files found in '{folder}'. "
            "Please add at least one study file there."
        )
    chosen = files[0]
    print(f"[INFO] Using study file: {chosen}")
    return os.path.join(folder, chosen)


# ============================
# Loading text
# ============================

def load_text(path: str) -> str:
    """Load text from PDF or TXT."""
    if path.lower().endswith(".txt"):
        print(f"[DEBUG] Loading TXT: {path}")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"[DEBUG] Loaded {len(text)} characters from TXT.")
        return text

    elif path.lower().endswith(".pdf"):
        print(f"[DEBUG] Loading PDF: {path}")
        text = ""
        with pdfplumber.open(path) as pdf:
            print(f"[DEBUG] PDF has {len(pdf.pages)} pages.")
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        print(f"[DEBUG] Extracted {len(text)} characters from PDF.")
        return text

    else:
        raise ValueError("Unsupported file type. Use .pdf or .txt.")


# ============================
# Segmenting
# ============================

def split_into_segments(text: str, max_len: int = MAX_SEGMENT_LENGTH):
    """Split long text into smaller segments for the LLM."""
    print("[DEBUG] Splitting text into segments...")

    words = text.split()
    segments = []
    current = []
    current_len = 0

    for word in words:
        current.append(word)
        current_len += len(word) + 1
        if current_len >= max_len:
            segments.append(" ".join(current))
            current = []
            current_len = 0

    if current:
        segments.append(" ".join(current))

    print(f"[DEBUG] Created {len(segments)} segments.")
    return segments


# ============================
# MCQ Generation
# ============================

def build_mcq_prompt(text_segment: str, num_questions: int) -> str:
    """
    Ask Qwen to generate multiple-choice questions (MCQs).
    """
    prompt = f"""
You are a helpful teaching assistant.

From the following study text, create {num_questions} multiple-choice questions (MCQs)
with FOUR options each. Each question should test an important concept.

Use EXACTLY this format:

Q1: <question text>
A) <option 1>
B) <option 2>
C) <option 3>
D) <option 4>
Correct: <A/B/C/D>

Q2: <question text>
A) <option 1>
B) <option 2>
C) <option 3>
D) <option 4>
Correct: <A/B/C/D>

Rules:
- Make only {num_questions} questions.
- Options should be plausible; only ONE is clearly correct.
- Answers (A–D) must be short and clear.
- Do NOT add explanations.
- Do NOT repeat the original text.
- Do NOT output anything else.

TEXT:
\"\"\"{text_segment}\"\"\"
"""
    return prompt.strip()


def generate_mcq_for_segment(model, tokenizer, text_segment: str, num_questions: int) -> str:
    """Generate MCQs for a given segment using Qwen."""
    prompt = build_mcq_prompt(text_segment, num_questions)

    inputs = tokenizer(prompt, return_tensors="pt")
    output_ids = model.generate(
        **inputs,
        max_new_tokens=450,
        do_sample=True,
        temperature=0.5,
        top_p=0.9,
    )
    result = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # If the model echoes the prompt, cut it off
    if result.startswith(prompt):
        result = result[len(prompt):].strip()

    return result.strip()


# ============================
# Main
# ============================

def main():
    print("\n===== QUIZ GENERATOR (MCQ, Qwen2.5-3B-Instruct) =====\n")

    # 1. Find data folder and study file
    data_folder = find_data_folder()
    study_path = pick_study_file(data_folder)

    # 2. Load text and split into segments
    text = load_text(study_path)
    segments = split_into_segments(text)

    if not segments:
        print("❌ No text segments were created from the study file.")
        return

    segments = segments[:MAX_SEGMENTS]
    print(f"[INFO] Using {len(segments)} segment(s) for MCQ generation.")

    # 3. Load Qwen model
    print("[INFO] Loading Qwen2.5-3B-Instruct model (first run may take time)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model.eval()
    print("[DEBUG] Model loaded.")

    # 4. Generate MCQs per segment
    blocks = ["# Generated Quiz (MCQ, Qwen2.5-3B)\n"]

    for i, seg in enumerate(segments, start=1):
        print(f"[INFO] Generating MCQs for segment {i}/{len(segments)}...")
        mcq_text = generate_mcq_for_segment(model, tokenizer, seg, QUESTIONS_PER_SEGMENT)
        blocks.append(f"## Segment {i}\n\n{mcq_text}\n")

    # 5. Save to Markdown
    final_md = "\n\n---\n\n".join(blocks)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_md)

    print(f"\n🎉 MCQ quiz generated successfully!")
    print(f"📄 Saved as: {OUTPUT_FILE}")
    print("==========================================")


if __name__ == "__main__":
    main()
