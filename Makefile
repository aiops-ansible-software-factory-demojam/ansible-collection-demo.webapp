export MOLECULE_GLOB := extensions/molecule/*/molecule.yml

.PHONY: molecule test converge destroy
molecule:
	molecule test --all

test: molecule

converge:
	molecule converge --all

destroy:
	molecule destroy --all
