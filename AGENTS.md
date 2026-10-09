# Collection development

Use fully qualified Ansible module names and keep roles idempotent. Put
configuration defaults in `roles/<role>/defaults/main.yml` and prefix their
names with the role name. Keep secret lookups outside roles.

Run `ansible-lint`, build the collection, and run `make molecule` before opening
a pull request. Update the affected scenario's `verify.yml` to check the
feature's behavior. Never commit credentials.

Run `make molecule` from the collection root in a demo Omnigent sandbox. It
runs every scenario discovered by `MOLECULE_GLOB`; nginx is currently the only
scenario. The sandbox supplies the Kubernetes client, a scoped test kubeconfig,
and preloaded collection dependencies. Keep the exact provisioner version in
`extensions/molecule/requirements-test.yml` and shared scenario configuration
in `extensions/molecule/config.yml`. Use the provisioner collection's lifecycle
playbooks and the existing CentOS Stream 10 DataSource with PodIP
connections. `make molecule` provisions CentOS Stream 10. The RHEL 10 entry
stays commented out until its package repository prerequisites are configured.
Keep each host's boot source and expected distribution facts in
`utils/inventory/hosts.yml`; keep common settings in its group variables.
Shared lifecycle playbooks live in `utils/playbooks/`. Each scenario directory
contains only `molecule.yml`, `converge.yml`, and `verify.yml`; shared `config.yml`
provides the lifecycle and inventory paths.

Keep the sandbox's normal collection paths so preloaded dependencies remain
available. If test requirements change, install
`extensions/molecule/requirements-test.yml` before testing. Declare production
collection dependencies in `galaxy.yml`; sandbox preloads do not replace them.

Keep the declarative YAML inventory. Its fixed hostname `centos-stream10` is
also the VM name in the shared `molecule-tests` namespace.
After an interrupted test, run `make destroy` from the same collection.

For this collection, test role changes with `make molecule` and check
HTTP and actual nginx worker identity. Keep changes scoped to the issue and
update the README when public behavior changes. Push a feature branch and open
a PR against `main`, referencing the issue. Do not merge the PR or push directly
to `main`.
