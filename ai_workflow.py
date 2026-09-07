import json
from pathlib import Path
from openai import OpenAI
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"

MODEL = "gpt-5"

def _get_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to Streamlit Secrets."
        )
    return OpenAI(api_key=api_key)

def _load_prompt(filename):
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")

def _call_ai(instructions, input_text):
    client = _get_client()
    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=input_text,
    )
    return response.output_text.strip()

def _json_from_text(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned)

def run_study_pack_workflow(profile):
    # Stage 1: Planning
    planning_prompt = _load_prompt("01_planning_prompt.txt")
    plan_text = _call_ai(
        planning_prompt,
        json.dumps(profile, ensure_ascii=False, indent=2),
    )
    plan = _json_from_text(plan_text)

    # Stage 2: Content generation
    content_prompt = _load_prompt("02_content_generation_prompt.txt")
    content_input = json.dumps(
        {"learner_profile": profile, "learning_plan": plan},
        ensure_ascii=False,
        indent=2,
    )
    content = _call_ai(content_prompt, content_input)

    # Stage 3: Quality review
    review_prompt = _load_prompt("03_review_repair_prompt.txt")
    review_input = json.dumps(
        {
            "learner_profile": profile,
            "learning_plan": plan,
            "study_pack": content,
        },
        ensure_ascii=False,
        indent=2,
    )
    review_text = _call_ai(review_prompt, review_input)
    review = _json_from_text(review_text)

    repaired = False
    final_pack = content

    # Conditional repair
    if review.get("needs_repair", False):
        repaired = True
        repair_request = json.dumps(
            {
                "learner_profile": profile,
                "learning_plan": plan,
                "study_pack": content,
                "review": review,
            },
            ensure_ascii=False,
            indent=2,
        )
        final_pack = _call_ai(
            review_prompt
            + "\n\nREPAIR MODE:\nReturn only the corrected final study pack in Markdown. "
              "Preserve good content and fix every issue identified by the reviewer.",
            repair_request,
        )

    # Deterministic final verification
    verification = verify_pack(final_pack, profile)

    return {
        "plan": plan,
        "final_pack": final_pack,
        "review": review,
        "quality_score": review.get("quality_score", 0),
        "review_status": "Passed" if not review.get("needs_repair") else "Repaired",
        "verification_status": "Passed" if verification["passed"] else "Warnings",
        "verification": verification,
        "repaired": repaired,
    }

def verify_pack(pack, profile):
    required_sections = [
        "Learning Objectives",
        "Study Plan",
        "Key Concepts",
        "Practice Questions",
        "Answer Key",
        "Quick Review",
    ]

    missing = [section for section in required_sections if section.lower() not in pack.lower()]

    expected_questions = int(profile["question_count"])
    question_lines = [
        line for line in pack.splitlines()
        if line.strip().startswith(tuple(f"{i}." for i in range(1, expected_questions + 1)))
    ]

    return {
        "passed": len(missing) == 0 and len(question_lines) >= min(expected_questions, 3),
        "missing_sections": missing,
        "question_count_check": len(question_lines),
    }
