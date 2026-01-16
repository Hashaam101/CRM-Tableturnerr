import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: number;
    positive: boolean;
  };
  variant?: 'default' | 'primary' | 'accent';
}

export function StatsCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  variant = 'default'
}: StatsCardProps) {
  const iconStyles = {
    default: 'bg-[var(--card-hover)] text-[var(--foreground)]',
    primary: 'bg-[var(--primary-subtle)] text-[var(--primary)]',
    accent: 'bg-[var(--accent-red-subtle)] text-[var(--accent-red)]',
  };

  return (
    <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl p-5 card-interactive">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-xs uppercase tracking-wider text-[var(--muted)] font-medium">
            {title}
          </p>
          <p className="text-2xl font-bold mt-2 tracking-tight">{value}</p>
          {description && (
            <p className="text-xs text-[var(--muted)] mt-1 truncate">{description}</p>
          )}
          {trend && (
            <div
              className={cn(
                'flex items-center gap-1 mt-2',
                trend.positive ? 'text-[var(--success)]' : 'text-[var(--error)]'
              )}
            >
              {trend.positive ? (
                <TrendingUp size={14} strokeWidth={2} />
              ) : (
                <TrendingDown size={14} strokeWidth={2} />
              )}
              <span className="text-xs font-medium">
                {trend.positive ? '+' : ''}{trend.value}% vs last week
              </span>
            </div>
          )}
        </div>
        <div className={cn('p-2.5 rounded-lg', iconStyles[variant])}>
          <Icon size={20} strokeWidth={1.5} />
        </div>
      </div>
    </div>
  );
}
