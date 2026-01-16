import { Building2, Phone, Users, UserCog, Activity } from 'lucide-react';
import { StatsCard } from '@/components/stats-card';
import { pb } from '@/lib/pocketbase';
import { COLLECTIONS } from '@/lib/types';
import type { EventLog } from '@/lib/types';
import { timeAgo } from '@/lib/utils';

async function getStats() {
  try {
    const [companies, coldCalls, leads, users] = await Promise.all([
      pb.collection(COLLECTIONS.COMPANIES).getList(1, 1),
      pb.collection(COLLECTIONS.COLD_CALLS).getList(1, 1),
      pb.collection(COLLECTIONS.LEADS).getList(1, 1),
      pb.collection(COLLECTIONS.USERS).getList(1, 1, { filter: 'status != "suspended"' }),
    ]);

    return {
      totalCompanies: companies.totalItems,
      totalColdCalls: coldCalls.totalItems,
      totalLeads: leads.totalItems,
      activeMembers: users.totalItems,
    };
  } catch (error) {
    console.error('Failed to fetch stats:', error);
    return {
      totalCompanies: 0,
      totalColdCalls: 0,
      totalLeads: 0,
      activeMembers: 0,
    };
  }
}

async function getRecentActivity() {
  try {
    const result = await pb.collection(COLLECTIONS.EVENT_LOGS).getList<EventLog>(1, 10, {
      sort: '-created',
      expand: 'user,actor,target,cold_call',
    });
    return result.items;
  } catch (error) {
    console.error('Failed to fetch recent activity:', error);
    return [];
  }
}

function getEventDescription(event: EventLog): string {
  const user = event.expand?.user?.name || 'Unknown';
  const actor = event.expand?.actor?.username || '';
  const target = event.expand?.target?.username || '';

  switch (event.event_type) {
    case 'Outreach':
      return `${actor || user} sent outreach to ${target}`;
    case 'Cold Call':
      return `${user} made a cold call`;
    case 'User':
      return event.details || `${user} performed an action`;
    case 'System':
      return event.details || 'System event';
    case 'Change in Tar Info':
      return `${user} updated target info for ${target}`;
    case 'Tar Exception Toggle':
      return `${user} toggled exception for ${target}`;
    default:
      return event.details || 'Activity logged';
  }
}

function getEventBadge(eventType: string): { bg: string; text: string } {
  switch (eventType) {
    case 'Outreach':
      return { bg: 'bg-[var(--info-subtle)]', text: 'text-[var(--info)]' };
    case 'Cold Call':
      return { bg: 'bg-[var(--success-subtle)]', text: 'text-[var(--success)]' };
    case 'User':
      return { bg: 'bg-[var(--primary-subtle)]', text: 'text-[var(--primary)]' };
    case 'System':
      return { bg: 'bg-[var(--card-hover)]', text: 'text-[var(--muted)]' };
    default:
      return { bg: 'bg-[var(--card-hover)]', text: 'text-[var(--foreground)]' };
  }
}

export default async function OverviewPage() {
  const [stats, recentActivity] = await Promise.all([
    getStats(),
    getRecentActivity(),
  ]);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Overview</h1>
        <p className="text-sm text-[var(--muted)] mt-1">Welcome to your CRM dashboard</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Companies"
          value={stats.totalCompanies}
          icon={Building2}
          description="Businesses in database"
          variant="default"
        />
        <StatsCard
          title="Cold Calls"
          value={stats.totalColdCalls}
          icon={Phone}
          description="Calls recorded"
          variant="accent"
        />
        <StatsCard
          title="Leads"
          value={stats.totalLeads}
          icon={Users}
          description="Prospects tracked"
          variant="primary"
        />
        <StatsCard
          title="Team Members"
          value={stats.activeMembers}
          icon={UserCog}
          description="Active users"
          variant="default"
        />
      </div>

      {/* Recent Activity */}
      <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-[var(--card-border)] flex items-center gap-2">
          <Activity size={18} strokeWidth={1.5} className="text-[var(--muted)]" />
          <h2 className="font-semibold text-sm">Recent Activity</h2>
        </div>
        <div>
          {recentActivity.length === 0 ? (
            <div className="px-5 py-16 text-center">
              <div className="w-12 h-12 rounded-full bg-[var(--card-hover)] flex items-center justify-center mx-auto mb-4">
                <Activity size={24} className="text-[var(--muted)]" />
              </div>
              <p className="text-sm font-medium">No recent activity</p>
              <p className="text-xs text-[var(--muted)] mt-1">Activity will appear here as events are logged</p>
            </div>
          ) : (
            <div className="divide-y divide-[var(--card-border)]">
              {recentActivity.map((event) => {
                const badge = getEventBadge(event.event_type);
                return (
                  <div key={event.id} className="px-5 py-3.5 flex items-start gap-4 hover:bg-[var(--card-hover)] transition-colors">
                    <div className="mt-0.5">
                      <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider ${badge.bg} ${badge.text}`}>
                        {event.event_type}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm">{getEventDescription(event)}</p>
                      {event.source && (
                        <span className="text-xs text-[var(--muted)]">via {event.source}</span>
                      )}
                    </div>
                    <span className="text-xs text-[var(--muted)] shrink-0">
                      {timeAgo(event.created)}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
