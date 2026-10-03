# Changelog

## Unreleased

- Added pinned pre-commit checks for Ansible, YAML, whitespace, merge conflicts,
  and large files, with Make commands for setup, hooks, lint, and collection builds.

## 0.1.0

- Rename the demo collection to `demo.webapp` and adopt the collection golden-path layout.
- Keep the nginx role and add default hello-world and nginx Molecule scenarios
  using the shared CentOS Stream 10 CDI inventory, with RHEL 10 commented out.
