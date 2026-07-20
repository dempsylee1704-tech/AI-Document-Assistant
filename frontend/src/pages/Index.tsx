import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { fetchDocuments, askQuestion, type AskResponse, type DocumentItem } from "@/lib/api";
import { useQueryClient } from "@tanstack/react-query";
import { SourceCard } from "@/components/SourceCard";
import { FileUpload } from "@/components/FileUpload";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Loader2,
  Sparkles,
  FileText,
  AlertCircle,
  BrainCircuit,
  MessageSquare,
  Send,
  Zap,
  ShieldCheck,
  Activity,
  Database,
  CheckCircle2,
} from "lucide-react";
import { useEffect } from "react";

export default function Index() {
  const [selectedDoc, setSelectedDoc] = useState<string>("all");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<{ count: number; newDocs: string[] } | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const queryClient = useQueryClient();
  const docs = useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments,
    // Poll every 3s while any uploaded file is still being indexed.
    refetchInterval: isProcessing ? 3000 : false,
  });

  // Auto-dismiss success banner
  useEffect(() => {
    if (!uploadSuccess) return;
    const t = setTimeout(() => setUploadSuccess(null), 5000);
    return () => clearTimeout(t);
  }, [uploadSuccess]);

  const handleUploadComplete = async (uploaded: { name: string }[]) => {
    const previous = docs.data ?? [];
    const previousIds = new Set(previous.map((d) => d.doc_id));
    const result = await queryClient.refetchQueries({ queryKey: ["documents"] });
    const fresh = queryClient.getQueryData<DocumentItem[]>(["documents"]) ?? [];
    const newDocs = fresh.filter((d) => !previousIds.has(d.doc_id)).map((d) => d.label);
    setUploadSuccess({ count: uploaded.length, newDocs });
    void result;
  };

  const ask = useMutation({
    mutationFn: () =>
      askQuestion(question, selectedDoc === "all" ? null : selectedDoc),
    onSuccess: setResult,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    ask.mutate();
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden noise-overlay">
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute -top-60 -right-60 h-[500px] w-[500px] rounded-full bg-primary/[0.04] blur-[100px] animate-pulse-glow" />
        <div className="absolute top-1/4 -left-60 h-[450px] w-[450px] rounded-full bg-cyan/[0.04] blur-[100px] animate-pulse-glow" style={{ animationDelay: "2s" }} />
        <div className="absolute bottom-10 right-1/3 h-[400px] w-[400px] rounded-full bg-violet/[0.03] blur-[100px] animate-pulse-glow" style={{ animationDelay: "4s" }} />
        {/* Grid pattern */}
        <div className="absolute inset-0 opacity-[0.015]" style={{
          backgroundImage: 'linear-gradient(hsl(var(--foreground)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--foreground)) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }} />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-border/30 glass-strong">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="relative group cursor-pointer">
              <div className="absolute -inset-1 rounded-2xl bg-gradient-to-br from-primary/30 via-violet/20 to-cyan/30 blur-md opacity-60 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary via-violet to-cyan shadow-xl">
                <BrainCircuit className="h-5.5 w-5.5 text-primary-foreground" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-extrabold tracking-tight gradient-text">
                AI Document Assistant
              </h1>
              <p className="text-[11px] text-muted-foreground font-medium tracking-wide">Intelligent analysis engine</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-4 mr-2">
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
                <span>Encrypted</span>
              </div>
              <div className="h-3 w-px bg-border/60" />
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Activity className="h-3.5 w-3.5 text-primary" />
                <span>v2.4</span>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded-full glass px-3.5 py-1.5">
              <div className="relative h-2 w-2">
                <div className="absolute inset-0 rounded-full bg-emerald-500 animate-ping opacity-40" />
                <div className="relative h-2 w-2 rounded-full bg-emerald-500" />
              </div>
              <span className="text-xs font-semibold text-foreground">Online</span>
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-7xl px-6 lg:px-8 py-8">
        {/* Stats bar */}
        <div className="grid grid-cols-3 gap-3 mb-8 animate-slide-up">
          {[
            { icon: Database, label: "Documents", value: docs.data?.length ?? "—", color: "text-primary" },
            { icon: MessageSquare, label: "Queries", value: result ? "1" : "0", color: "text-violet" },
            { icon: FileText, label: "Sources", value: result?.sources.length ?? "—", color: "text-cyan" },
          ].map((stat) => (
            <div key={stat.label} className="glass rounded-xl px-4 py-3 flex items-center gap-3 transition-all duration-300 hover:glass-elevated hover:scale-[1.02] cursor-default">
              <div className={`flex h-8 w-8 items-center justify-center rounded-lg bg-secondary/80 ${stat.color}`}>
                <stat.icon className="h-4 w-4" />
              </div>
              <div>
                <p className="text-lg font-extrabold text-foreground tabular-nums leading-none">{stat.value}</p>
                <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider mt-0.5">{stat.label}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-8 lg:grid-cols-[1fr_1.4fr]">
          {/* Left column */}
          <div className="space-y-6">
            {/* Upload */}
            <section className="animate-slide-up rounded-2xl glass-elevated p-6 gradient-border" style={{ animationDelay: "80ms" }}>
              <div className="flex items-center gap-2.5 mb-5">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-accent text-primary">
                  <FileText className="h-4.5 w-4.5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-foreground">Upload Documents</h2>
                  <p className="text-[10px] text-muted-foreground">Add files for AI analysis</p>
                </div>
              </div>
              <FileUpload
                onUploadComplete={handleUploadComplete}
                documents={docs.data}
                onProcessingChange={setIsProcessing}
              />
              {uploadSuccess && (
                <div className="mt-4 flex items-start gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/[0.06] backdrop-blur-xl p-3.5 animate-fade-in">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-500">
                    <CheckCircle2 className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-bold text-foreground">
                      {uploadSuccess.count === 1 ? "File uploaded" : `${uploadSuccess.count} files uploaded`}
                    </p>
                    <p className="text-[11px] text-muted-foreground mt-0.5 truncate">
                      {uploadSuccess.newDocs.length > 0
                        ? `Added: ${uploadSuccess.newDocs.join(", ")}`
                        : "Document library refreshed"}
                    </p>
                  </div>
                </div>
              )}
            </section>

            {/* Query */}
            <section className="animate-slide-up rounded-2xl glass-elevated p-6 gradient-border" style={{ animationDelay: "160ms" }}>
              <div className="flex items-center gap-2.5 mb-5">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-violet/10 to-accent text-violet">
                  <MessageSquare className="h-4.5 w-4.5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-foreground">Ask a Question</h2>
                  <p className="text-[10px] text-muted-foreground">Query your document library</p>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="mb-2 block text-[11px] font-semibold text-muted-foreground uppercase tracking-widest">
                    Document scope
                  </label>
                  <Select value={selectedDoc} onValueChange={setSelectedDoc} disabled={docs.isLoading}>
                    <SelectTrigger className="w-full rounded-xl border-border/40 bg-secondary/40 backdrop-blur-sm transition-all duration-300 hover:border-primary/30 hover:bg-secondary/60 focus:ring-2 focus:ring-primary/20 focus:border-primary/40 h-11">
                      <SelectValue placeholder={docs.isLoading ? "Loading documents…" : "Select a document"} />
                    </SelectTrigger>
                    <SelectContent className="rounded-xl glass-strong border-border/40">
                      <SelectItem value="all">All documents</SelectItem>
                      {(docs.data ?? [])
                        .filter((d) => d && typeof d.doc_id === "string" && d.doc_id.length > 0)
                        .map((d) => (
                          <SelectItem key={d.doc_id} value={d.doc_id}>
                            {d.label || d.doc_id}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                  {docs.isError && !docs.isSuccess && !docs.isFetching && (
                    <p className="mt-2 text-xs text-destructive flex items-center gap-1.5 animate-fade-in">
                      <AlertCircle className="h-3 w-3" /> Failed to load documents
                    </p>
                  )}
                </div>

                <div>
                  <label className="mb-2 block text-[11px] font-semibold text-muted-foreground uppercase tracking-widest">
                    Your question
                  </label>
                  <div className="flex gap-2.5">
                    <Input
                      placeholder="Ask anything about your documents…"
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      className="flex-1 rounded-xl border-border/40 bg-secondary/40 backdrop-blur-sm transition-all duration-300 hover:border-primary/30 hover:bg-secondary/60 focus:ring-2 focus:ring-primary/20 focus:border-primary/40 h-11"
                    />
                    <Button
                      type="submit"
                      disabled={ask.isPending || !question.trim() || isProcessing}
                      title={isProcessing ? "Waiting for document to finish processing…" : undefined}
                      className="relative rounded-xl h-11 px-6 overflow-hidden bg-gradient-to-r from-primary via-primary to-violet shadow-lg shadow-primary/25 transition-all duration-500 hover:shadow-xl hover:shadow-primary/35 hover:scale-[1.03] active:scale-[0.97] disabled:opacity-40 disabled:shadow-none disabled:scale-100 group animate-gradient-shift"
                    >
                      <span className="absolute inset-0 bg-gradient-to-r from-transparent via-primary-foreground/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                      {ask.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin relative z-10" />
                      ) : (
                        <Send className="h-4 w-4 relative z-10 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                      )}
                      <span className="ml-2 font-bold relative z-10">Ask</span>
                    </Button>
                  </div>
                </div>
              </form>
            </section>
          </div>

          {/* Right column */}
          <div className="space-y-6">
            {/* Error */}
            {ask.isError && (
              <div className="flex items-center gap-3 rounded-2xl border border-destructive/20 bg-destructive/5 backdrop-blur-xl p-5 text-sm text-destructive animate-fade-in">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-destructive/10">
                  <AlertCircle className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-bold">Analysis failed</p>
                  <p className="text-xs opacity-70 mt-0.5">Please try again or check your connection.</p>
                </div>
              </div>
            )}

            {/* Loading */}
            {ask.isPending && (
              <div className="animate-fade-in rounded-2xl glass-elevated p-10 text-center glow-lg gradient-border">
                <div className="relative mx-auto mb-5 flex h-16 w-16 items-center justify-center">
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/15 to-violet/10 animate-pulse" />
                  <div className="absolute inset-[-4px] rounded-2xl border-2 border-primary/20 animate-border-glow" />
                  <Sparkles className="h-8 w-8 text-primary relative z-10" />
                  <div className="absolute h-2 w-2 rounded-full bg-cyan animate-orbit" style={{ animationDuration: "3s" }} />
                </div>
                <p className="text-base font-bold text-foreground">Analyzing documents…</p>
                <p className="mt-1.5 text-sm text-muted-foreground">AI is processing your query</p>
                <div className="mt-5 mx-auto h-1.5 w-56 rounded-full overflow-hidden bg-secondary/80">
                  <div className="h-full rounded-full animate-shimmer" />
                </div>
                <div className="flex justify-center gap-1.5 mt-4">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="h-1.5 w-1.5 rounded-full bg-primary"
                      style={{ animation: `typing-dot 1.4s ease-in-out ${i * 0.2}s infinite` }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty state */}
            {!result && !ask.isPending && !ask.isError && (
              <div className="animate-slide-up rounded-2xl glass-elevated p-14 text-center gradient-border" style={{ animationDelay: "240ms" }}>
                <div className="relative mx-auto mb-5 flex h-20 w-20 items-center justify-center">
                  <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-primary/8 via-violet/5 to-cyan/8 animate-float" />
                  <div className="absolute inset-2 rounded-2xl glass" />
                  <Zap className="h-9 w-9 text-primary/50 relative z-10" />
                </div>
                <h3 className="text-lg font-extrabold text-foreground">Ready to analyze</h3>
                <p className="mt-2 text-sm text-muted-foreground max-w-sm mx-auto leading-relaxed">
                  Upload documents and ask questions to get AI-powered insights with source attribution.
                </p>
                <div className="mt-6 flex justify-center gap-2">
                  {["Upload", "Ask", "Analyze"].map((step, i) => (
                    <div key={step} className="flex items-center gap-2">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">{i + 1}</span>
                      <span className="text-xs font-semibold text-muted-foreground">{step}</span>
                      {i < 2 && <div className="w-6 h-px bg-border" />}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Answer */}
            {result && !ask.isPending && (
              <section className="animate-fade-in space-y-3">
                <h2 className="flex items-center gap-2 text-[11px] font-extrabold uppercase tracking-[0.15em] text-muted-foreground">
                  <Sparkles className="h-3.5 w-3.5 text-primary" /> AI Answer
                </h2>
                <div className="relative rounded-2xl glass-elevated p-7 glow-lg gradient-border overflow-hidden">
                  {/* Scan line effect */}
                  <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute inset-x-0 h-8 bg-gradient-to-b from-primary/[0.03] to-transparent" style={{ animation: "scan-line 4s linear infinite" }} />
                  </div>
                  <div className="absolute top-4 right-4 flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-violet/10">
                    <BrainCircuit className="h-4 w-4 text-primary" />
                  </div>
                  <p className="relative text-foreground leading-[1.8] pr-10 text-[15px]">{result.answer}</p>
                </div>
              </section>
            )}

            {/* Sources */}
            {result && !ask.isPending && (
              <section className="space-y-3 animate-fade-in" style={{ animationDelay: "200ms" }}>
                <h2 className="flex items-center gap-2 text-[11px] font-extrabold uppercase tracking-[0.15em] text-muted-foreground">
                  <FileText className="h-3.5 w-3.5 text-primary" /> Sources
                  {result.sources.length > 0 && (
                    <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-extrabold text-primary ring-1 ring-primary/15">
                      {result.sources.length}
                    </span>
                  )}
                </h2>
                {result.sources.length === 0 ? (
                  <div className="rounded-2xl glass p-8 text-center">
                    <p className="text-sm text-muted-foreground">No sources matched this query</p>
                  </div>
                ) : (
                  <div className="grid gap-3">
                    {result.sources.map((s, i) => (
                      <SourceCard key={i} source={s} index={i} />
                    ))}
                  </div>
                )}
              </section>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
