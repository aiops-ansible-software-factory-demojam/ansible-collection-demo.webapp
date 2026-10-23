# demo.webapp.nginx

Installs the Enterprise Linux nginx package, owns `/etc/nginx/nginx.conf`, and
starts the service using the package's nginx worker account. Configuration is
rendered from a template, checked with `nginx -t` before replacement, and reloaded
through a handler only when it changes. This role does not manage SELinux mode
or add labels, firewall rules, or TLS certificates.

Requires Enterprise Linux 9/10, ansible-core >=2.16, package repository access,
a service manager, and root privileges. The template replaces the main nginx
configuration; existing files under `/etc/nginx/conf.d/` remain included and must
be compatible with the managed server.

| Variable | Default | Purpose |
| --- | --- | --- |
| `nginx_service_enabled` | `true` | Enable at boot; the service is always started. |
| `nginx_docroot` | `/usr/share/nginx/html` | Absolute document root without traversal components. |
| `nginx_index_content` | `''` | Optional index page; empty leaves existing content alone. |
| `nginx_listen_port` | `80` | HTTP port, from 1 through 65535. |

```yaml
---
- name: Install nginx
  hosts: webservers
  become: true
  roles:
    - role: demo.webapp.nginx
```

Keep application settings in a vars file. The demo's page and `/web` path live
in `vars/webapp.yml`, loaded by `playbooks/deploy_webapp.yml`; they are not generic
role defaults or inventory settings. The baseline deliberately leaves `/web`
without a persistent SELinux policy so the incident can demonstrate remediation.

Repeated convergence is idempotent. On a fresh host, check mode predicts package
installation and skips configuration and service operations that need that package.
On an existing installation it predicts configuration changes without activating
them. Rollback/uninstall is outside this role's scope. License: MIT.
