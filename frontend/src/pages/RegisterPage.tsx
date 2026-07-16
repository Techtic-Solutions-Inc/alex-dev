import { RegistrationForm } from "../components/RegistrationForm";
import styles from "./RegisterPage.module.css";

export function RegisterPage() {
  return (
    <main className={styles.page}>
      <section className={styles.card} aria-labelledby="register-heading">
        <div className={styles.header}>
          <p className={styles.brand}>Agentwise</p>
          <h1 id="register-heading" className={styles.title}>
            Create your account
          </h1>
          <p className={styles.subtitle}>
            Register to start using the AI Assistant securely.
          </p>
        </div>

        <RegistrationForm />

        <p className={styles.footer}>
          Already have an account?{" "}
          <a className={styles.link} href="/login">
            Sign in
          </a>
        </p>
      </section>
    </main>
  );
}
