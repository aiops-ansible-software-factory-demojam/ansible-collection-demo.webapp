# Changelog

## 1.0.0

- Bump collection version to 1.0.0 for Galaxy metadata compliance.
- Align task naming with strict ansible-lint `name[prefix]` checks.

## 0.1.0

- Rename the demo collection to `demo.webapp` and adopt the collection golden-path layout.
- Keep the nginx role with demo settings in `vars/webapp.yml` and `playbooks/deploy_webapp.yml`.
- Add shared Molecule lifecycle under `extensions/molecule/` with AWS RHEL 9/10 and KubeVirt CentOS Stream 10 scenarios.
- Ship `collections/requirements.yml` for the pinned Molecule provisioner used in lint and tests.
