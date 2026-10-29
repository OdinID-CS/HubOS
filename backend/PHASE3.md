# Phase 3: Institutional identity and authorization

## Institutional profiles

Each account has a separate one-to-one `InstitutionalProfile`, created for new
users and backfilled for existing users. It stores optional institutional
email/ID, department, designation, status, timestamps, and (when verified) the
reviewing user. Authentication email and password remain on `User`.

Institutional email is trimmed and lowercased, but is not unique. Institutional
IDs are not unique. No institution-wide uniqueness scope has been established,
and identifier formats or department-specific uniqueness must be confirmed by
institutional policy before adding constraints. Email domains are not treated
as proof of identity.

Statuses and allowed transitions:

- `UNVERIFIED` -> `PENDING` when the owner requests review.
- `REJECTED` -> `PENDING` when the owner requests review again.
- `PENDING` -> `VERIFIED` or `REJECTED` through an authorized review.
- `VERIFIED` -> `PENDING` when the owner changes identity fields; the edit is
  audited and must be reviewed again.

A review request requires at least an institutional email or ID, but neither
value is independently validated against institutional records. Owners cannot
write status/reviewer fields. A verification event records every transition,
actor, time, and optional decision reason. Event/profile and actor relations
protect audit history from deletion; account deactivation is preferred over
deletion.

## Roles

`setup_hub_roles` creates or synchronizes these exact Django Group names and
permissions. It preserves group membership and replaces each listed role's
permission set with the canonical mapping below. Run it after migrations:

```powershell
python manage.py migrate
python manage.py setup_hub_roles
```

| Role | Phase 3 permissions | Intended future capability (not granted or implemented) |
|---|---|---|
| `MEMBER` | No additional Django model permissions. Authenticated owners can access only their own profile. | Participate in projects they are authorized to access. |
| `PROJECT_LEAD` | No additional permissions. | Manage proposals/projects they lead. |
| `REVIEWER` | No additional permissions. | Review proposals assigned to them. |
| `ASSET_MANAGER` | No additional permissions. | Manage hub asset inventory. |
| `HUB_ADMIN` | `view_verification_queue`, `verify_institutionalprofile`, `view_verificationhistory`. | Manage institutional identity verification only in this phase. |
| `EXECUTIVE` | No additional permissions. | Read executive-level portfolio summaries. |

Roles do not imply Django `is_staff` or `is_superuser`. Users are never
automatically promoted; assigning group membership is a separate authorized
administrative action. `has_hub_role()` checks explicit group membership and
does not infer a role from superuser status. Django superusers retain Django's
normal permission bypass, but cannot review their own identity.

## API

All routes use DRF `SessionAuthentication` and require an authenticated session.
DRF enforces CSRF on unsafe session-authenticated requests.

| Method and path | Access |
|---|---|
| `GET /api/accounts/me/profile/` | Authenticated owner; returns the caller's profile. |
| `PATCH /api/accounts/me/profile/` | Authenticated owner; only institutional email, ID, department, and designation are writable. |
| `POST /api/accounts/me/profile/verification-request/` | Authenticated owner; submits an unverified or rejected profile for manual review. |
| `GET /api/accounts/verification-queue/` | `HUB_ADMIN` verification-queue permission; returns pending profiles for review. |
| `POST /api/accounts/verification-decisions/` | `HUB_ADMIN` verification permission; JSON fields: `profile_id`, `decision` (`VERIFIED` or `REJECTED`), optional `reason`. Reviewers cannot review their own profiles. |
| `GET /api/accounts/verification-history/<profile-uuid>/` | `HUB_ADMIN` verification-history permission. |

The owner response omits login email and reviewer identity. The restricted
queue includes the identity fields needed for manual review. There is no public
profile lookup, role-assignment API, email/OTP verification, or external
directory integration. Session establishment/sign-in remains outside this
phase; the React frontend was not changed.

## Migration and validation

- Added migration `0002_institutionalprofile_verificationevent_and_more`; it
  creates the profile/history tables, backfills existing users as unverified,
  and enforces that verified status has both reviewer and timestamp. The
  existing `0001_initial` migration is unchanged.
- Applied migration `0002` to the configured PostgreSQL database after
  reviewing its operations. Before application, the account table contained
  zero users; no existing user rows needed backfilling. The migration does not
  drop or recreate the configured database.
- `python manage.py check`: passed.
- `python manage.py makemigrations --check --dry-run`: passed; no model changes
  are missing migrations.
- `python manage.py test apps.accounts.tests --verbosity 2`: 17 tests passed.
  Django created and removed the separate `test_hubos` test database; the
  configured application database was not reset.

## Decisions and limitations

Institutional policy must confirm acceptable verification evidence, email/ID
formats, identifier uniqueness scope, department naming, and who may receive
the `HUB_ADMIN` role. Requests only require one supplied institutional
identifier and are not independently validated; a human reviewer must verify
identity outside this system. Verification history records decisions and
actors, not immutable snapshots of every previous profile value. The sign-in
endpoint/session bootstrap and account-registration workflow are not part of
this phase.
