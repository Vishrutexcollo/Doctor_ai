# Utility functions here
def generate_previsit_summary(questions: list[dict]) -> str:
    return " ".join([f"{q['question']} - {q['answer']}." for q in questions])
