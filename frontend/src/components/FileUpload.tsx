import { useCallback, useRef, useState } from "react";
import { Upload, X, File, CheckCircle2, CloudUpload, Loader2, AlertCircle } from "lucide-react";
import { uploadFile } from "@/lib/api";

interface UploadedFile {
  file: File;
  id: string;
  status: "pending" | "uploading" | "done" | "error";
}

interface FileUploadProps {
  onUploadComplete?: (uploaded: { name: string }[]) => void;
}

export function FileUpload({ onUploadComplete }: FileUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleUpload = useCallback(async (newFiles: FileList | File[]) => {
    const arr = Array.from(newFiles).map((file) => ({
      file,
      id: crypto.randomUUID(),
      status: "uploading" as const,
    }));
    setFiles((prev) => [...prev, ...arr]);

    const succeeded: { name: string }[] = [];
    for (const entry of arr) {
      try {
        await uploadFile(entry.file);
        setFiles((prev) =>
          prev.map((f) => (f.id === entry.id ? { ...f, status: "done" } : f))
        );
        succeeded.push({ name: entry.file.name });
      } catch {
        setFiles((prev) =>
          prev.map((f) => (f.id === entry.id ? { ...f, status: "error" } : f))
        );
      }
    }
    if (succeeded.length) onUploadComplete?.(succeeded);
  }, [onUploadComplete]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      if (e.dataTransfer.files.length) handleUpload(e.dataTransfer.files);
    },
    [handleUpload]
  );

  const removeFile = (id: string) => setFiles((prev) => prev.filter((f) => f.id !== id));

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`
          relative cursor-pointer rounded-2xl border-2 border-dashed p-7 text-center
          transition-all duration-500 group overflow-hidden noise-overlay
          ${isDragOver
            ? "border-primary/60 bg-primary/5 scale-[1.015] glow-md"
            : "border-border/40 hover:border-primary/30 hover:bg-accent/20"
          }
        `}
      >
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 mesh-bg" />
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          className="hidden"
          onChange={(e) => e.target.files && handleUpload(e.target.files)}
        />
        <div className={`relative mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl transition-all duration-500 ${
          isDragOver
            ? "bg-primary/15 text-primary scale-110 glow-sm"
            : "bg-gradient-to-br from-secondary to-muted text-muted-foreground group-hover:from-primary/10 group-hover:to-accent group-hover:text-primary group-hover:scale-105"
        }`}>
          <CloudUpload className="h-7 w-7 transition-transform duration-500 group-hover:-translate-y-0.5" />
          {isDragOver && <div className="absolute inset-0 rounded-2xl animate-border-glow border-2 border-primary/30" />}
        </div>
        <p className="relative text-sm font-semibold text-foreground">
          Drag & drop files here or{" "}
          <span className="text-primary font-bold underline underline-offset-2 decoration-primary/30">browse</span>
        </p>
        <p className="relative mt-1.5 text-xs text-muted-foreground">
          PDF, DOC, DOCX, TXT — up to 25 MB
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-1.5">
          {files.map((f, i) => (
            <div
              key={f.id}
              className="group/file flex items-center gap-3 rounded-xl border border-border/30 glass px-4 py-3 transition-all duration-300 hover:glow-ring animate-fade-in"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-accent text-primary transition-all duration-300 group-hover/file:from-primary/15 group-hover/file:scale-105">
                <File className="h-4.5 w-4.5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-foreground truncate">{f.file.name}</p>
                <p className="text-[11px] text-muted-foreground font-mono">{(f.file.size / 1024).toFixed(1)} KB</p>
              </div>
              <div className="flex items-center gap-2">
                {f.status === "uploading" && <Loader2 className="h-4 w-4 text-primary animate-spin shrink-0" />}
                {f.status === "done" && <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />}
                {f.status === "error" && <AlertCircle className="h-4 w-4 text-destructive shrink-0" />}
                <button
                  onClick={(e) => { e.stopPropagation(); removeFile(f.id); }}
                  className="rounded-lg p-1.5 text-muted-foreground opacity-0 group-hover/file:opacity-100 hover:text-destructive hover:bg-destructive/10 transition-all duration-200"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
