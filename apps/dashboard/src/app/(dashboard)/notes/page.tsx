"use client";

import { useState, useEffect } from 'react';
import { pb } from '@/lib/pocketbase';
import { Note, COLLECTIONS, User } from '@/lib/types';
import { format } from 'date-fns';
import { Plus, Archive, Trash2, RotateCcw, FileText, Search, X, StickyNote } from 'lucide-react';
import { cn } from '@/lib/utils';

type Tab = 'active' | 'archived' | 'deleted';

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>('active');
  const [search, setSearch] = useState('');

  const [isEditing, setIsEditing] = useState(false);
  const [currentNote, setCurrentNote] = useState<Partial<Note>>({});

  useEffect(() => {
    fetchNotes();
  }, []);

  async function fetchNotes() {
    setLoading(true);
    try {
      const result = await pb.collection(COLLECTIONS.NOTES).getList<Note>(1, 200, {
        sort: '-updated',
        expand: 'created_by'
      });
      setNotes(result.items);
    } catch (error) {
      console.error("Error fetching notes:", error);
    } finally {
      setLoading(false);
    }
  }

  const filteredNotes = notes.filter(n => {
    const matchesSearch = n.title.toLowerCase().includes(search.toLowerCase()) ||
      n.note_text.toLowerCase().includes(search.toLowerCase());

    if (tab === 'active') return !n.is_archived && !n.is_deleted && matchesSearch;
    if (tab === 'archived') return n.is_archived && !n.is_deleted && matchesSearch;
    if (tab === 'deleted') return n.is_deleted && matchesSearch;
    return false;
  });

  async function handleSave() {
    try {
      const data = {
        title: currentNote.title || 'Untitled',
        note_text: currentNote.note_text || '',
        created_by: pb.authStore.model?.id,
        is_archived: currentNote.is_archived || false,
        is_deleted: currentNote.is_deleted || false
      };

      if (currentNote.id) {
        await pb.collection(COLLECTIONS.NOTES).update(currentNote.id, data);
      } else {
        await pb.collection(COLLECTIONS.NOTES).create(data);
      }
      setIsEditing(false);
      setCurrentNote({});
      fetchNotes();
    } catch (e) {
      alert("Error saving note: " + e);
    }
  }

  async function handleStatusChange(id: string, updates: Partial<Note>) {
    try {
      await pb.collection(COLLECTIONS.NOTES).update(id, updates);
      fetchNotes();
    } catch (e) {
      console.error(e);
    }
  }

  async function handleDeletePermanent(id: string) {
    if (!confirm("Permanently delete this note?")) return;
    try {
      await pb.collection(COLLECTIONS.NOTES).delete(id);
      fetchNotes();
    } catch (e) {
      console.error(e);
    }
  }

  if (isEditing) {
    return (
      <div className="h-full flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <input
            type="text"
            placeholder="Note Title"
            className="text-2xl font-bold bg-transparent border-none focus:outline-none focus:ring-0 w-full placeholder:text-[var(--muted)]"
            value={currentNote.title || ''}
            onChange={e => setCurrentNote({ ...currentNote, title: e.target.value })}
          />
          <div className="flex gap-2 shrink-0">
            <button
              onClick={() => setIsEditing(false)}
              className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-[var(--card-hover)] transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)] transition-colors"
            >
              Save
            </button>
          </div>
        </div>
        <textarea
          className="flex-1 w-full p-4 rounded-xl border border-[var(--card-border)] bg-[var(--card-bg)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)] resize-none font-mono text-sm placeholder:text-[var(--muted)]"
          placeholder="Write your note here (Markdown supported)..."
          value={currentNote.note_text || ''}
          onChange={e => setCurrentNote({ ...currentNote, note_text: e.target.value })}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Notes</h1>
            <p className="text-sm text-[var(--muted)] mt-1">Team notes and documentation</p>
          </div>
        </div>

        <button
          onClick={() => { setCurrentNote({}); setIsEditing(true); }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)] transition-colors"
        >
          <Plus size={16} />
          New Note
        </button>
      </div>

      {/* Tabs and Search */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="flex bg-[var(--card-bg)] border border-[var(--card-border)] p-1 rounded-lg">
          {(['active', 'archived', 'deleted'] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cn(
                'px-3 py-1.5 text-sm font-medium rounded-md capitalize transition-colors',
                tab === t
                  ? 'bg-[var(--foreground)] text-[var(--background)]'
                  : 'text-[var(--muted)] hover:text-[var(--foreground)]'
              )}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="relative flex-1 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" />
          <input
            type="text"
            placeholder="Search notes..."
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-[var(--card-border)] bg-[var(--card-bg)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Notes Grid */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-8 h-8 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-[var(--muted)]">Loading notes...</p>
        </div>
      ) : filteredNotes.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-12 h-12 rounded-full bg-[var(--card-hover)] flex items-center justify-center mx-auto mb-4">
            <StickyNote size={24} className="text-[var(--muted)]" />
          </div>
          <p className="text-sm font-medium">No notes found</p>
          <p className="text-xs text-[var(--muted)] mt-1">
            {search ? 'Try a different search term' : `No ${tab} notes yet`}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredNotes.map((note) => (
            <div
              key={note.id}
              className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl flex flex-col h-64 card-interactive"
            >
              <div className="p-4 flex-1 overflow-hidden">
                <div className="flex justify-between items-start gap-2 mb-3">
                  <h3 className="font-semibold text-sm truncate">{note.title}</h3>
                  <span className="text-[10px] text-[var(--muted)] uppercase tracking-wider shrink-0">
                    {format(new Date(note.updated), 'MMM d')}
                  </span>
                </div>
                <p className="text-sm text-[var(--muted)] whitespace-pre-wrap line-clamp-6">
                  {note.note_text}
                </p>
              </div>

              <div className="px-4 py-3 border-t border-[var(--card-border)] flex justify-between items-center">
                <span className="text-xs text-[var(--muted)]">
                  {(note.expand?.created_by as User)?.name || 'Unknown'}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => { setCurrentNote(note); setIsEditing(true); }}
                    className="p-1.5 rounded-md hover:bg-[var(--card-hover)] text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                    title="Edit"
                  >
                    <FileText size={14} />
                  </button>

                  {tab === 'active' && (
                    <>
                      <button
                        onClick={() => handleStatusChange(note.id, { is_archived: true })}
                        className="p-1.5 rounded-md hover:bg-[var(--card-hover)] text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                        title="Archive"
                      >
                        <Archive size={14} />
                      </button>
                      <button
                        onClick={() => handleStatusChange(note.id, { is_deleted: true })}
                        className="p-1.5 rounded-md hover:bg-[var(--error-subtle)] text-[var(--muted)] hover:text-[var(--error)] transition-colors"
                        title="Move to Trash"
                      >
                        <Trash2 size={14} />
                      </button>
                    </>
                  )}

                  {tab === 'archived' && (
                    <>
                      <button
                        onClick={() => handleStatusChange(note.id, { is_archived: false })}
                        className="p-1.5 rounded-md hover:bg-[var(--card-hover)] text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                        title="Unarchive"
                      >
                        <RotateCcw size={14} />
                      </button>
                      <button
                        onClick={() => handleStatusChange(note.id, { is_deleted: true })}
                        className="p-1.5 rounded-md hover:bg-[var(--error-subtle)] text-[var(--muted)] hover:text-[var(--error)] transition-colors"
                        title="Move to Trash"
                      >
                        <Trash2 size={14} />
                      </button>
                    </>
                  )}

                  {tab === 'deleted' && (
                    <>
                      <button
                        onClick={() => handleStatusChange(note.id, { is_deleted: false })}
                        className="p-1.5 rounded-md hover:bg-[var(--card-hover)] text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                        title="Restore"
                      >
                        <RotateCcw size={14} />
                      </button>
                      <button
                        onClick={() => handleDeletePermanent(note.id)}
                        className="p-1.5 rounded-md hover:bg-[var(--error-subtle)] text-[var(--muted)] hover:text-[var(--error)] transition-colors"
                        title="Delete Permanently"
                      >
                        <X size={14} />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
