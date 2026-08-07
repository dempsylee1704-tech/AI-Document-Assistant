import { afterEach, describe, expect, it, vi } from "vitest";
import { askQuestion, fetchDocuments } from "@/lib/api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("API client", () => {
  it("normalizes document responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        documents: ["legacy.pdf", { doc_id: "123", filename: "report.pdf" }],
      }),
    }));

    await expect(fetchDocuments()).resolves.toEqual([
      { doc_id: "legacy.pdf", label: "legacy.pdf" },
      { doc_id: "123", label: "report.pdf" },
    ]);
  });

  it("sends the question and selected document", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ answer: "Answer", sources: [] }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await askQuestion("What is this document?", "document-1");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/ask"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ query: "What is this document?", doc_id: "document-1" }),
      }),
    );
  });
});
