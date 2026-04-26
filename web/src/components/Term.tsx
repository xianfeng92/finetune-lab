import { useEffect, useRef, useState } from "react";
import { lookupTerm } from "../glossary";

export function Term(props: { term?: string; children: React.ReactNode }) {
  const key = props.term ?? (typeof props.children === "string" ? props.children : "");
  const entry = lookupTerm(key);
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLSpanElement | null>(null);
  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);
  if (!entry) return <>{props.children}</>;
  return (
    <span ref={wrapRef} className="term-wrap">
      <span
        className="term"
        tabIndex={0}
        aria-describedby={open ? `term-pop-${key}` : undefined}
        onClick={(e) => { e.stopPropagation(); setOpen((v) => !v); }}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setOpen((v) => !v); }
          if (e.key === "Escape") setOpen(false);
        }}
      >
        {props.children}
      </span>
      {open ? (
        <span role="tooltip" id={`term-pop-${key}`} className="term-pop">{entry.short}</span>
      ) : null}
    </span>
  );
}
