"""Authentication and simple RBAC for Streamlit pages."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from hmac import compare_digest
from pathlib import Path

import streamlit as st

import config as cfg

ROLE_LEVELS = {"viewer": 1, "analyst": 2, "admin": 3}


@dataclass(frozen=True)
class AppUser:
    username: str
    password: str
    role: str


def _is_weak_password(password: str) -> bool:
    lowered = password.lower()
    weak_tokens = ["changeme", "change_me", "password", "12345", "admin", "qwerty"]
    return len(password) < 10 or any(token in lowered for token in weak_tokens)


def _validate_auth_config(users: list[AppUser]) -> None:
    if not cfg.is_production():
        return
    weak = [user.username for user in users if _is_weak_password(user.password)]
    if weak:
        user_list = ", ".join(sorted(weak))
        raise RuntimeError(
            "Weak auth credentials are not allowed in production. "
            f"Rotate passwords for: {user_list}."
        )


def _to_users(raw_users: list[dict[str, str]]) -> list[AppUser]:
    users: list[AppUser] = []
    for user in raw_users:
        username = str(user.get("username", "")).strip()
        password = str(user.get("password", "")).strip()
        role = str(user.get("role", "viewer")).strip().lower()
        if not username or not password:
            continue
        if role not in ROLE_LEVELS:
            role = "viewer"
        users.append(AppUser(username=username, password=password, role=role))
    return users


def _load_users() -> list[AppUser]:
    # 1) Streamlit secrets (preferred for hosted deployments)
    secret_users = st.secrets.get("auth_users", []) if hasattr(st, "secrets") else []
    if isinstance(secret_users, list):
        users = _to_users(secret_users)
        if users:
            return users

    # 2) Mounted secrets file (JSON array)
    users_file = os.getenv("SUST_AUTH_USERS_FILE", "").strip()
    if users_file:
        path = Path(users_file)
        if path.exists():
            try:
                parsed = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(parsed, list):
                    users = _to_users(parsed)
                    if users:
                        return users
            except json.JSONDecodeError:
                pass

    # 3) JSON env variable for multi-user local deployments
    raw_env_users = os.getenv("SUST_AUTH_USERS_JSON", "").strip()
    if raw_env_users:
        try:
            parsed = json.loads(raw_env_users)
            if isinstance(parsed, list):
                users = _to_users(parsed)
                if users:
                    return users
        except json.JSONDecodeError:
            pass

    # 4) Single-user fallback
    username = os.getenv("SUST_APP_USERNAME", "").strip()
    password = os.getenv("SUST_APP_PASSWORD", "").strip()
    role = os.getenv("SUST_APP_ROLE", "admin").strip().lower()
    if username and password:
        if role not in ROLE_LEVELS:
            role = "admin"
        return [AppUser(username=username, password=password, role=role)]

    return []


def _session_expired() -> bool:
    if not cfg.AUTH_ENABLED:
        return False
    login_ts = st.session_state.get("auth_login_ts")
    if login_ts is None:
        return True
    elapsed_minutes = (time.time() - float(login_ts)) / 60.0
    return elapsed_minutes > cfg.SESSION_TIMEOUT_MINUTES


def _clear_session() -> None:
    for key in ["auth_user", "auth_role", "auth_login_ts", "auth_ok"]:
        if key in st.session_state:
            del st.session_state[key]


def _render_login(users: list[AppUser]) -> None:
    st.title("🔐 Secure Access")
    st.caption("Sign in to continue.")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        for user in users:
            if compare_digest(username.strip(), user.username) and compare_digest(password, user.password):
                st.session_state["auth_user"] = user.username
                st.session_state["auth_role"] = user.role
                st.session_state["auth_login_ts"] = time.time()
                st.session_state["auth_ok"] = True
                st.rerun()
        st.error("Invalid credentials.")


def require_login() -> None:
    """Enforce authenticated access if enabled."""
    if not cfg.AUTH_ENABLED:
        st.session_state.setdefault("auth_user", "local-dev")
        st.session_state.setdefault("auth_role", "admin")
        return

    users = _load_users()
    if not users:
        st.error(
            "Authentication is enabled but no users are configured. "
            "Set Streamlit secrets.auth_users or SUST_APP_USERNAME/SUST_APP_PASSWORD."
        )
        st.stop()

    try:
        _validate_auth_config(users)
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    if _session_expired():
        _clear_session()

    is_authenticated = bool(st.session_state.get("auth_ok"))
    if not is_authenticated:
        _render_login(users)
        st.stop()

    with st.sidebar:
        st.markdown("---")
        st.caption(f"Signed in as: {st.session_state.get('auth_user')} ({st.session_state.get('auth_role')})")
        if st.button("Sign Out", use_container_width=True):
            _clear_session()
            st.rerun()


def require_role(minimum_role: str) -> None:
    """Enforce minimum RBAC role for a page."""
    if minimum_role not in ROLE_LEVELS:
        raise ValueError(f"Unknown role: {minimum_role}")
    if not cfg.AUTH_ENABLED:
        return
    current_role = str(st.session_state.get("auth_role", "viewer")).lower()
    if ROLE_LEVELS.get(current_role, 0) < ROLE_LEVELS[minimum_role]:
        st.error(f"Access denied. This page requires '{minimum_role}' role or higher.")
        st.stop()
