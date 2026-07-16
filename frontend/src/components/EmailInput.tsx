import styles from "./EmailInput.module.css";

interface EmailInputProps {
  id?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

export function EmailInput({
  id = "email",
  value,
  onChange,
  error,
  disabled = false,
}: EmailInputProps) {
  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>
        Email
      </label>
      <input
        id={id}
        className={`${styles.input} ${error ? styles.inputError : ""}`}
        type="email"
        name="email"
        autoComplete="email"
        placeholder="you@example.com"
        value={value}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : undefined}
        onChange={(event) => onChange(event.target.value)}
      />
      {error ? (
        <span id={`${id}-error`} className={styles.fieldError} role="alert">
          {error}
        </span>
      ) : null}
    </div>
  );
}
