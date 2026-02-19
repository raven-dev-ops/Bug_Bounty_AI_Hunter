import { expect, test } from "@playwright/test";

test("visual: overview desktop shell", async ({ page }) => {
  await page.goto("/overview");
  await expect(page.getByRole("heading", { level: 1, name: "Overview" })).toBeVisible();
  await expect(page).toHaveScreenshot("overview-desktop.png", {
    fullPage: true,
    animations: "disabled",
  });
});

test("visual: settings mobile shell", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/settings");
  await expect(page.getByRole("heading", { level: 1, name: "Settings" })).toBeVisible();
  await expect(page).toHaveScreenshot("settings-mobile.png", {
    fullPage: true,
    animations: "disabled",
  });
});
