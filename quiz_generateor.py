import os
import pdfplumber
from transformers import AutoTokenizer, AutoModelForCausalLM

# ============================
# Configuration
# ============================

DATA_FOLDER = "Data"  # Folder containing PDF files
OUTPUT_FILE = "generated_quiz.md"  # Output file name
QUESTIONS_PER_SEGMENT = 5          # Questions generated per text segment
MAX_SEGMENT_LENGTH = 1200          # Controls chunk size for LLM input


# ============================
# PDF Loading
# ============================

def load_pdf_text(pdf_path):
    """Load and extract text from a PDF file."""
    print(f"[DEBUG] Loading PDF: {pdf_path}")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        print(f"[DEBUG] PDF has {len(pdf.pages)} pages.")
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    print(f"[DEBUG] Extracted {len(text)} characters from PDF.")
    return text


# ============================
# Text Chunking
# ============================

def split_into_segments(text, max_len=MAX_SEGMENT_LENGTH):
    """Split long text into smaller segments for the LLM."""
    print("[DEBUG] Splitting text into segments...")

    words = text.split()
    segments = []
    current = []

    for word in words:
        current.append(word)
        if sum(len(w) for w in current) > max_len:
            segments.append(" ".join(current))
            current = []

    if current:
        segments.append(" ".join(current))

    print(f"[DEBUG] Created {len(segments)} segments.")
    return segments


# ============================
# Quiz Generation
# ============================

def generate_quiz_questions(llm, tokenizer, text_segment, num_questions=QUESTIONS_PER_SEGMENT):
    """Generate quiz questions from a text segment."""
    prompt = (
        f"Read the following text and generate {num_questions} quiz questions.\n"
        f"Text:\n{text_segment}\n\nQuestions:\n"
    )

    inputs = tokenizer(prompt, return_tensors="pt")
    output = llm.generate(**inputs, max_new_tokens=300)
    result = tokenizer.decode(output[0], skip_special_tokens=True)

    return result


# ============================
# Main Pipeline
# ============================

def main():
    print("\n===== QUIZ GENERATOR STARTED =====\n")

    # Pick the first PDF in /data folder
    pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("❌ No PDF files found in the 'data' folder!")
        return

    pdf_path = os.path.join(DATA_FOLDER, pdf_files[0])
    print(f"[INFO] Using PDF file: {pdf_path}")

    # Load and process PDF
    text = load_pdf_text(pdf_path)
    segments = split_into_segments(text)

    # Load LLM
    print("[INFO] Loading model (TinyLlama)...")
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Generate quiz
    quiz_output = ["# Generated Quiz\n"]

    for i, seg in enumerate(segments):
        print(f"[INFO] Generating questions for segment {i + 1}/{len(segments)}...")
        questions = generate_quiz_questions(model, tokenizer, seg)
        quiz_output.append(f"## Segment {i + 1}\n{questions}\n")

    # Save quiz file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(quiz_output))

    print(f"\n🎉 Quiz generated successfully!")
    print(f"📄 Saved as: {OUTPUT_FILE}")
    print("======================================")


# Run script
if __name__ == "__main__":
    main()