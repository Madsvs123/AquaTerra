import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi, getApiError } from "@/api/client";
import { useAuthStore } from "@/stores/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((s) => s.setSession);
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    const data = new FormData(event.currentTarget);
    try {
      const session = await authApi.login({ email: String(data.get("email")), password: String(data.get("password")) });
      setSession(session.access, session.refresh, session.user, session.memberships);
      navigate("/register");
    } catch (err) {
      setError(getApiError(err));
    }
  }

  return (
    <div className="auth">
      <section className="auth-story">
        <p className="eyebrow" style={{ color: "#b7e4d4" }}>Smart irrigation operations</p>
        <h1>Keep every zone at the moisture it was planted for.</h1>
        <p style={{ maxWidth: 460, marginTop: 18, color: "#dff3ea" }}>
          AquaTerra brings sensors, valves, weather, and crew decisions onto one board for farms, greenhouses, and irrigation operators.
        </p>
      </section>
      <section className="auth-panel">
        <h2>Sign in</h2>
        <p className="muted" style={{ margin: "8px 0 18px" }}>Use the operations account issued to your organization.</p>
        <form className="form" onSubmit={onSubmit}>
          {error && <div className="error">{error}</div>}
          <label>Email<input className="field" name="email" type="email" required /></label>
          <label>Password<input className="field" name="password" type="password" required /></label>
          <button className="btn-primary" type="submit">Enter operations</button>
        </form
        <p className="muted" style={{ marginTop: 16 }}>New organization? <Link to="/register">Create AquaTerra</Link></p>
      </section>
    </div>
  );
}
