import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { RegistrationForm } from "../components/RegistrationForm";
import { DUPLICATE_EMAIL_MESSAGE } from "../utils/validation";

describe("RegistrationForm", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(globalThis, "fetch");
  });

  it("validates email and password before submitting", async () => {
    const user = userEvent.setup();
    render(<RegistrationForm />);

    await user.click(screen.getByRole("button", { name: "Register" }));

    expect(await screen.findByText("Email is required.")).toBeInTheDocument();
    expect(
      screen.getByText("Password is required."),
    ).toBeInTheDocument();
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("creates an account on successful registration", async () => {
    const user = userEvent.setup();
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        message:
          "Registration successful. Please check your email to confirm your account.",
        email: "newuser@example.com",
      }),
    } as Response);

    render(<RegistrationForm />);

    await user.type(screen.getByLabelText("Email"), "newuser@example.com");
    await user.type(screen.getByLabelText("Password"), "StrongPass1");
    await user.click(screen.getByRole("button", { name: "Register" }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "newuser@example.com",
          password: "StrongPass1",
        }),
      });
    });

    expect(
      await screen.findByText(
        "Registration successful. Please check your email to confirm your account.",
      ),
    ).toBeInTheDocument();
  });

  it("shows duplicate email error message from the API", async () => {
    const user = userEvent.setup();
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: DUPLICATE_EMAIL_MESSAGE }),
    } as Response);

    render(<RegistrationForm />);

    await user.type(screen.getByLabelText("Email"), "testuser@example.com");
    await user.type(screen.getByLabelText("Password"), "StrongPass1");
    await user.click(screen.getByRole("button", { name: "Register" }));

    expect(
      await screen.findByRole("alert"),
    ).toHaveTextContent(DUPLICATE_EMAIL_MESSAGE);
  });
});
