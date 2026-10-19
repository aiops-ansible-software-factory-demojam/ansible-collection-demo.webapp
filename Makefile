export MOLECULE_GLOB := extensions/molecule/*/molecule.yml

# The invoice scenario needs separate artifact credentials and an authored
# remediation playbook. Select it explicitly to preserve the nginx demo.
MOLECULE_SCENARIO ?=
ifneq ($(strip $(MOLECULE_SCENARIO)),)
MOLECULE_SELECTION := -s $(MOLECULE_SCENARIO)
else
MOLECULE_SELECTION := --all --exclude invoice_portal
endif

.PHONY: molecule test converge destroy
molecule:
	molecule test $(MOLECULE_SELECTION)

test: molecule

converge:
	molecule converge $(MOLECULE_SELECTION)

destroy:
	molecule destroy $(MOLECULE_SELECTION)
