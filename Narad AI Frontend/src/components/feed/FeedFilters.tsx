"use client";

const filters = ["All", "Today", "Yesterday", "This Week", "This Month"];

interface FeedFiltersProps {
  active: string;
  onChange: (filter: string) => void;
}

export function FeedFilters({ active, onChange }: FeedFiltersProps) {
  return (
    <div className="flex gap-2 flex-wrap">
      {filters.map((filter) => (
        <button
          key={filter}
          onClick={() => onChange(filter)}
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${
            active === filter
              ? "bg-violet-500/20 text-violet-400 border border-violet-500/30"
              : "bg-slate-800/50 text-slate-400 border border-slate-700/50 hover:border-slate-600"
          }`}
        >
          {filter}
        </button>
      ))}
    </div>
  );
}
