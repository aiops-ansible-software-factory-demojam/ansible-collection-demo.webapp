# demo.webapp

Ansible collection for the nginx web application and SELinux outage demonstration on RHEL. The Python invoice application is maintained separately in [demo.pythonapp](https://github.com/aiops-ansible-software-factory-demojam/ansible-collection-demo.pythonapp).

The web application runs on the RHEL host in inventory group `webapps`. Its demo baseline uses nginx with permissive SELinux. The explicit `webapp_selinux_enable` job introduces the outage; the agent changes this collection and tests the fix before human review and deployment. Python deployment and security checks target a different host and never change this host's SELinux mode.

From the existing Omnigent sandbox:

```sh
ansible-lint roles/nginx extensions/molecule/nginx
ansible-galaxy collection build --output-path /tmp
make molecule
make destroy  # Recover after interruption
```

Source `/etc/profile.d/molecule.sh` and retain its backend, network, credentials and preloaded dependencies. AWS scenarios use the pinned RHEL 9 and RHEL 10 images; both must finish the full lifecycle, including idempotence, HTTP/worker-identity checks, enforcing SELinux and cleanup. CNV uses the existing CentOS Stream 10 DataSource. Shared lifecycle configuration is under `extensions/molecule/`; the published provisioner is pinned in `requirements-test.yml`.

The management plane and separate application-host provisioning live in [openshift-gitops](https://github.com/aiops-ansible-software-factory-demojam/openshift-gitops) and [demojam-ansible](https://github.com/aiops-ansible-software-factory-demojam/demojam-ansible).

Application details are in `vars/webapp.yml`, loaded by
`playbooks/deploy_webapp.yml`. The shared nginx role manages only the service
configuration and accepts generic variables; its default document root is the
standard package path. The production wrapper and Molecule use the same collection
playbook. Configuration is validated before replacement and reloads only on change.
Fresh-host check mode does not try to configure or start a simulated installation.

The enforcing-mode incident acceptance intentionally fails for this unremediated
baseline. Code-quality checks must not be reported as a successful SELinux fix.

The playbook uses `deploy_webapp.yml` so consumers can resolve the valid collection-qualified import `demo.webapp.deploy_webapp`.

Local input and fresh-host check-mode regressions run with `python -m unittest discover -s tests -v` in an environment with Ansible and PyYAML.
