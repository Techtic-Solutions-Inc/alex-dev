import styles from "./RegisterButton.module.css";

interface RegisterButtonProps {
  disabled?: boolean;
  isLoading?: boolean;
}

export function RegisterButton({
  disabled = false,
  isLoading = false,
}: RegisterButtonProps) {
  return (
    <button
      type="submit"
      className={styles.button}
      disabled={disabled || isLoading}
    >
      {isLoading ? "Creating account..." : "Register"}
    </button>
  );
}
