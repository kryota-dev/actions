#!/usr/bin/env bash

# ADR creation script
# Replaces the functionality of the deprecated `adr` npm package

set -euo pipefail

ADR_DIR="docs/adr"
TEMPLATE_FILE="${ADR_DIR}/.template.md"

# Function to get the next ADR number
get_next_number() {
  local max_num=0
  for file in "${ADR_DIR}"/*.md; do
    if [[ -f "$file" && "$file" != *"README.md"* && "$file" != *"/.template.md"* ]]; then
      local basename=$(basename "$file")
      if [[ $basename =~ ^([0-9]+)- ]]; then
        local num=${BASH_REMATCH[1]}
        # Remove leading zeros for comparison
        num=$((10#$num))
        if ((num > max_num)); then
          max_num=$num
        fi
      fi
    fi
  done
  echo $((max_num + 1))
}

# Function to convert title to kebab-case
to_kebab_case() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g'
}

# Function to update the README
update_readme() {
  local num=$1
  local title=$2
  local filename=$3

  # Add entry to README if not already present
  if ! grep -q "\[${num}\. ${title}\]" "${ADR_DIR}/README.md" 2>/dev/null; then
    # Insert before the last line (empty line)
    local entry="* [${num}. ${title}](${filename})"
    if [[ -f "${ADR_DIR}/README.md" ]]; then
      # Add to the end of the file
      echo "$entry" >> "${ADR_DIR}/README.md"
    else
      # Create README if it doesn't exist
      echo "# Architecture Decision Records" > "${ADR_DIR}/README.md"
      echo "" >> "${ADR_DIR}/README.md"
      echo "$entry" >> "${ADR_DIR}/README.md"
    fi
  fi
}

# Main script
main() {
  if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <title>"
    echo "Example: $0 \"Use PostgreSQL for data storage\""
    exit 1
  fi

  # Join all arguments as the title
  local title="$*"
  local kebab_title=$(to_kebab_case "$title")
  local next_num=$(get_next_number)
  local padded_num=$(printf "%03d" "$next_num")
  local filename="${padded_num}-${kebab_title}.md"
  local filepath="${ADR_DIR}/${filename}"
  local current_date=$(date +%Y-%m-%d)

  # Create ADR file from template or use default
  if [[ -f "$TEMPLATE_FILE" ]]; then
    sed -e "s/{{NUMBER}}/${next_num}/g" \
        -e "s/{{TITLE}}/${title}/g" \
        -e "s/{{DATE}}/${current_date}/g" \
        "$TEMPLATE_FILE" > "$filepath"
  else
    cat > "$filepath" <<EOF
# ${next_num}. ${title}

Date: ${current_date}

## Status

${current_date} proposed

## Context

Context here...

## Decision

Decision here...

## Consequences

Consequences here...
EOF
  fi

  # Update README
  update_readme "$next_num" "$title" "$filename"

  echo "Created: ${filepath}"
  echo "Remember to:"
  echo "  1. Fill in the Context, Decision, and Consequences sections"
  echo "  2. Update the Status as needed (proposed → accepted → deprecated → superseded)"
}

main "$@"
