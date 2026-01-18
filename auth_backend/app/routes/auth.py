from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..auth import create_access_token, get_bearer_token, hash_password, verify_password
from ..db import get_db_session
from ..models import User
from ..schemas import (
    AuthResponseSchema,
    LoginRequestSchema,
    MessageSchema,
    ProfileSchema,
    ProfileUpdateRequestSchema,
    RegisterRequestSchema,
)

blp = Blueprint(
    "Auth",
    "auth",
    url_prefix="/",
    description="Authentication and profile management",
)


def _jwt_expiry_minutes() -> int:
    from ..auth import _get_jwt_expiry_minutes  # local import to keep helper private

    return _get_jwt_expiry_minutes()


def _get_current_user(db):
    """Return current authenticated User based on Authorization header."""
    token = get_bearer_token(request.headers.get("Authorization"))
    if not token:
        abort(401, message="Missing Authorization: Bearer <token> header")
    try:
        from ..auth import decode_access_token

        payload = decode_access_token(token)
    except Exception:
        abort(401, message="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        abort(401, message="Invalid token payload")

    user = db.get(User, int(user_id))
    if not user:
        abort(401, message="User not found for token")
    return user


@blp.route("/register")
class Register(MethodView):
    """Register a new user account."""

    @blp.arguments(RegisterRequestSchema)
    @blp.response(201, ProfileSchema)
    def post(self, payload):
        """Create a new user.

        Returns the created user's profile. Password is never returned.
        """
        email = payload["email"].lower().strip()
        password = payload["password"]

        display_name = payload.get("display_name")
        bio = payload.get("bio")

        db = next(get_db_session())
        try:
            user = User(
                email=email,
                password_hash=hash_password(password),
                display_name=display_name,
                bio=bio,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user, 201
        except IntegrityError:
            db.rollback()
            abort(409, message="Email already registered")
        finally:
            db.close()


@blp.route("/login")
class Login(MethodView):
    """Login and obtain a JWT access token."""

    @blp.arguments(LoginRequestSchema)
    @blp.response(200, AuthResponseSchema)
    def post(self, payload):
        """Authenticate credentials and return an access token."""
        email = payload["email"].lower().strip()
        password = payload["password"]

        db = next(get_db_session())
        try:
            user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if not user or not verify_password(password, user.password_hash):
                abort(401, message="Invalid email or password")

            token = create_access_token(user.id)
            return {
                "access_token": token,
                "token_type": "Bearer",
                "expires_in_minutes": _jwt_expiry_minutes(),
            }
        finally:
            db.close()


@blp.route("/logout")
class Logout(MethodView):
    """Logout endpoint (stateless JWT).

    Since JWT is stateless, this endpoint is a no-op for the server; the client should discard the token.
    """

    @blp.response(200, MessageSchema)
    def post(self):
        """Acknowledge logout."""
        return {"message": "Logged out (client should delete token)."}, 200


@blp.route("/profile")
class Profile(MethodView):
    """Get/update the authenticated user's profile."""

    @blp.response(200, ProfileSchema)
    def get(self):
        """Return the current user's profile."""
        db = next(get_db_session())
        try:
            user = _get_current_user(db)
            return user, 200
        finally:
            db.close()

    @blp.arguments(ProfileUpdateRequestSchema)
    @blp.response(200, ProfileSchema)
    def put(self, payload):
        """Update the current user's profile fields (display_name, bio)."""
        db = next(get_db_session())
        try:
            user = _get_current_user(db)
            if "display_name" in payload:
                user.display_name = payload["display_name"]
            if "bio" in payload:
                user.bio = payload["bio"]

            db.add(user)
            db.commit()
            db.refresh(user)
            return user, 200
        finally:
            db.close()


@blp.route("/protected")
class ProtectedExample(MethodView):
    """Example protected route requiring a valid JWT."""

    @blp.response(200, MessageSchema)
    def get(self):
        """Return a message only if authenticated."""
        db = next(get_db_session())
        try:
            user = _get_current_user(db)
            return {"message": f"Hello, {user.email}. You have access to protected data."}, 200
        finally:
            db.close()
