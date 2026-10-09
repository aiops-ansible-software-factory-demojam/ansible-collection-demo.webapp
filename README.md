# demo.webapp

Demo web application collection with an nginx role and KubeVirt Molecule tests.

This demo collection follows the Ansible collection golden-path layout. Its
nginx role and Molecule scenarios use disposable CentOS Stream 10
KubeVirt VMs. The Forgejo repository remains `ansible-collection-demo.webapp`; the
Ansible collection name is `demo.webapp`.

## Get started

Run these commands from the collection root in a demo Omnigent agent sandbox:

```sh
ansible-lint
ansible-galaxy collection build --output-path /tmp
make molecule
```

The nginx scenario installs nginx on CentOS Stream 10, then verifies HTTP,
worker identity, SSH connectivity, and the guest operating system.
`roles/example` remains a starter role; add a scenario to converge your role
and verify its intended behavior.

The sandbox supplies Ansible Development Tools, the Kubernetes Python client,
SSH, `KUBECONFIG`, `MOLECULE_GLOB`, and preloaded collection dependencies. If test
requirements change, install them with `ansible-galaxy collection install -r
extensions/molecule/requirements-test.yml` before testing. Production collection
dependencies still belong in `galaxy.yml`. Run from the collection root so the
shared `extensions/molecule/config.yml` is discovered. `make molecule` runs all
scenarios, currently nginx; adding a scenario requires no Makefile change.
`make test` remains an alias.

The shared `utils/inventory/hosts.yml` enables `centos-stream10`, which clones
its CDI DataSource in `openshift-virtualization-os-images`. The VM is created in
`molecule-tests`. The `rhel10` entry and image/version metadata remain commented
out until RHEL package repository prerequisites are configured. Each test run
provisions, converges, verifies, and destroys the CentOS host:

```sh
make molecule               # All scenarios, currently nginx
molecule test -s nginx       # Run only nginx when more scenarios are added
```

Each VM gets two vCPUs, 2 GiB RAM, a disposable 30 GiB disk, and a generated SSH key. Connections
use the VM's pod IP; no NodePort or cluster-wide node permissions are needed.
The namespace quota permits up to four test VMs and 120 GiB of requested disks.

The YAML inventory uses the fixed hostname `centos-stream10`,
which the provisioner also uses as the VM name. This demo runs one agent. After
an interrupted run, use `make destroy` from the same collection.

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
- `ansible.cfg` and `Makefile` configure collection resolution and root-level test commands.
- `devfile.yaml` defines development commands for editors that support Devfiles.
