# demo.webapp.example

Starter role that prints `example_message` at verbosity 1 or above. It makes no
managed-host changes and supports check mode. The default message is
`Hello from the example role`. Requires ansible-core 2.16 or later.

```yaml
- name: Show the starter message
  hosts: all
  gather_facts: false
  roles:
    - role: demo.webapp.example
```

License: MIT.
