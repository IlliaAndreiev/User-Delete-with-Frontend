import React, { useCallback, useEffect, useMemo, useState } from "react";

// ===== Типи =====
export type Role = "admin" | "member";
export type Participant = { id: string; name: string; role: Role; roomId: string };

// ===== API-клієнти =====
// сирий тип з бекенду (може не мати name / roomId)
type RawParticipant = {
  id: string;
  name?: string;
  role: Role;
  roomId?: string;
  room_id?: string;
};

async function fetchParticipants(apiBase: string, roomId: string): Promise<Participant[]> {
  const url = `${apiBase.replace(/\/$/, "")}/users/participants?roomId=${encodeURIComponent(roomId)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`LOAD_FAILED_${res.status}`);

  const raw: RawParticipant[] = await res.json();

  // Нормалізація під те, що чекає UI
  return raw.map((p) => ({
    id: p.id,
    name: p.name ?? p.id,            // якщо name немає – показуємо id
    role: p.role,
    roomId: p.roomId ?? p.room_id!,  // roomId або room_id з бекенду
  }));
}

async function deleteParticipantAPI({
  apiBase,
  userId,
  adminCode,
}: {
  apiBase: string;
  userId: string;
  adminCode: string;
}): Promise<{ removedUserId: string; roomId: string; participantsCount: number; message: string }> {
  const url = `${apiBase.replace(/\/$/, "")}/users/${encodeURIComponent(userId)}?userCode=${encodeURIComponent(adminCode)}`;
  const res = await fetch(url, { method: "DELETE" });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = body?.detail || `HTTP_${res.status}`;
    const err = new Error(detail) as any;
    err.status = res.status;
    throw err;
  }
  return body;
}

// ===== Допоміжні =====
function explainError(code: string): string {
  switch (code) {
    case "USER_NOT_FOUND": return "Користувача не знайдено.";
    case "ADMIN_NOT_FOUND": return "Адмін-код не знайдено.";
    case "NOT_ADMIN": return "Тільки адміністратор може видаляти учасників.";
    case "DIFFERENT_ROOMS": return "Адмін і користувач у різних кімнатах.";
    case "CANNOT_DELETE_SELF": return "Адміністратор не може видалити себе.";
    case "ROOM_CLOSED_OR_LOCKED": return "Кімната заблокована для змін.";
    default: return code || "Невідома помилка.";
  }
}

function TrashIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" className={className} aria-hidden>
      <path d="M3 6h18" />
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6M14 11v6" />
    </svg>
  );
}

function ConfirmModal({
  open, title, description, confirmLabel = "Remove", cancelLabel = "Cancel", onConfirm, onCancel,
}: {
  open: boolean; title: string; description?: string; confirmLabel?: string; cancelLabel?: string;
  onConfirm: () => void; onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div aria-hidden className="absolute inset-0 bg-black/50" onClick={onCancel} />
      <div role="dialog" data-testid="confirm-modal" aria-modal="true" className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="text-xl font-semibold">{title}</h2>
        {description ? <p className="mt-2 text-sm text-gray-600">{description}</p> : null}
        <div className="mt-6 flex items-center justify-end gap-3">
          <button role="button" onClick={onCancel} className="rounded-xl border px-4 py-2 text-sm font-medium hover:bg-gray-50">
            {cancelLabel}
          </button>
          <button role="button" onClick={onConfirm} className="rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700">
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// ===== Головний компонент =====
export default function DeleteParticipantsDemo({
  adminCode,
  apiBase = "/api",
  roomId,
}: {
  adminCode: string;
  apiBase?: string;
  roomId: string;
}) {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ type: "success" | "error"; msg: string } | null>(null);

  const byId = useMemo(() => new Map(participants.map(p => [p.id, p])), [participants]);

  // Завантаження зі сторони бекенду (замість initialParticipants)
  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchParticipants(apiBase, roomId);
      setParticipants(data);
    } catch (e) {
      setToast({ type: "error", msg: "Не вдалося завантажити учасників." });
    } finally {
      setLoading(false);
    }
  }, [apiBase, roomId]);

  useEffect(() => {
    reload();
  }, [reload]);

  const handleDelete = useCallback(async (userId: string) => {
    // оптимістичне видалення з rollback
    const prev = participants;
    const next = prev.filter(p => p.id !== userId);
    setPendingId(userId);
    setParticipants(next);

    try {
      await deleteParticipantAPI({ apiBase, userId, adminCode });
      setToast({ type: "success", msg: "Учасника видалено." });
      // опційно: підтягнути сучасний список з сервера
      // await reload();
    } catch (e: any) {
      setParticipants(prev); // rollback
      setToast({ type: "error", msg: explainError(e?.message || "UNKNOWN_ERROR") });
    } finally {
      setPendingId(null);
      setConfirmId(null);
    }
  }, [participants, apiBase, adminCode]);

  return (
    <div className="mx-auto max-w-2xl p-6">
      <h1 className="text-2xl font-bold">Who’s Playing?</h1>

      {/* стани завантаження */}
      {loading ? (
        <div className="mt-4 rounded-2xl border bg-white p-4 text-sm text-gray-500">Завантаження…</div>
      ) : (
        <ul className="mt-4 divide-y rounded-2xl border bg-white">
          {participants.map((p) => (
            <li key={p.id} className="flex items-center justify-between gap-3 px-4 py-3">
              <div>
                <div className="font-medium">{p.name}</div>
                <div className="text-xs text-gray-500">{p.role} · room {p.roomId}</div>
              </div>
              <div className="flex items-center gap-2">
                {p.role === "admin" ? (
                  <span className="text-xs text-gray-400">admin</span>
                ) : (
                  <button
                    className="inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
                    aria-label={`Remove ${p.name}`}
                    disabled={pendingId === p.id}
                    onClick={() => setConfirmId(p.id)}
                  >
                    <TrashIcon />
                    Remove
                  </button>
                )}
              </div>
            </li>
          ))}
          {participants.length === 0 && !loading && (
            <li className="px-4 py-8 text-center text-sm text-gray-500">Немає учасників</li>
          )}
        </ul>
      )}

      {/* модал підтвердження */}
      <ConfirmModal
        open={!!confirmId}
        title="Remove participant?"
        description={confirmId ? `Підтвердьте видалення користувача ${byId.get(confirmId)?.name ?? confirmId}.` : undefined}
        onCancel={() => setConfirmId(null)}
        onConfirm={() => confirmId && handleDelete(confirmId)}
        confirmLabel={pendingId ? "Removing..." : "Remove"}
      />

      {/* toast */}
      {toast && (
        <div
          role="status"
          className={`fixed bottom-4 right-4 rounded-xl px-4 py-3 shadow-lg ${toast.type === "success" ? "bg-emerald-600 text-white" : "bg-red-600 text-white"}`}
        >
          {toast.msg}
          <button className="ml-3 underline" onClick={() => setToast(null)}>Закрити</button>
        </div>
      )}

      <div className="mt-8 text-xs text-gray-500">
        API base: <code>{apiBase}</code> · Admin code: <code>{adminCode}</code> · Room: <code>{roomId}</code>
        <button className="ml-3 underline" onClick={reload}>Перезавантажити</button>
      </div>
    </div>
  );
}
