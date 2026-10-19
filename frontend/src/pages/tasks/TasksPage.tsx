import { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { workApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { bandClass } from "@/lib/utils";

export default function TasksPage() {
  const client = useQueryClient();
  const query = useQuery({ queryKey: ["tasks"], queryFn: workApi.list });
  const create = useMutation({ mutationFn: workApi.create, onSuccess: () => client.invalidateQueries({ queryKey: ["tasks"] }) });
  const update = useMutation({ mutationFn: ({ id, status }: { id: string; status: string }) => workApi.update(id, { status }), onSuccess: () => client.invalidateQueries({ queryKey: ["tasks"] }) });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    create.mutate({ title: data.get("title"), details: data.get("details"), due_at: data.get("due_at") || null });
    event.currentTarget.reset();
  }

  return (
    <Page title="Tasks" lede="Field work, follow-ups, and crew assignments.">
      <div className="grid-2">
        <section className="card">
          {(query.data?.results ?? []).map((task) => (
            <article key={task.id} className="factor">
              <div>
                <strong>{task.title}</strong>
                <div className="muted">{task.details}</div>
              </div>
              <div className="btn-row">
                <span className={bandClass(task.status)}>{task.status}</span>
                {task.status !== "done" && <button className="btn-ghost" onClick={() => update.mutate({ id: task.id, status: "open" })}>Done</button>}
              </div>
            </article>
          ))}
        </section>
        <form className="card form" onSubmit={onSubmit}>
          <h3>New task</h3>
          <label>Title<input className="field" name="title" required /></label>
          <label>Details<textarea className="field" name="details" rows={3} /></label>
          <label>Due<input className="field" name="due_at" type="datetime-local" /></label>
          <button className="btn-primary">Add task</button>
        </form>
      </div>
    </Page>
  );
}
