import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PagePlaceholder } from "./PagePlaceholder";

describe("PagePlaceholder", () => {
  it("renders title and description", () => {
    render(<PagePlaceholder title="Example Title" description="Example Description" />);

    expect(screen.getByRole("heading", { name: "Example Title" })).toBeInTheDocument();
    expect(screen.getByText("Example Description")).toBeInTheDocument();
  });
});
