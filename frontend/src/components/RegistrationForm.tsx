import { FormEvent, useState } from "react";

import { registerUser } from "../api/register";
import {
  RegisterFormData,
  RegisterFormErrors,
  validateRegistrationForm,
} from "../utils/validation";
import { EmailInput } from "./EmailInput";
import { ErrorMessage } from "./ErrorMessage";
import { PasswordInput } from "./PasswordInput";
import { RegisterButton } from "./RegisterButton";
import styles from "./RegistrationForm.module.css";

interface RegistrationFormProps {
  onSuccess?: (message: string) => void;
}

const initialFormData: RegisterFormData = {
  email: "",
  password: "",
};

export function RegistrationForm({ onSuccess }: RegistrationFormProps) {
  const [formData, setFormData] = useState<RegisterFormData>(initialFormData);
  const [errors, setErrors] = useState<RegisterFormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSuccessMessage(null);

    const validationErrors = validateRegistrationForm(formData);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const response = await registerUser(formData.email, formData.password);
      setSuccessMessage(response.message);
      setFormData(initialFormData);
      onSuccess?.(response.message);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Registration failed. Please try again.";
      setErrors({ form: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <ErrorMessage message={errors.form} />

      {successMessage ? (
        <p className={styles.successMessage} role="status">
          {successMessage}
        </p>
      ) : null}

      <EmailInput
        value={formData.email}
        onChange={(email) => setFormData((current) => ({ ...current, email }))}
        error={errors.email}
        disabled={isSubmitting}
      />

      <PasswordInput
        value={formData.password}
        onChange={(password) =>
          setFormData((current) => ({ ...current, password }))
        }
        error={errors.password}
        disabled={isSubmitting}
      />

      <RegisterButton isLoading={isSubmitting} />
    </form>
  );
}
