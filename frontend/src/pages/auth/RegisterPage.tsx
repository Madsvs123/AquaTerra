import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi, getApiError } from "@/api/client";
import { useAuthStore } from "@/stores/authStore";

export default function RegisterPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((s) => s.setSession);
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    try {
      const session = await authApi.register({
        full_name: String(data.get("full_name")),
        email: String(data.get("email")),
        password: String(data.get("pwd")),
        organization_name: String(data.get("organization_name")),
        title: String(data.get("title") || ""),
      });
      setSession(session.access, session.refresh, session.user, session.memberships);
      navigate("/");
    } catch (err) {
      setError(getApiError(err));
    }
  }

  return (
    <div className="auth">
      <section className="auth-story">
        <p className="eyebrow" style={{ color: "#b7e4d4" }}>Start an operations workspace</p>
        <h1>Stand up farms, zones, and controllers in one afternoon.</h1>
      </section>
      <section className="auth-panel">
        <h2>Create organization</h2>
        <form className="form" onSubmit={onSubmit}>
          {error && <div className="error">{error}</div>}
          <label>Your name<input className="field" name="full_name" required /></label>
          <label>Title<input className="field" name="title" placeholder="Irrigation manager" /></label>
          <label>Work email<input className="field" name="email" type="email" required /></label>
          <label>Password<input className="field" name="password" type="password" required /></label>
          <label>Organization<input className="field" name="organization_name" required /></label>
          <button className="btn-primary" type="submit">Create AquaTerra</button>
        </form>
        <p className="muted" style={{ marginTop: 16 }}>Already have access? <Link to="/login">Sign in</Link></p>
      </section>
    </div>
  );
}
