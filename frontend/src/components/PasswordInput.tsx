import styles from "./PasswordInput.module.css";

interface PasswordInputProps {
  id?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

export function PasswordInput({
  id = "password",
  value,
  onChange,
  error,
  disabled = false,
}: PasswordInputProps) {
  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>
        Password
      </label>
      <input
        id={id}
        className={`${styles.input} ${error ? styles.inputError : ""}`}
        type="password"
        name="password"
        autoComplete="new-password"
        placeholder="Create a strong password"
        value={value}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : `${id}-hint`}
        onChange={(event) => onChange(event.target.value)}
      />
      <span id={`${id}-hint`} className={styles.hint}>
        Use 8+ characters with uppercase, lowercase, and a number.
      </span>
      {error ? (
        <span id={`${id}-error`} className={styles.fieldError} role="alert">
          {error}
        </span>
      ) : null}
    </div>
  );
}
