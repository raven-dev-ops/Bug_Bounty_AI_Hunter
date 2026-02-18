import { FormEvent, useEffect, useState } from "react";
import {
  autoLinkTasks,
  createTask,
  deleteTask,
  getTaskBoard,
  updateTask,
  type TaskRow,
} from "../api/client";

const COLUMNS = ["open", "in_progress", "blocked", "done"] as const;

type ColumnName = (typeof COLUMNS)[number];

export function TaskBoardPage() {
  const [board, setBoard] = useState<Record<string, TaskRow[]>>({});
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState<ColumnName>("open");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function refreshBoard() {
    const columns = await getTaskBoard();
    setBoard(columns);
  }

  useEffect(() => {
    refreshBoard().catch((reason: unknown) => {
      const text = reason instanceof Error ? reason.message : "Failed to load task board";
      setError(text);
    });
  }, []);

  async function onCreateTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await createTask({ title: title.trim(), status });
      setTitle("");
      setStatus("open");
      setMessage("Task created.");
      await refreshBoard();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to create task";
      setError(text);
    }
  }

  async function onChangeStatus(task: TaskRow, nextStatus: ColumnName) {
    setError("");
    try {
      await updateTask(task.id, { status: nextStatus });
      await refreshBoard();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to update task";
      setError(text);
    }
  }

  async function onDeleteTask(taskId: string) {
    setError("");
    try {
      await deleteTask(taskId);
      await refreshBoard();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to delete task";
      setError(text);
    }
  }

  async function onAutoLink() {
    setError("");
    setMessage("");
    try {
      const created = await autoLinkTasks();
      setMessage(`Automation created ${created} linked tasks.`);
      await refreshBoard();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to auto-link tasks";
      setError(text);
    }
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #198</p>
        <h1 className="text-3xl font-semibold text-text">Task Board</h1>
        <p className="max-w-3xl text-sm text-muted">
          Kanban board with status lanes and auto-link rules that create tasks from findings.
        </p>
      </header>

      <form className="flex flex-wrap items-end gap-2 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onCreateTask}>
        <label className="min-w-[260px] flex-1 space-y-1">
          <span className="text-xs text-muted">Task title</span>
          <input
            className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            required
          />
        </label>
        <label className="space-y-1">
          <span className="text-xs text-muted">Status</span>
          <select
            className="rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
            value={status}
            onChange={(event) => setStatus(event.target.value as ColumnName)}
          >
            {COLUMNS.map((column) => (
              <option key={column} value={column}>
                {column}
              </option>
            ))}
          </select>
        </label>
        <button
          type="submit"
          className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
        >
          Add task
        </button>
        <button
          type="button"
          className="rounded-lg border border-border bg-bg/40 px-3 py-2 text-xs text-text hover:border-accent"
          onClick={onAutoLink}
        >
          Auto-link from findings
        </button>
      </form>

      <div className="grid gap-3 xl:grid-cols-4">
        {COLUMNS.map((column) => (
          <div key={column} className="rounded-2xl border border-border bg-surface/85 p-3">
            <p className="text-xs uppercase tracking-[0.18em] text-muted">{column}</p>
            <div className="mt-3 space-y-2">
              {(board[column] ?? []).map((task) => (
                <div key={task.id} className="rounded-lg border border-border bg-bg/30 p-3">
                  <p className="text-sm font-semibold text-text">{task.title}</p>
                  <p className="text-xs text-muted">{task.id}</p>
                  <p className="text-xs text-muted">
                    finding: {task.linked_finding_id ?? "-"} | program: {task.linked_program_id ?? "-"}
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <select
                      className="rounded-lg border border-border bg-bg/50 px-2 py-1 text-xs text-text"
                      value={task.status}
                      onChange={(event) => onChangeStatus(task, event.target.value as ColumnName)}
                    >
                      {COLUMNS.map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      className="rounded-lg border border-red-500/40 bg-red-500/10 px-2 py-1 text-xs text-red-200"
                      onClick={() => onDeleteTask(task.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
              {(board[column] ?? []).length === 0 ? (
                <p className="text-xs text-muted">No tasks.</p>
              ) : null}
            </div>
          </div>
        ))}
      </div>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-300">{message}</p> : null}
    </section>
  );
}
