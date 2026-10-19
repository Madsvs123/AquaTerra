import { FormEvent, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { authApi, getApiError } from "@/api/client";
import { useAuthStore } from "@/stores/authStore";

export default function InvitePage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const setSession = useAuthStore((s) => s.setSession);
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    try {
      const session = await authApi.accept({
        token: token?.slice(1) || "",
        full_name: String(data.get("full_name")),
        password: String(data.get("password")),
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
        <h1>You have been invited onto a farm workspace.</h1>
      </section>
      <section className="auth-panel">
        <h2>Accept invitation</h2>
        <form className="form" onSubmit={onSubmit}>
          {error && <div className="error">{error}</div>}
          <label>Full name<input className="field" name="full_name" required /></label>
          <label>Title<input className="field" name="title" /></label>
          <label>Password<input className="field" name="password" type="password" required /></label>
          <button className="btn-primary" type="submit">Join organization</button>
        </form>
      </section>
    </div>
  );
}
