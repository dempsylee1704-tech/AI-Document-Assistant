const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

// Common headers for all backend requests.
// `ngrok-skip-browser-warning` is required when the backend is hosted behind
// a free ngrok tunnel — without it, ngrok intercepts the request and returns
// an HTML warning page instead of forwarding to FastAPI, which causes
// "Failed to fetch" / CORS errors in the browser.
const COMMON_HEADERS: Record<string, string> = {
  "ngrok-skip-browser-warning": "true",
};

export interface Source {
  source_filename: string;
  doc_id: string;
  page_start: number;
  page_end: number;
  page?: number;
  category: string;
  score: number;
  pdf_url?: string;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface DocumentItem {
  doc_id: string;
  label: string;
}

export async function fetchDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${BASE_URL}/documents`, {
    headers: { ...COMMON_HEADERS },
  });
  if (!res.ok) throw new Error("Failed to load documents");
  const data = await res.json();
  // Support new ({doc_id,label}), filename ({doc_id,filename}) and legacy (string) formats
  return (data.documents ?? []).map((d: unknown) => {
    if (typeof d === "string") return { doc_id: d, label: d };
    const obj = d as { doc_id: string; label?: string; filename?: string };
    return { doc_id: obj.doc_id, label: obj.label || obj.filename || obj.doc_id };
  });
}

export async function askQuestion(query: string, doc_id: string | null): Promise<AskResponse> {
  const res = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...COMMON_HEADERS },
    body: JSON.stringify({ query, doc_id }),
  });
  if (!res.ok) throw new Error("Failed to get answer");
  return res.json();
}

export async function uploadFile(file: File): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    headers: { ...COMMON_HEADERS },
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to upload file");
}
