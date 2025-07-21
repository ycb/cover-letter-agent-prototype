# 🤝 Contributing Guide

Welcome! This project thrives on collaboration between developers and product-minded contributors. Whether you’re a seasoned engineer or a Engineering minded PM, these guidelines will help us work smoothly together.

---

## 📅 Communication & Planning

- **Weekly/Bi-weekly Syncs:** Schedule regular check-ins to discuss priorities, blockers, and new ideas.
- **Shared Task List:** Track features, bugs, and ideas using GitHub Issues, a shared doc, or a TODO list in the repo.
- **Role Clarity:** Define who’s leading on features, reviews, or documentation for each cycle.

---

## 🌱 Branching & Code Management

- **Feature Branches:**
  - Create a new branch for each feature or fix (e.g., `feature/pm-idea`, `bugfix/typo`).
- **Pull Requests (PRs):**
  - Open a PR for every change, no matter how small.
  - Use the PR template (see below) to describe your changes.
- **Sandbox Branch:**
  - For experiments or new features use a `sandbox/yourname` branch. Merge to main only after review.

---

## 👀 Code Review & Quality

- **Review Each Other’s Code:**
  - Request a review for every PR. Use comments to ask questions or explain decisions.
- **Automated Checks:**
  - Run `make lint`, `make test`, and `make all` before merging.
- **Pre-commit Hooks:**
  - Set up with `pre-commit install` (see Developer Guide).

---

## 📝 Documentation & Knowledge Sharing

- **Document Features:**
  - Add a short doc or comment for new features or changes.
  - Update the README or a Changelog for major updates.
- **Inline Comments:**
  - Explain "why" for non-obvious code.
- **Reference:**
  - See `docs/DEVELOPER_GUIDE.md` for technical patterns and examples.

---

## 🧪 Testing & Validation

- **Write Simple Tests:**
  - Add a test for each new feature or bugfix (see `tests/` for examples).
- **Manual Testing:**
  - For experimental features, do a quick manual test and note results in the PR.

---

## 🚦 Example Workflow

1. **Idea:** Create a GitHub Issue or add to the TODO list.
2. **Prototype:** Code in a feature or sandbox branch.
3. **Pull Request:** Open a PR, fill out the template, and request review.
4. **Review:** Discuss, suggest changes, and approve.
5. **Merge:** Merge to main after checks pass.
6. **Document:** Update docs if needed.

---

## ✅ Pull Request Checklist

- [ ] Code reviewed by at least one collaborator
- [ ] All tests pass (`make test`)
- [ ] Linting and type checks pass (`make lint`, `make typecheck`)
- [ ] Documentation/comments updated
- [ ] PR template filled out

---

## 📝 Pull Request Template

```
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

---

## 💡 Tips for PMs Who Code ;) 
- Don’t hesitate to ask questions in PRs or Issues.
- If you’re unsure about Python or Git, ask for a pairing session.
- Your super powers would be awesome to bring the following: Focus on user stories or acceptance criteria for new features. This helps clarify what “done” looks like and guides both coding and testing.
- Use comments to explain the intent behind your code.

---

## 📚 Resources
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [User Guide](docs/USER_GUIDE.md)
- [Testing Guide](TESTING.md)

---

Happy collaborating! 🎉 