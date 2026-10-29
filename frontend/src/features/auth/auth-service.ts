import axios from "axios";

export type SignInCredentials = {
  email: string;
  password: string;
};

export type SignInResult = {
  displayName?: string;
};

export type AuthErrorKind = "unavailable" | "rejected" | "unexpected";

export class AuthServiceError extends Error {
  readonly kind: AuthErrorKind;

  constructor(message: string, kind: AuthErrorKind) {
    super(message);
    this.name = "AuthServiceError";
    this.kind = kind;
  }
}

// Point VITE_AUTH_API_URL at the backend sign-in endpoint once it exists.
// Without it the UI reports that authentication is unavailable instead of faking a session.
const AUTH_ENDPOINT = import.meta.env.VITE_AUTH_API_URL?.trim();

export const isAuthConfigured = Boolean(AUTH_ENDPOINT);

export async function signIn(
  credentials: SignInCredentials,
): Promise<SignInResult> {
  if (!AUTH_ENDPOINT) {
    throw new AuthServiceError(
      "HubOS authentication is not connected yet, so sign-in is unavailable.",
      "unavailable",
    );
  }

  try {
    const { data } = await axios.post<SignInResult>(
      AUTH_ENDPOINT,
      { email: credentials.email, password: credentials.password },
      {
        timeout: 15_000,
        withCredentials: true,
        headers: { "Content-Type": "application/json" },
      },
    );

    return data ?? {};
  } catch (error) {
    throw toAuthServiceError(error);
  }
}

function toAuthServiceError(error: unknown): AuthServiceError {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return new AuthServiceError(
        "We couldn't reach the sign-in service. Check your connection and try again.",
        "unavailable",
      );
    }

    const { status } = error.response;

    if (status === 401 || status === 403) {
      return new AuthServiceError(
        "The email or password you entered doesn't match our records.",
        "rejected",
      );
    }

    if (status === 429) {
      return new AuthServiceError(
        "Too many sign-in attempts. Please wait a moment and try again.",
        "rejected",
      );
    }
  }

  return new AuthServiceError(
    "Something went wrong while signing in. Please try again.",
    "unexpected",
  );
}
