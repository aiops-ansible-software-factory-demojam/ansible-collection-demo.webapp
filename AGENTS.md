# Web application collection development

This collection contains the nginx/SELinux demonstration. The Python vulnerability application lives in `ansible-collection-demo.pythonapp` (`demo.pythonapp`) on a separate RHEL host.

Keep demo page content and document-root settings in `vars/webapp.yml`; use `playbooks/deploy_webapp.yml` as the application entry point. Keep the nginx role reusable and do not put application details in role defaults or inventory.

Use fully qualified Ansible module names and keep roles idempotent. Defaults belong in `roles/<role>/defaults/main.yml` with the role prefix. Keep credentials outside the repository.

Run `make molecule` from the collection root in the existing Omnigent sandbox. Source `/etc/profile.d/molecule.sh`; use its backend, pinned provisioner, network and scoped credentials. AWS tests must finish creation, convergence, idempotence, verification and destruction on both RHEL 9 and RHEL 10. After interruption, run `make destroy` in the same sandbox to recover the saved ownership record. Do not replace the sandbox's normal collection paths or credentials.

Shared Molecule settings live in `extensions/molecule/config.yml` and `extensions/molecule/utils/`; the pinned requirements are `extensions/molecule/requirements-test.yml`. Scenarios contain only molecule.yml, converge.yml and verify.yml. Verify HTTP and the actual nginx worker identity, with SELinux enforcing. Preserve the fault until the issue requests remediation; never change production yourself.

Push an issue feature branch and open a PR against main. Do not merge or push directly to main.

Every incident fix must add or extend `extensions/molecule/nginx/tasks/regression.yml`
and include those tasks from `verify.yml`. Existing HTTP/enforcing assertions
alone do not satisfy new regression coverage. Use explicit
`ansible.builtin.assert` verdicts after non-fatal observations. The independent
operator executes the identical tasks against the incident merge base (an
assertion must fail on each guest) and the published fix (all must pass), then
checks persistent SELinux policy by relabeling and verifying enforcing HTTP
recovery. Never publish the operator's `webapp/regression-validation` status.

Production source guards use the Controller-protected full SHA in
`awx_job_scm_branch` for overridden jobs. `awx_project_revision` describes the
default project revision and may have advanced to a later merge commit.

PR submission is not completion. After the final edit, rerun lint, build and all
Molecule tests, then commit and publish the same incident branch and PR. Run
`demo-goldenpath --repository demo-owner/ansible-collection-demo.webapp ci <issue> --wait` until independent CI
passes for that exact head. Exit 75 means pending: keep waiting without editing
the published tree. On failure, read trusted CI diagnostics on the PR, fix the
cause on the same branch, rerun local checks, push a new commit and wait again.
Never publish your own CI status, weaken checks or claim completion while CI
is pending or failed. A passing verdict permits human review, not deployment.
