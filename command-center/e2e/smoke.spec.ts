import { expect, test } from "@playwright/test";

function uniqueSuffix(): string {
  return `${Date.now()}-${Math.round(Math.random() * 1_000_000)}`;
}

test("shell navigation and command palette route jumping", async ({ page }) => {
  await page.goto("/overview");
  await expect(page.getByRole("heading", { level: 1, name: "Overview" })).toBeVisible();

  await page.getByRole("link", { name: /Bounty Feed/ }).click();
  await expect(page).toHaveURL(/\/feed$/);
  await expect(page.getByRole("heading", { level: 1, name: "Bounty Feed" })).toBeVisible();

  await page.keyboard.press("ControlOrMeta+K");
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByPlaceholder("Search pages, for example: logs or reports").fill("task board");
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/\/tasks$/);
  await expect(page.getByRole("heading", { level: 1, name: "Task Board" })).toBeVisible();
});

test("workspaces flow: create workspace and record acknowledgement", async ({ page }) => {
  const suffix = uniqueSuffix();
  const workspaceSlug = `e2e-${suffix}`;
  const workspaceName = `E2E Workspace ${suffix}`;

  await page.goto("/workspaces");
  await expect(
    page.getByRole("heading", { level: 1, name: "Engagement Workspaces" }),
  ).toBeVisible();

  await page.getByLabel("Platform").first().fill("bugcrowd");
  await page.getByLabel("Slug").fill(workspaceSlug);
  await page.getByLabel("Name").fill(workspaceName);
  await page.getByLabel("Engagement URL").fill(`https://example.test/${workspaceSlug}`);
  await page.getByRole("button", { name: "Create and scaffold" }).click();

  const workspaceCard = page.getByRole("button", { name: new RegExp(workspaceName) });
  await expect(workspaceCard).toBeVisible();
  await workspaceCard.click();

  await page.getByLabel("Acknowledged by").fill("e2e-operator");
  await page.getByLabel("Authorized target").fill("app.example.test");
  await page.getByRole("button", { name: "Record acknowledgement" }).click();
  await expect(page.getByText(/Acknowledgement recorded for/)).toBeVisible();
});

test("notifications flow: create notification and toggle read state", async ({ page }) => {
  const suffix = uniqueSuffix();
  const title = `E2E Notification ${suffix}`;

  await page.goto("/notifications");
  await expect(
    page.getByRole("heading", { level: 1, name: "Notifications Center" }),
  ).toBeVisible();

  await page.getByLabel("Channel").selectOption("system");
  await page.getByLabel("Title").fill(title);
  await page.getByLabel("Body").fill("Smoke-test notification body");
  await page.getByRole("button", { name: "Add notification" }).click();

  await expect(page.getByText("Notification created.")).toBeVisible();
  const notificationCard = page.locator("div.rounded-lg", { hasText: title }).first();
  await expect(notificationCard).toBeVisible();

  await notificationCard.getByRole("button", { name: /Mark as/ }).click();
  await expect(notificationCard.getByRole("button", { name: /Mark as/ })).toBeVisible();
});
