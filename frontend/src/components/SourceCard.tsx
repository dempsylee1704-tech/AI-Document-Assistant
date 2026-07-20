import type { Source } from "@/lib/api";
import { FileText, Layers, Tag, ExternalLink } from "lucide-react";

function scoreGradient(score: number) {
  if (score >= 0.7) return "from-emerald-500 to-emerald-400";
  if (score >= 0.4) return "from-amber-500 to-amber-400";
  return "from-red-500 to-red-400";
}

function scoreBg(score: number) {
  if (score >= 0.7) return "bg-emerald-500/10 text-emerald-600 ring-emerald-500/20";
  if (score >= 0.4) return "bg-amber-500/10 text-amber-600 ring-amber-500/20";
  return "bg-red-500/10 text-red-600 ring-red-500/20";
}

function scoreLabel(_score: number) {
  return "Relevance";
}

export function SourceCard({ source, index }: { source: Source; index: number }) {
  const pageNumber = source.page ?? source.page_start;
  const href = source.pdf_url ?? undefined;

  const handleClick = (e: React.MouseEvent) => {
    if (!href) return;
    e.preventDefault();
    e.stopPropagation();
    window.open(source.pdf_url, "_blank", "noopener,noreferrer");
  };

  const hasPageRange =
    source.page_start && source.page_end && source.page_start !== source.page_end;

  const commonClass =
    "group relative block rounded-2xl glass p-5 transition-all duration-500 hover:glass-elevated hover:-translate-y-1 hover:scale-[1.01] animate-fade-in noise-overlay focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50";

  const content = (
    <>
      {/* Top gradient accent */}
      <div className="absolute top-0 left-4 right-4 h-[2px] rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${scoreGradient(source.score)} transition-all duration-700 opacity-40 group-hover:opacity-100`}
          style={{ width: `${Math.max(source.score * 100, 15)}%` }}
        />
      </div>

      <div className="relative flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/8 to-accent text-primary transition-all duration-400 group-hover:from-primary/15 group-hover:shadow-lg group-hover:shadow-primary/10 group-hover:scale-105">
            <FileText className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-bold text-foreground leading-tight group-hover:text-primary transition-colors duration-300">{source.source_filename}</p>
            <p className="text-[11px] text-muted-foreground mt-1 font-mono tracking-wide truncate">{source.doc_id}</p>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1 shrink-0">
          <span className="text-[10px] text-muted-foreground/60 font-medium uppercase tracking-wider">
            {scoreLabel(source.score)}
          </span>
          <span className="text-[11px] text-muted-foreground tabular-nums">
            {(source.score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      <div className="relative mt-4 flex flex-wrap gap-2">
        {pageNumber ? (
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-primary/10 backdrop-blur-sm px-3 py-1.5 text-xs font-semibold text-primary ring-1 ring-primary/20 transition-colors group-hover:bg-primary/20">
            <Layers className="h-3 w-3" />
            Page {pageNumber}
            {hasPageRange ? ` (${source.page_start}–${source.page_end})` : ""}
          </span>
        ) : null}
        <span className="inline-flex items-center gap-1.5 rounded-lg bg-secondary/60 backdrop-blur-sm px-3 py-1.5 text-xs text-muted-foreground transition-colors group-hover:bg-secondary/90 group-hover:text-foreground">
          <Tag className="h-3 w-3 text-violet/60" />
          {source.category}
        </span>
      </div>

      {/* Hover reveal action */}
      {href ? (
        <div className="absolute top-5 right-5 opacity-0 group-hover:opacity-100 translate-x-1 group-hover:translate-x-0 transition-all duration-300">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary hover:bg-primary/20 cursor-pointer transition-colors">
            <ExternalLink className="h-3.5 w-3.5" />
          </div>
        </div>
      ) : null}
    </>
  );

  if (href) {
    return (
      <a
        href={href}
        onClick={handleClick}
        target="_blank"
        rel="noopener noreferrer"
        title={`Open ${source.source_filename}${pageNumber ? ` (page ${pageNumber})` : ""}`}
        className={`${commonClass} cursor-pointer`}
        style={{ animationDelay: `${index * 100}ms` }}
      >
        {content}
      </a>
    );
  }

  return (
    <div
      className={commonClass}
      style={{ animationDelay: `${index * 100}ms` }}
    >
      {content}
    </div>
  );
}
