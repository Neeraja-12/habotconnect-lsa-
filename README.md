# HabotConnect API

A standalone Django + Django REST Framework backend for HabotConnect, a remote platform that connects parents of children with learning difficulties to Learning Support Assistants (LSAs).

## Stack

- **Python 3.13**
- **Django 6.1**
- **Django REST Framework 3.18**
- **SQLite** (configured for easy local development; swap to PostgreSQL in production)

## Features

- **Users & Profiles**: Custom user model with roles (`parent`, `lsa`, `admin`), shared profiles, and LSA-specific profiles.
- **Matching**: Search/filter LSAs by specialization, hourly rate, verification status, and rating.
- **Bookings**: Parents request sessions; LSAs confirm, decline, cancel, or complete them.
- **Availability**: LSAs post recurring or one-off open slots; parents browse open slots.
- **Reviews**: Parents review completed bookings; LSA average rating is recomputed automatically.

## Project structure

```text
habotconnect-api/
├── api/
│   ├── models.py       # Domain models and indexes
│   ├── serializers.py  # DRF serializers
│   ├── views.py        # ViewSets with optimized queries
│   ├── urls.py         # Router wiring
│   ├── admin.py        # Django admin configuration
│   └── tests.py        # API tests
├── habotconnect/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── requirements.txt
└── README.md
```

## Quick start

```bash
cd habotconnect-api
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/v1/`.

## Running tests

```bash
python manage.py test
```

## Key endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/users/` | Register a new parent or LSA |
| `GET /api/v1/lsa-profiles/` | Search available LSAs |
| `GET /api/v1/availability/` | Browse open LSA slots |
| `POST /api/v1/bookings/` | Parent requests a booking |
| `PATCH /api/v1/bookings/<id>/update_status/` | LSA confirms/declines/cancels |
| `PATCH /api/v1/bookings/<id>/complete/` | Parent marks booking completed |
| `POST /api/v1/reviews/` | Parent reviews a completed booking |

## Query optimization

List endpoints use `select_related` and `prefetch_related` to avoid N+1 queries:

- `LSAProfileViewSet` prefetches `specializations` and selects the related `user`.
- `BookingViewSet` selects `parent`, `lsa`, and `child`, and prefetches `review`.
- `ReviewViewSet` selects the related `booking` parent and LSA.

Database indexes are declared on the most common filter/sort fields (`status`, `starts_at`, `hourly_rate`, `average_rating`, etc.).

## Notes

- `AUTH_USER_MODEL` is set to `api.User`. Do not change this after running migrations.
- The default permission class is `IsAuthenticatedOrReadOnly`, so public read access is allowed for reference/list endpoints; writes require authentication.
- For production, switch `SECRET_KEY`, set `DEBUG=False`, configure PostgreSQL, and add token/JWT authentication.
