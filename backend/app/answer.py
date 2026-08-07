from openai import OpenAI

from vector_db import search_chunks
from config import API_KEY

def get_openai_client():
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=API_KEY)

def generate_answer(query, chunks):
    context = ""

    for i, chunk in enumerate(chunks, start=1):
        context += f"""
Quelle {i}
Datei: {chunk.get("source_filename", "unbekannt")}
Seite: {chunk.get("page_start", chunk.get("page", "unbekannt"))}
Kategorie: {chunk.get("category", "other")}

Text:
{chunk.get("text", "")}

---
"""

    prompt = f"""
Du bist ein präziser deutscher Dokumenten-Assistent.

Beantworte die Frage ausschließlich mit Informationen aus dem gegebenen Kontext.

Wichtige Regeln:
- Antworte auf Deutsch.
- Wenn die Frage allgemein ist, z. B. "Worum geht es?", "Was ist das für ein Dokument?" oder "Fasse das Dokument zusammen", dann gib eine kurze Zusammenfassung des Dokuments.
- Nutze auch Dateiname, Kategorie und Seiteninformationen, wenn sie helfen.
- Wenn der Kontext nur teilweise lesbar ist, formuliere vorsichtig: "Das Dokument scheint ... zu sein".
- Sage nur dann, dass du die Information nicht findest, wenn wirklich keine passenden Informationen im Kontext vorhanden sind.
- Erfinde keine Details, die nicht im Kontext stehen.

Bei Formularen:
- Erkenne, ob es sich um einen Antrag, Fragebogen, Vertrag, Kontoauszug oder ein anderes Dokument handelt.
- Beschreibe kurz den Zweck des Dokuments.
- Nenne keine sensiblen persönlichen Details ausführlich, wenn sie für die Frage nicht nötig sind.

Kontext:
{context}

Frage:
{query}

Antwort:
"""

    response = get_openai_client().responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text

def ask_documents(query, doc_id=None):
    results = search_chunks(query, doc_id=doc_id)
    answer = generate_answer(query, results)

    return {
        "answer": answer,
        "sources": results
    }
