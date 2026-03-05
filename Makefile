.PHONY: adr

# Create a new ADR (Architecture Decision Record)
# Usage: make adr title="ADR title"
adr:
	@bash scripts/adr-new.sh $(title)
