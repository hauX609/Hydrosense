# Contributing to Hydrosense

Thank you for your interest in contributing. This document describes how to contribute code, docs, and bug reports.

## Ground Rules

- Be respectful and constructive in discussions.
- Keep pull requests focused and small where possible.
- Write clear commit messages.
- Add or update documentation when behavior changes.

## Development Setup

1. Clone the repository.
2. Create a branch from `main`.
3. Set up backend:
   - `cd backend`
   - `pip install -r requirements.txt`
4. Set up frontend:
   - `cd frontend`
   - `npm install`

## Running Locally

- Backend: `uvicorn app.main:app --reload` from `backend`
- Frontend: `npm run dev` from `frontend`

## Pull Request Checklist

- The branch is rebased on top of the latest `main`.
- Changes are tested locally.
- Documentation and examples are updated when needed.
- The PR description clearly explains what changed and why.
- Related issue is linked when applicable.

## Reporting Bugs and Requesting Features

- Use the GitHub issue templates.
- Include reproduction steps, expected behavior, and actual behavior.
- For feature requests, explain the use case and possible alternatives.
