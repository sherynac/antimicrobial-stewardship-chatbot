
import re
def get_splitted_question(question):
    question = question.lower()
    question = re.sub(r'\s+', ' ', question)
    question = question.strip()
    words = re.findall(r'\b\w+\b', question)
    print(f"Splitted question: {words}")
    return words

