# demo.webapp

Demo web application collection with an nginx role and AWS or CNV Molecule tests.

This demo collection follows the Ansible collection golden-path layout. Its
nginx role and Molecule scenarios use disposable Linux guests. CNV selects
CentOS Stream 10; AWS selects pinned RHEL 9 and RHEL 10 images. The Forgejo repository remains `ansible-collection-demo.webapp`; the
Ansible collection name is `demo.webapp`.

## Get started

Run these commands from the collection root in a demo Omnigent agent sandbox:

```sh
ansible-lint
ansible-galaxy collection build --output-path /tmp
make molecule
```

The nginx scenario installs nginx on each selected guest, then verifies HTTP,
the package worker account, Enforcing SELinux, SSH and the operating system.
`roles/example` remains a starter role; add a scenario to converge your role
and verify its intended behavior.

The sandbox supplies Ansible Development Tools, SSH, the selected test
identity, `MOLECULE_GLOB`, and preloaded dependencies. CNV also supplies a
scoped `KUBECONFIG`; AWS supplies its credential-file path, network and image
settings. Run from the collection root so the shared `config.yml` is discovered.
`make molecule` runs every scenario; `make test` is an alias. Production
collection dependencies still belong in `galaxy.yml`.

Common inventory loads from `utils/inventory/base/`, followed by the selected
`kubevirt/` or `aws/` host layer and the generated connection inventory.
CNV clones the CentOS Stream 10 DataSource into `molecule-tests`, with two vCPUs,
2 GiB RAM, a disposable 30 GiB disk and PodIP SSH. Its namespace quota permits
four VMs and 120 GiB of requested disks. AWS uses the sandbox's pinned RHEL 9
and RHEL 10 images in a provided public subnet, with `t3.medium` instances,
encrypted 30 GiB gp3 disks and public-IP SSH as `ec2-user`.

Test requirements pin the published `david_igou.molecule_provisioners:0.0.7-alpha`
release. The sandbox preloads its verified Galaxy artifact. Shared inventory
maps the mounted profile to the release's `mp_defaults.aws` fields, including
the expected account and bootstrap-owned security group. Tests retain that group
and network, and destroy their own guests, disks and generated SSH keys.

```sh
make molecule               # All nginx scenarios; invoice is opt-in
molecule test -s nginx       # Run only nginx when more scenarios are added
```

The shared provisioner assigns run identities and retains cleanup state in
Molecule's ephemeral directory. After an interrupted run, use `make destroy`
from the same sandbox and collection. These tests need the selected backend's
credentials and reachable guest networking; a standalone workspace must supply
those inputs. Verification checks every connected guest against its expected
OS and major version. This demo runs one coding agent.

To add another OS image, add a host to
the selected `extensions/molecule/utils/inventory/<backend>/hosts.yml`, with
a distinct inventory name and expected OS/major version. CNV hosts specify
`mp.kubevirt.boot_source`; AWS hosts specify an exact `mp.aws.image_id`. Common
settings stay in `utils/inventory/base/group_vars/molecule.yml`.
For CNV, grant `get` for the new DataSource in the GitOps `molecule-image-cloner` Role
before using it. The disk must be at least as large as the source image, and the
guest must support cloud-init SSH key injection. Each CNV VM gets one boot DataVolume.

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
# Invoice processing scenario

`roles/invoice_portal` contains the PDF application and common authenticated
release tasks. `playbooks/invoice.yml` installs the known vulnerable baseline.
`playbooks/invoice-remediate.yml` is an explicit authoring stub: the demo agent
implements the operational Lightwell workflow and its recovery tests there.
The `invoice_portal` Molecule scenario executes that authored playbook against
disposable RHEL EC2 guests. See the GitOps repository's
[complete walkthrough](https://github.com/aiops-ansible-software-factory-demojam/openshift-gitops/blob/feature/lightwell-invoice-demo/docs/invoice-lightwell-demo.md).

Select the invoice lifecycle explicitly, with the mounted artifact material
and public signing key available in the sandbox:

```bash
make molecule MOLECULE_SCENARIO=invoice_portal
make destroy MOLECULE_SCENARIO=invoice_portal  # Recovery after interruption
```

The application unit checks use actual stock PyPDF2 3.0.1:

```bash
python -m unittest discover -s tests -p test_invoice_portal.py -v
```

They reproduce the vulnerable behavior and fail remediation verification on
the unpatched release. Full remediation acceptance requires the real signed
Lightwell wheel and EC2 Molecule lifecycle checks.

With Ansible installed, run
`python -m unittest discover -s tests -p test_invoice_source_revision.py -v`
to exercise the source guard in an AAP-like execution copy without `.git` and
in a direct Git checkout. Missing or mismatched revisions must fail.
