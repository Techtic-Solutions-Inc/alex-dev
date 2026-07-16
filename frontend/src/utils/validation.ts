export interface RegisterFormData {
  email: string;
  password: string;
}

export interface RegisterFormErrors {
  email?: string;
  password?: string;
  form?: string;
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(email: string): string | undefined {
  const trimmed = email.trim();
  if (!trimmed) {
    return "Email is required.";
  }
  if (!EMAIL_PATTERN.test(trimmed)) {
    return "Please enter a valid email address.";
  }
  return undefined;
}

export function validatePassword(password: string): string | undefined {
  if (!password) {
    return "Password is required.";
  }
  if (password.length < 8) {
    return "Password must be at least 8 characters.";
  }
  if (!/[A-Z]/.test(password)) {
    return "Password must contain at least one uppercase letter.";
  }
  if (!/[a-z]/.test(password)) {
    return "Password must contain at least one lowercase letter.";
  }
  if (!/\d/.test(password)) {
    return "Password must contain at least one digit.";
  }
  return undefined;
}

export function validateRegistrationForm(
  data: RegisterFormData,
): RegisterFormErrors {
  const errors: RegisterFormErrors = {};
  const emailError = validateEmail(data.email);
  const passwordError = validatePassword(data.password);

  if (emailError) {
    errors.email = emailError;
  }
  if (passwordError) {
    errors.password = passwordError;
  }

  return errors;
}

export const DUPLICATE_EMAIL_MESSAGE =
  "Email already in use. Please use a different email address.";
