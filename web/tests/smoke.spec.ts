import { expect, test } from "@playwright/test";

test("example selection evaluates and renders a verdict", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Blocked showcase: Hidden refund flow" }).click();
  await page.getByRole("button", { name: "Evaluate" }).click();

  await expect(page.getByText("blocked", { exact: true })).toBeVisible();
  await expect(page.getByText("No Harm")).toBeVisible();
  await expect(page.getByText("Radical Honesty")).toBeVisible();
  await expect(page.getByText("harm.explicit_or_unsafe_concealment")).toBeVisible();
});
