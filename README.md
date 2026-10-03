# demo.webapp

Demo web application collection with an nginx role and KubeVirt Molecule tests.

This demo collection follows the Ansible collection golden-path layout. Its
nginx role and Molecule scenarios use disposable CentOS Stream 10
KubeVirt VMs. The Forgejo repository remains `ansible-collection-demo.webapp`; the
Ansible collection name is `demo.webapp`.

## Get started

Run these commands from the collection root in a demo Omnigent agent sandbox:

```sh
make setup
make hooks
make lint
make build
molecule test
```

The default scenario prints hello world on CentOS Stream 10, then verifies SSH
connectivity and the guest operating system. `roles/example` remains a starter
role; add a scenario to converge your role and verify its intended behavior.

## Lint and pre-commit

Use Python 3.12 or newer and Make. `make setup` creates `.venv`, installs the
versions in `requirements-dev.txt`, and installs the pinned Molecule collection
dependencies. It reruns when those requirements change. No system Python
packages are modified. Setup also links this checkout into the ignored
`.ansible/source` namespace so the offline lint hook resolves `demo.webapp`
from the current source, including in a fresh sandbox. This path is scoped
to the lint hook; Molecule keeps its normal collection installation path.
Run `make hooks` once in each GitHub or Forgejo checkout
to install the Git hooks; hook installation is local and is not copied by
bootstrap's repository refresh.

`make lint` runs the same [pre-commit](https://pre-commit.com/) checks across all
tracked files: trailing whitespace, final newlines, merge conflicts, large
files, YAML syntax and duplicate keys, YAML style, and
[Ansible lint](https://docs.ansible.com/projects/lint/configuring/).
Ansible lint checks the entire collection with the `production` profile, including
Molecule playbooks. Installed hooks run automatically on each commit, and
their pinned Python environments also work without activating `.venv`.

The first setup and hook run need package download access. Subsequent lint
runs use the cached tools and installed collections and need no cluster
credentials. `.yamllint` and `.ansible-lint` define the shared rules; there are
no blanket rule skips or mocked modules. Development configuration is excluded
from the built Galaxy artifact.

When whitespace hooks fix files, review and stage those fixes, then retry the
commit. To run one check directly:

```sh
.venv/bin/pre-commit run ansible-lint --all-files
```

## Molecule tests

The sandbox supplies Ansible Development Tools, the Kubernetes Python client,
SSH, `KUBECONFIG`, and `MOLECULE_GLOB`. Molecule installs its pinned collection
dependencies automatically. Run from the collection root so the shared
`extensions/molecule/config.yml` is discovered. `make test` runs both scenarios sequentially.

The shared `utils/inventory/hosts.yml` enables `centos-stream10`, which clones
its CDI DataSource in `openshift-virtualization-os-images`. The VM is created in
`molecule-tests`. The `rhel10` entry and image/version metadata remain commented
out until RHEL package repository prerequisites are configured. Each test run
provisions, converges, verifies, and destroys the CentOS host:

```sh
molecule test                 # CentOS Stream 10
molecule test -s nginx       # Install nginx and verify HTTP and worker identity
make test                     # Both scenarios, sequentially
```

Each VM gets two vCPUs, 2 GiB RAM, a disposable 30 GiB disk, and a generated SSH key. Connections
use the VM's pod IP; no NodePort or cluster-wide node permissions are needed.
The namespace quota permits up to four test VMs and 120 GiB of requested disks.

The YAML inventory uses the fixed hostname `centos-stream10`,
which the provisioner also uses as the VM name. Collision risk is accepted
temporarily: serialize test runs across all demo sandboxes, collections, and scenarios sharing
`molecule-tests`. Overlapping runs can modify or delete each other's VM. After
an interrupted run, use `molecule destroy` from the same collection once no
other run is using the test VM. Provisioner-managed run naming is tracked in
[molecule_provisioners issue #59](https://github.com/david-igou/ansible-collection-molecule_provisioners/issues/59).

These VM tests are configured for the demo's agent sandboxes. Local devcontainers
and standalone Devfile workspaces need their own credentials and VM network
access. Preflight checks each host's golden image is ready before provisioning.
Verification checks each connected guest's distribution and major version
against that host's inventory settings.

To add another OS image, add a host to
`extensions/molecule/utils/inventory/hosts.yml` with a distinct fixed name,
its `mp.kubevirt.boot_source`, and expected distribution / major version.
Common compute and SSH settings stay in `utils/inventory/group_vars/molecule.yml`;
override them in the host's `mp.kubevirt` settings when required.
Grant `get` for the new DataSource in the GitOps `molecule-image-cloner` Role
before using it. The disk must be at least as large as the source image, and the
guest must support cloud-init SSH key injection. Each VM gets one boot DataVolume.

To add a scenario, create a directory under `extensions/molecule/` with only
`molecule.yml`, `converge.yml`, and `verify.yml`. Set `scenario.name` to the
directory name. The shared `config.yml` supplies inventory and lifecycle paths;
scenario playbooks target `hosts: molecule`. Import
`../utils/playbooks/verify.yml` to reuse host connectivity and OS checks, then
add behavioral assertions for your scenario. No lifecycle copies or role
symlinks are needed; shared `config.yml` supplies Molecule's role search path.

## Layout

- `galaxy.yml` defines the collection package.
- `roles/example/` is the starter role.
- `roles/nginx/` installs and starts the distribution nginx package.
- `extensions/molecule/nginx/` converges `demo.webapp.nginx` and verifies HTTP and worker identity.
- `extensions/molecule/config.yml` shares lifecycle configuration across scenarios.
- `extensions/molecule/requirements-test.yml` pins the provisioner release.
- `extensions/molecule/utils/inventory/` tracks boot images and expected OS versions for all scenarios.
- `extensions/molecule/utils/playbooks/` supplies create, prepare, destroy, and common host verification.
- `extensions/molecule/default/` contains only `molecule.yml`, hello-world `converge.yml`, and `verify.yml`.
- `ansible.cfg` and `Makefile` configure collection resolution and root-level test commands.
- `devfile.yaml` defines development commands for editors that support Devfiles.
- `.pre-commit-config.yaml`, `.ansible-lint`, and `.yamllint` define development checks.
- `requirements-dev.txt` pins the Python tools installed by `make setup`.
