#!/usr/bin/env bash
set -euo pipefail

# GitHub Repository Rulesets management script
# Usage: bash scripts/manage-rulesets.sh <subcommand> [args]

RULESETS_DIR=".github/rulesets"
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
SUBCOMMAND="${1:-apply}"
shift 2>/dev/null || true

case "$SUBCOMMAND" in
  apply|sync)
    if [ ! -d "$RULESETS_DIR" ] || [ -z "$(ls -A "${RULESETS_DIR}"/*.json 2>/dev/null)" ]; then
      echo "Error: No JSON files found in ${RULESETS_DIR}/"
      exit 1
    fi
    for json_file in "${RULESETS_DIR}"/*.json; do
      RULESET_NAME=$(jq -r '.name' "$json_file")
      EXISTING_ID=$(gh api "repos/${REPO}/rulesets" --jq ".[] | select(.name == \"${RULESET_NAME}\") | .id" 2>/dev/null || echo "")
      if [ -n "$EXISTING_ID" ]; then
        gh api "repos/${REPO}/rulesets/${EXISTING_ID}" --method PUT --input "$json_file" > /dev/null
        echo "[UPDATED] ${RULESET_NAME} (ID: ${EXISTING_ID})"
      else
        NEW_ID=$(gh api "repos/${REPO}/rulesets" --method POST --input "$json_file" --jq '.id')
        echo "[CREATED] ${RULESET_NAME} (ID: ${NEW_ID})"
      fi
    done
    ;;

  list)
    RESULT=$(gh api "repos/${REPO}/rulesets" --jq '.[] | "ID: \(.id) | \(.name) | target: \(.target) | enforcement: \(.enforcement)"' 2>/dev/null || echo "")
    if [ -z "$RESULT" ]; then
      echo "No rulesets configured."
    else
      echo "$RESULT"
    fi
    ;;

  delete)
    RULESET_NAME="${1:?Error: Ruleset name required}"
    RULESET_ID=$(gh api "repos/${REPO}/rulesets" --jq ".[] | select(.name == \"${RULESET_NAME}\") | .id" 2>/dev/null || echo "")
    if [ -z "$RULESET_ID" ]; then
      echo "Error: Ruleset '${RULESET_NAME}' not found"
      exit 1
    fi
    gh api "repos/${REPO}/rulesets/${RULESET_ID}" --method DELETE
    echo "[DELETED] ${RULESET_NAME} (ID: ${RULESET_ID})"
    ;;

  delete-all)
    IDS=$(gh api "repos/${REPO}/rulesets" --jq '.[].id' 2>/dev/null || echo "")
    if [ -z "$IDS" ]; then
      echo "No rulesets to delete."
      exit 0
    fi
    for id in $IDS; do
      NAME=$(gh api "repos/${REPO}/rulesets/${id}" --jq '.name')
      gh api "repos/${REPO}/rulesets/${id}" --method DELETE
      echo "[DELETED] ${NAME} (ID: ${id})"
    done
    ;;

  diff)
    if [ ! -d "$RULESETS_DIR" ] || [ -z "$(ls -A "${RULESETS_DIR}"/*.json 2>/dev/null)" ]; then
      echo "Error: No JSON files found in ${RULESETS_DIR}/"
      exit 1
    fi
    COMPARE_FIELDS='{name, target, enforcement, conditions, rules, bypass_actors}'
    for json_file in "${RULESETS_DIR}"/*.json; do
      RULESET_NAME=$(jq -r '.name' "$json_file")
      EXISTING_ID=$(gh api "repos/${REPO}/rulesets" --jq ".[] | select(.name == \"${RULESET_NAME}\") | .id" 2>/dev/null || echo "")
      if [ -z "$EXISTING_ID" ]; then
        echo "[NEW] ${RULESET_NAME}: not on GitHub (will be created by apply)"
        continue
      fi
      REMOTE=$(gh api "repos/${REPO}/rulesets/${EXISTING_ID}" --jq "$COMPARE_FIELDS" | jq -S .)
      LOCAL=$(jq "$COMPARE_FIELDS" "$json_file" | jq -S .)
      if [ "$REMOTE" = "$LOCAL" ]; then
        echo "[OK] ${RULESET_NAME}: in sync"
      else
        echo "[DIFF] ${RULESET_NAME}:"
        diff <(echo "$LOCAL") <(echo "$REMOTE") || true
      fi
    done
    ;;

  export)
    mkdir -p "${RULESETS_DIR}"
    EXPORT_FIELDS='{name, target, enforcement, conditions, rules, bypass_actors}'
    IDS=$(gh api "repos/${REPO}/rulesets" --jq '.[].id' 2>/dev/null || echo "")
    if [ -z "$IDS" ]; then
      echo "No rulesets to export."
      exit 0
    fi
    for id in $IDS; do
      RULESET=$(gh api "repos/${REPO}/rulesets/${id}")
      NAME=$(echo "$RULESET" | jq -r '.name')
      echo "$RULESET" | jq "$EXPORT_FIELDS" > "${RULESETS_DIR}/${NAME}.json"
      echo "[EXPORTED] ${NAME} -> ${RULESETS_DIR}/${NAME}.json"
    done
    ;;

  *)
    echo "Unknown subcommand: ${SUBCOMMAND}"
    echo "Usage: manage-rulesets.sh <apply|list|delete|delete-all|diff|export> [args]"
    exit 1
    ;;
esac
