import { FormEvent, useEffect, useState } from "react";
import {
  createNotification,
  listNotifications,
  sendNotification,
  setNotificationRead,
  type NotificationRow,
} from "../api/client";

export function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationRow[]>([]);
  const [channel, setChannel] = useState("slack");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [slackWebhook, setSlackWebhook] = useState("");
  const [smtpHost, setSmtpHost] = useState("");
  const [smtpFrom, setSmtpFrom] = useState("command-center@example.local");
  const [smtpTo, setSmtpTo] = useState("operator@example.local");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function refreshNotifications() {
    const items = await listNotifications(false);
    setNotifications(items);
  }

  useEffect(() => {
    refreshNotifications().catch((reason: unknown) => {
      const text = reason instanceof Error ? reason.message : "Failed to load notifications";
      setError(text);
    });
  }, []);

  async function onCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await createNotification({
        channel,
        title: title.trim(),
        body: body.trim(),
      });
      setTitle("");
      setBody("");
      setMessage("Notification created.");
      await refreshNotifications();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to create notification";
      setError(text);
    }
  }

  async function onDispatch() {
    setError("");
    setMessage("");
    try {
      await sendNotification({
        channel,
        title: title.trim(),
        body: body.trim(),
        slack_webhook_url: slackWebhook || undefined,
        smtp_host: smtpHost || undefined,
        smtp_port: 587,
        smtp_from: smtpFrom || undefined,
        smtp_to: smtpTo || undefined,
      });
      setMessage(`Dispatched ${channel} notification.`);
      await refreshNotifications();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to dispatch notification";
      setError(text);
    }
  }

  async function markRead(notificationId: string, nextRead: boolean) {
    setError("");
    try {
      await setNotificationRead(notificationId, nextRead);
      await refreshNotifications();
    } catch (reason: unknown) {
      const text = reason instanceof Error ? reason.message : "Failed to update notification";
      setError(text);
    }
  }

  return (
    <section className="space-y-6 animate-shell-enter">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Issue #184</p>
        <h1 className="text-3xl font-semibold text-text">Notifications Center</h1>
        <p className="max-w-3xl text-sm text-muted">
          Track generated notification events and capture Slack/SMTP placeholders for future integration wiring.
        </p>
      </header>

      <form className="space-y-3 rounded-2xl border border-border bg-surface/85 p-4" onSubmit={onCreate}>
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Create notification</p>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="space-y-1">
            <span className="text-xs text-muted">Channel</span>
            <select
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={channel}
              onChange={(event) => setChannel(event.target.value)}
            >
              <option value="slack">slack</option>
              <option value="email">email</option>
              <option value="system">system</option>
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-xs text-muted">Title</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
            />
          </label>
        </div>
        <label className="space-y-1">
          <span className="text-xs text-muted">Body</span>
          <textarea
            className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
            rows={3}
            value={body}
            onChange={(event) => setBody(event.target.value)}
            required
          />
        </label>
        <div className="flex gap-2">
          <button
            type="submit"
            className="rounded-lg border border-accent bg-accent/15 px-3 py-2 text-xs font-semibold text-text hover:bg-accent/25"
          >
            Add notification
          </button>
          <button
            type="button"
            className="rounded-lg border border-border bg-bg/40 px-3 py-2 text-xs text-text hover:border-accent"
            onClick={() => {
              void onDispatch();
            }}
          >
            Dispatch now
          </button>
        </div>
      </form>

      <div className="grid gap-4 lg:grid-cols-[1fr,1fr]">
        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Integration placeholders</p>
          <label className="mt-3 block space-y-1">
            <span className="text-xs text-muted">Slack webhook URL (placeholder)</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={slackWebhook}
              onChange={(event) => setSlackWebhook(event.target.value)}
              placeholder="https://hooks.slack.com/services/..."
            />
          </label>
          <label className="mt-3 block space-y-1">
            <span className="text-xs text-muted">SMTP host (placeholder)</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={smtpHost}
              onChange={(event) => setSmtpHost(event.target.value)}
              placeholder="smtp.example.com"
            />
          </label>
          <label className="mt-3 block space-y-1">
            <span className="text-xs text-muted">SMTP from</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={smtpFrom}
              onChange={(event) => setSmtpFrom(event.target.value)}
              placeholder="command-center@example.local"
            />
          </label>
          <label className="mt-3 block space-y-1">
            <span className="text-xs text-muted">SMTP to</span>
            <input
              className="w-full rounded-lg border border-border bg-bg/30 px-3 py-2 text-sm text-text"
              value={smtpTo}
              onChange={(event) => setSmtpTo(event.target.value)}
              placeholder="operator@example.local"
            />
          </label>
          <p className="mt-3 text-xs text-muted">
            Placeholder settings are local UI state only in MVP and are not persisted.
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-surface/85 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Events</p>
          <div className="mt-3 space-y-2">
            {notifications.map((item) => (
              <div key={item.id} className="rounded-lg border border-border bg-bg/30 p-3">
                <p className="text-sm font-semibold text-text">{item.title}</p>
                <p className="text-xs text-muted">{item.channel} | {item.created_at}</p>
                <p className="mt-1 text-sm text-muted">{item.body}</p>
                <button
                  type="button"
                  className="mt-2 rounded-lg border border-border bg-bg/50 px-2 py-1 text-xs text-text hover:border-accent"
                  onClick={() => markRead(item.id, item.read ? false : true)}
                >
                  Mark as {item.read ? "unread" : "read"}
                </button>
              </div>
            ))}
            {notifications.length === 0 ? (
              <p className="cc-empty-state text-sm">No notifications available.</p>
            ) : null}
          </div>
        </div>
      </div>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-300">{message}</p> : null}
    </section>
  );
}
