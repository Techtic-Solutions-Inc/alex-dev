import { DUPLICATE_EMAIL_MESSAGE } from "../utils/validation";

export interface RegisterResponse {
  message: string;
  email: string;
}

export interface RegisterApiError {
  detail: string | { msg: string; type: string }[];
}

export class RegisterRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RegisterRequestError";
  }
}

export async function registerUser(
  email: string,
  password: string,
): Promise<RegisterResponse> {
  const response = await fetch("/api/v1/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email.trim(), password }),
  });

  if (response.ok) {
    return response.json() as Promise<RegisterResponse>;
  }

  const errorBody = (await response.json()) as RegisterApiError;

  if (response.status === 400 && typeof errorBody.detail === "string") {
    throw new RegisterRequestError(errorBody.detail);
  }

  if (response.status === 422 && Array.isArray(errorBody.detail)) {
    const messages = errorBody.detail.map((item) => item.msg).join(" ");
    throw new RegisterRequestError(messages);
  }

  throw new RegisterRequestError(
    typeof errorBody.detail === "string"
      ? errorBody.detail
      : "Registration failed. Please try again.",
  );
}

export { DUPLICATE_EMAIL_MESSAGE };
