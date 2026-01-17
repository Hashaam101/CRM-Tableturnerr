import { Skeleton } from "@/components/ui/skeleton";

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header Skeleton */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-[200px]" />
        <Skeleton className="h-4 w-[300px]" />
      </div>

      {/* Content Skeleton - Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Skeleton className="h-[120px] w-full rounded-xl" />
        <Skeleton className="h-[120px] w-full rounded-xl" />
        <Skeleton className="h-[120px] w-full rounded-xl" />
        <Skeleton className="h-[120px] w-full rounded-xl" />
      </div>

      {/* Main Content Area */}
      <Skeleton className="h-[400px] w-full rounded-xl" />
    </div>
  );
}

export function CompaniesTableSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header Skeleton */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-2">
          <Skeleton className="h-8 w-[200px]" />
          <Skeleton className="h-4 w-[300px]" />
        </div>
        <div className="flex items-center gap-2">
          <Skeleton className="h-10 w-full sm:w-64 rounded-lg" />
          <Skeleton className="h-10 w-32 rounded-lg" />
          <Skeleton className="h-10 w-10 rounded-lg" />
        </div>
      </div>

      {/* Table Skeleton */}
      <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl overflow-hidden">
        {/* Table Header */}
        <div className="border-b border-[var(--card-border)] bg-[var(--sidebar-bg)] p-4 flex gap-4">
          <Skeleton className="h-6 w-1/4" />
          <Skeleton className="h-6 w-1/6" />
          <Skeleton className="h-6 w-1/6" />
          <Skeleton className="h-6 w-1/6" />
          <Skeleton className="h-6 w-1/6" />
        </div>
        
        {/* Table Rows */}
        <div className="divide-y divide-[var(--card-border)]">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="p-4 flex gap-4 items-center">
              <Skeleton className="h-5 w-1/4" />
              <Skeleton className="h-5 w-1/6" />
              <Skeleton className="h-5 w-1/6" />
              <Skeleton className="h-5 w-1/6" />
              <Skeleton className="h-5 w-1/6" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
