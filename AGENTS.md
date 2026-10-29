# Web application collection development

This collection contains the nginx/SELinux demonstration. The Python vulnerability application lives in `ansible-collection-demo.pythonapp` (`demo.pythonapp`) on a separate RHEL host.

Keep demo page content and document-root settings in `vars/webapp.yml`; use `playbooks/deploy_webapp.yml` as the application entry point. Keep the nginx role reusable and do not put application details in role defaults or inventory.

Use fully qualified Ansible module names and keep roles idempotent. Defaults belong in `roles/<role>/defaults/main.yml` with the role prefix. Keep credentials outside the repository.

Run `make molecule` from the collection root in the existing Omnigent sandbox. Source `/etc/profile.d/molecule.sh`; use its backend, pinned provisioner, network and scoped credentials. AWS tests must finish creation, convergence, idempotence, verification and destruction on both RHEL 9 and RHEL 10. After interruption, run `make destroy` in the same sandbox to recover the saved ownership record. Do not replace the sandbox's normal collection paths or credentials.

Shared Molecule settings live in `extensions/molecule/config.yml` and `extensions/molecule/utils/`; the pinned requirements are `extensions/molecule/requirements-test.yml`. Scenarios contain only molecule.yml, converge.yml and verify.yml. Verify HTTP and the actual nginx worker identity, with SELinux enforcing. Preserve the fault until the issue requests remediation; never change production yourself.

Push an issue feature branch and open a PR against main. Do not merge or push directly to main.

Every incident fix must add meaningful Molecule regression assertions for its
specific failure. Renaming an existing HTTP check or adding diagnostic output
does not add regression coverage. Keep the production playbook's fact requirements
in mind: gather required facts in the reusable role rather than only in the test
setup. Run lint, unit tests, a collection build and every Molecule scenario after
the final edit, and report each actual exit code. Do not hide a failing command
behind a pipeline's successful tail or head command.

Molecule provisioning commands (`test`, `converge`, `create`, `check`) deliberately
destroy the scenario's owned test guests before creating replacements. Preserve
these lifecycle sequences. After any code change, rerun the complete test lifecycle
on fresh RHEL 9/10 guests before reporting success; an earlier converge or a run
with skipped creation does not validate the final code. Keep the saved ownership
records so cleanup can remove partial resources; never delete state to force a
new run. Set the shell tool timeout to at least 1800000 ms (30 minutes) for a full EC2
lifecycle; do not add a shorter shell `timeout` around Molecule. A timeout or
incomplete output is not a pass. Run tests without output-filtering pipelines,
or enable `set -o pipefail` and preserve the actual Molecule exit status.

Keep generated collection installations outside the checkout. Never commit the
`collections/ansible_collections/` cache or absolute/outside-checkout symlinks. Use a separate temporary
collection installation root and preserve the sandbox's normal dependency paths.
Before committing and submitting, inspect `git diff --cached --stat` and
`git diff --cached --name-status`; stage only reviewed source and regression tests.
The PR helper rejects nonportable committed content before pushing or publishing.
Keep standard `collections/requirements.yml` dependency declarations in source.

## Ansible authoring standard

Follow [Red Hat CoP Automation Good Practices](https://redhat-cop.github.io/automation-good-practices/),
especially role design, coding style, idempotence and check mode. Repository and
operator requirements still determine application layout and acceptance boundaries.

Prefer an existing built-in or maintained collection module to `command` or
`shell`; check its interface with `ansible-doc` and declare production collection
dependencies in `galaxy.yml` when applicable. Use `ansible.builtin.uri` for HTTP
APIs. Avoid custom modules/plugins when existing modules and straightforward tasks
are sufficient; document the specific unsupported capability before adding one.
Keep application details in vars files, not role defaults or inventory.

If a command is necessary, comment why no suitable module covers it, prefer
`ansible.builtin.command` with `argv`, and provide accurate change detection,
check-mode behavior and failure handling. Use shell only when shell features are
required. Never suppress configuration/test errors with `|| true` or unconditional
`failed_when: false`, and never hide mutations with blanket `changed_when: false`.
Read-only diagnostic commands can legitimately report no change; classify expected
nonzero results explicitly and retain unexpected failures.

Keep meaningful regression assertions and the complete Molecule lifecycle,
including idempotence and verification. Run `ansible-lint --profile production`
from the collection root (installs deps from `collections/requirements.yml` first)
or lint scoped paths after dependencies are present; preserve actual nonzero exit codes. Do not weaken tests or discard test
state to claim success. Report failed or unavailable checks honestly.

For nginx SELinux remediation, prefer `community.general.sefcontext` to manage
persistent file-context policy, with a declared production dependency. Applying
labels with `restorecon` may require a command; preserve its errors and report
actual relabel changes. Keep fact/binding setup in reusable production tasks.
