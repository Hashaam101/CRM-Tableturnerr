import React from 'react';

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Cold Call Details</h1>
      <p className="text-[var(--muted)]">Displaying details for ID: {id}</p>
      <div className="mt-4 p-4 border border-[var(--card-border)] rounded bg-[var(--card-bg)]">
        <p>Work in progress...</p>
      </div>
    </div>
  );
}