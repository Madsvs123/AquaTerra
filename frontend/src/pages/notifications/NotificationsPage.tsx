import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { notifyApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";

export default function NotificationsPage() {
  const client = useQueryClient();
  const query = useQuery({ queryKey: ["notifications"], queryFn: notifyApi.list });
  const read = useMutation({ mutationFn: notifyApi.read, onSuccess: () => client.invalidateQueries({ queryKey: ["notifications"] }) });
  const readAll = useMutation({ mutationFn: notifyApi.readAll, onSuccess: () => client.invalidateQueries({ queryKey: ["notifications"] }) });

  return (
    <Page title="Notifications" lede="Alerts, recommendations, and maintenance notices for this workspace." action={<button className="btn-ghost" onClick={() => readAll.mutate()}>Mark all read</button>}>
      {(query.data?.results ?? []).map((note) => (
        <article key={note.id} className="card" style={{ marginBottom: 10 }}>
          <div className="factor">
            <strong>{note.title}</strong>
            {!note.read_at && <button className="btn-ghost" onClick={() => read.mutate(note.id)}>Read</button>}
          </div>
          <p className="muted">{note.body}</p>
        </article>
      ))}
      {!query.data.results.length && <p className="empty">Inbox is clear.</p>}
    </Page>
  );
}
