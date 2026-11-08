import React from "react";

interface SafeAnswerRendererProps {
  text: string;
  onCitationClick?: (citationNumber: number) => void;
  selectedCitation?: number | null;
}

export const SafeAnswerRenderer: React.FC<SafeAnswerRendererProps> = ({
  text,
  onCitationClick,
  selectedCitation,
}) => {
  if (!text) return null;

  // Render inline text segments with **bold** and [n] citation chips
  const renderInline = (line: string): React.ReactNode[] => {
    // Regex splits by [n], [n, m], or **bold**
    const parts = line.split(/(\[\d+(?:,\s*\d+)*\]|\*\*[^*]+\*\*)/g);

    return parts.map((part, idx) => {
      if (!part) return null;

      // Citation match: [1] or [1, 2, 3]
      const citMatch = part.match(/^\[(\d+(?:,\s*\d+)*)\]$/);
      if (citMatch) {
        const numbers = citMatch[1].split(",").map((n) => parseInt(n.trim(), 10));
        return (
          <span key={idx} className="inline-flex gap-1 mx-1 align-baseline">
            {numbers.map((num) => (
              <button
                key={num}
                type="button"
                onClick={() => onCitationClick?.(num)}
                className={`inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-semibold rounded-md border transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                  selectedCitation === num
                    ? "bg-emerald-600 text-white border-emerald-700 shadow-sm"
                    : "bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800 hover:bg-emerald-100 dark:hover:bg-emerald-900"
                }`}
                title={`View cited official source [${num}]`}
                aria-label={`View cited source ${num}`}
              >
                [{num}]
              </button>
            ))}
          </span>
        );
      }

      // Bold match: **text**
      if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
        return <strong key={idx} className="font-semibold text-zinc-900 dark:text-zinc-100">{part.slice(2, -2)}</strong>;
      }

      // Plain text span
      return <span key={idx}>{part}</span>;
    });
  };

  // Split into paragraph blocks
  const paragraphs = text.split(/\n\n+/);

  return (
    <div className="space-y-3 leading-relaxed text-zinc-800 dark:text-zinc-200 text-base">
      {paragraphs.map((para, pIdx) => {
        const trimmed = para.trim();
        if (!trimmed) return null;

        // Check if paragraph is composed of bullet points
        const lines = trimmed.split("\n");
        const isBulletList = lines.every(
          (l) => l.trim().startsWith("* ") || l.trim().startsWith("- ") || l.trim().startsWith("• ")
        );

        if (isBulletList) {
          return (
            <ul key={pIdx} className="list-disc pl-5 space-y-1.5 marker:text-emerald-600 dark:marker:text-emerald-400">
              {lines.map((bullet, bIdx) => {
                const cleaned = bullet.replace(/^[*•-]\s*/, "");
                return <li key={bIdx}>{renderInline(cleaned)}</li>;
              })}
            </ul>
          );
        }

        // Regular paragraph or mixed lines
        return (
          <p key={pIdx}>
            {lines.map((line, lIdx) => (
              <React.Fragment key={lIdx}>
                {renderInline(line)}
                {lIdx < lines.length - 1 && <br />}
              </React.Fragment>
            ))}
          </p>
        );
      })}
    </div>
  );
};
