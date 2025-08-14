import os
import re
import json
import hashlib
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from graphviz import Digraph
from dotenv import load_dotenv


load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


_model = None
def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def sanitize_filename(title: str) -> str:
    """Remove invalid filename chars and trim whitespace."""
    return re.sub(r'[^\w\-_]', '_', title.strip())

def hash_id(value: str) -> str:
    return hashlib.md5(value.encode()).hexdigest()[:8]

def add_node(dot, node_id, label, shape='box', style='rounded,filled', fillcolor='lightblue'):
    dot.node(node_id, label, shape=shape, style=style, fillcolor=fillcolor)

def build_flowchart(dot, data, parent_id=None, level=0):
    """Recursive function to build a flowchart from nested JSON."""
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'lavender',
              'peachpuff', 'mistyrose', 'honeydew', 'thistle']
    current_color = colors[level % len(colors)]

    if isinstance(data, dict):
        for key, value in data.items():
            node_label = str(key).strip()
            key_id = hash_id(f"{parent_id}_{node_label}" if parent_id else node_label)
            add_node(dot, key_id, node_label, fillcolor=current_color)
            if parent_id:
                dot.edge(parent_id, key_id)
            build_flowchart(dot, value, key_id, level + 1)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                build_flowchart(dot, item, parent_id, level + 1)
            else:
                item_label = str(item).strip()
                item_id = hash_id(f"{parent_id}_{item_label}")
                add_node(dot, item_id, f"• {item_label}", shape='box', style='filled', fillcolor='white')
                if parent_id:
                    dot.edge(parent_id, item_id)

    else:
        if parent_id and str(data).strip():
            val_label = str(data).strip()
            val_id = hash_id(f"{parent_id}_{val_label}")
            add_node(dot, val_id, val_label, shape='ellipse', fillcolor='white')
            dot.edge(parent_id, val_id)


def call_llama_api(prompt: str, model="meta-llama/llama-3.3-70b-instruct") -> str:
    """Call OpenRouter LLaMA API with a given prompt."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Career-Path-Recommender"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        res.raise_for_status()
        return res.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.Timeout:
        print("❌ LLaMA API Timeout.")
        return None
    except Exception as e:
        print(f"❌ LLaMA API Error: {e}")
        return None


def generate_recommendation_from_input(user_interest: str, user_qualification: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "final_course_data_for_bert.csv")


    df = pd.read_csv(csv_path)
    df['course_summary'] = "Course: " + df['Course'] + " | Field: " + df['Field']


    df_filtered = df[df['Minimum_Qualification'].str.lower() == user_qualification.lower()]
    if df_filtered.empty:
        raise ValueError("No courses found for your qualification.")


    model = get_model()
    course_texts = df_filtered['course_summary'].tolist()
    course_embeddings = model.encode(course_texts, show_progress_bar=False)
    user_embedding = model.encode([user_interest])
    similarities = cosine_similarity(user_embedding, course_embeddings)[0]
    best_index = similarities.argmax()
    best_row = df_filtered.iloc[best_index]
    best_course = best_row['Course']


    prompt_related = (
        f"Suggest 4 other full degree courses related to '{best_course}'. "
        "Return only a raw JSON array of course names."
    )
    related_response = call_llama_api(prompt_related)
    related_courses = []

    if related_response:
        try:
            related_courses = json.loads(related_response)
        except:
            for line in related_response.strip().split('\n'):
                match = re.match(r'^\d+\. (.+)', line.strip())
                if match:
                    related_courses.append(match.group(1).strip())


    prompt_roadmap = f"""
You are an expert mentor and a caring parent helping your child succeed in the course '{best_course}'.

Create a deeply structured, spoon-feeding style 4-year roadmap from scratch to expert level.
Organize everything in proper hierarchy as valid JSON.
Include:
1. Semester-wise academic curriculum
2. Skills to build
3. Online course recommendations
4. Learning milestones
5. Project ideas
6. Portfolio building
7. Personality development
8. Events to join
9. Internship search strategy
10. Final year placement guide

Root key: "roadmap". Output only valid JSON.
"""
    roadmap_json = call_llama_api(prompt_roadmap)
    roadmap_data = {}

    if roadmap_json:
        try:
            roadmap_data = json.loads(roadmap_json).get("roadmap", {})
        except json.JSONDecodeError:
            match = re.search(r'\{[\s\S]*\}', roadmap_json)
            if match:
                try:
                    cleaned_json = match.group(0)
                    roadmap_data = json.loads(cleaned_json).get("roadmap", {})
                except:
                    pass


    filename = sanitize_filename(best_course)


    pdf_folder = os.path.join(BASE_DIR, "roadmaps")
    os.makedirs(pdf_folder, exist_ok=True)

    dot = Digraph(comment=f"Roadmap for {best_course}", format='pdf')
    dot.attr(rankdir='TB')
    build_flowchart(dot, roadmap_data)
    output_path = os.path.join(pdf_folder, filename)
    dot.render(output_path, cleanup=True)

    return {
        "recommended_course": best_course,
        "related_courses": [best_course] + related_courses,
        "roadmap": roadmap_data,
        "pdf_path": f"roadmaps/{filename}.pdf"  
    }


if __name__ == "__main__":
    interest = input("🎤 Enter your interests: ")
    qualification = input("🎓 Enter your current qualification: ").strip().lower()
    try:
        result = generate_recommendation_from_input(interest, qualification)
        print("\n🎯 Recommended Course:", result["recommended_course"])
        print("\n📚 Related Courses:", result["related_courses"])
        print("\n📄 PDF saved at:", result["pdf_path"])
    except Exception as e:
        print("❌ Error:", e)
