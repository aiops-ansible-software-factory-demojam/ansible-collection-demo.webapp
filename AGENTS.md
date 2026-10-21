# Web application collection development

This collection contains the nginx/SELinux demonstration. The Python vulnerability application lives in `ansible-collection-demo.pythonapp` (`demo.pythonapp`) on a separate RHEL host.

Use fully qualified Ansible module names and keep roles idempotent. Defaults belong in `roles/<role>/defaults/main.yml` with the role prefix. Keep credentials outside the repository.

Run `make molecule` from the collection root in the existing Omnigent sandbox. Source `/etc/profile.d/molecule.sh`; use its backend, pinned provisioner, network and scoped credentials. AWS tests must finish creation, convergence, idempotence, verification and destruction on both RHEL 9 and RHEL 10. After interruption, run `make destroy` in the same sandbox to recover the saved ownership record. Do not replace the sandbox's normal collection paths or credentials.

Shared Molecule settings live in `extensions/molecule/config.yml` and `extensions/molecule/utils/`; the pinned requirements are `extensions/molecule/requirements-test.yml`. Scenarios contain only molecule.yml, converge.yml and verify.yml. Verify HTTP and the actual nginx worker identity, with SELinux enforcing. Preserve the fault until the issue requests remediation; never change production yourself.

Push an issue feature branch and open a PR against main. Do not merge or push directly to main.
