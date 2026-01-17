import { Settings } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-[var(--muted)] mt-1">Configure application settings</p>
      </div>

      <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl p-16 text-center">
        <div className="w-12 h-12 rounded-full bg-[var(--primary-subtle)] flex items-center justify-center mx-auto mb-4">
          <Settings size={24} className="text-[var(--primary)]" />
        </div>
        <h2 className="text-sm font-medium">Settings module</h2>
        <p className="text-xs text-[var(--muted)] mt-1">Configuration options coming soon</p>
      </div>
    </div>
  );
}
