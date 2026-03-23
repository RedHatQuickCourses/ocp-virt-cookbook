#!/bin/bash
set -euo pipefail

# ══════════════════════════════════════════════════════════════════════════════
# Documentation Review Script for ocp-virt-cookbook
# ══════════════════════════════════════════════════════════════════════════════
#
# This script performs automated quality checks on AsciiDoc documentation files.
# Exit code: 0 if no errors, 1 if any ERROR-level issues found.
# Warnings alone do NOT cause non-zero exit.

# ── Configuration ─────────────────────────────────────────────────────────────

# Product name patterns to check (case-sensitive)
declare -A PRODUCT_NAMES
PRODUCT_NAMES["Openshift"]="OpenShift"
PRODUCT_NAMES["openshift"]="OpenShift"

# Banned terminology patterns
declare -A BANNED_TERMS
BANNED_TERMS["k8s"]="Kubernetes"

# Admonition keywords
ADMONITIONS="NOTE|WARNING|TIP|IMPORTANT|CAUTION"

# Color codes (used when stdout is a terminal)
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[0;33m'
COLOR_BLUE='\033[0;34m'
COLOR_GREEN='\033[0;32m'
COLOR_RESET='\033[0m'

# Detect if output is to a terminal
if [[ -t 1 ]]; then
    USE_COLOR=true
else
    USE_COLOR=false
fi

# Counters
TOTAL_FILES=0
TOTAL_ERRORS=0
TOTAL_WARNINGS=0

# ── Helper Functions ──────────────────────────────────────────────────────────

# Output with color support
print_error() {
    if [[ "$USE_COLOR" == "true" ]]; then
        echo -e "${COLOR_RED}  ERROR  ${COLOR_RESET}$1"
    else
        echo "  ERROR  $1"
    fi
}

print_warn() {
    if [[ "$USE_COLOR" == "true" ]]; then
        echo -e "${COLOR_YELLOW}  WARN   ${COLOR_RESET}$1"
    else
        echo "  WARN   $1"
    fi
}

print_info() {
    if [[ "$USE_COLOR" == "true" ]]; then
        echo -e "${COLOR_BLUE}  INFO   ${COLOR_RESET}$1"
    else
        echo "  INFO   $1"
    fi
}

print_header() {
    if [[ "$USE_COLOR" == "true" ]]; then
        echo -e "${COLOR_GREEN}Reviewing: ${COLOR_RESET}$1"
    else
        echo "Reviewing: $1"
    fi
}

# ── Core Review Functions ─────────────────────────────────────────────────────

review_file() {
    local file="$1"
    local errors=0
    local warnings=0

    if [[ ! -f "$file" ]]; then
        print_error "File not found: $file"
        return 1
    fi

    print_header "$file"

    # Track state
    local in_code_block=false
    local code_block_lang=""
    local code_block_start_line=0
    local prev_line=""
    local heading_levels=()
    local first_heading_found=false
    local h1_count=0

    # Read file line by line
    local line_num=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        line_num=$((line_num + 1))

        # Skip comment lines for prose checks
        if [[ "$line" =~ ^// ]]; then
            prev_line="$line"
            continue
        fi

        # Track code block boundaries
        if [[ "$line" =~ ^---- ]]; then
            if [[ "$in_code_block" == "false" ]]; then
                in_code_block=true
                code_block_start_line=$line_num
                # Check for language specifier in previous line
                if [[ "$prev_line" =~ ^\[source,?([a-zA-Z0-9_-]*)\] ]] || [[ "$prev_line" =~ ^\[source,?([a-zA-Z0-9_-]*),.*\] ]]; then
                    code_block_lang="${BASH_REMATCH[1]}"
                else
                    code_block_lang=""
                    # Warn if code block has no language specified
                    if [[ ! "$prev_line" =~ ^\[source ]]; then
                        print_warn "line $line_num: Code block delimiter without [source,language] specifier"
                        warnings=$((warnings + 1))
                    fi
                fi
            else
                in_code_block=false
                code_block_lang=""
            fi
            prev_line="$line"
            continue
        fi

        # ── CODE BLOCK CHECKS ─────────────────────────────────────────────────

        if [[ "$in_code_block" == "true" ]]; then
            # Check for creationTimestamp in YAML blocks
            if [[ "$code_block_lang" == "yaml" ]] && [[ "$line" =~ creationTimestamp:\ *null ]]; then
                print_warn "line $line_num: creationTimestamp: null found in YAML block"
                warnings=$((warnings + 1))
            fi

            # Check for inline YAML flow syntax
            if [[ "$code_block_lang" == "yaml" ]] && { [[ "$line" =~ .*:\ *\{.*\} ]] || [[ "$line" =~ .*:\ *\[.*\] ]]; }; then
                # Skip legitimate cases like empty objects in specific contexts
                if [[ ! "$line" =~ chpasswd:\ *\{.*\} ]] && [[ ! "$line" =~ capabilities:$ ]]; then
                    print_warn "line $line_num: Inline YAML flow syntax detected (use block style)"
                    warnings=$((warnings + 1))
                fi
            fi

            prev_line="$line"
            continue
        fi

        # ── PROSE CHECKS (outside code blocks) ───────────────────────────────

        # Check heading hierarchy
        if [[ "$line" =~ ^(=+)\ +(.+)$ ]]; then
            local equals="${BASH_REMATCH[1]}"
            local level=${#equals}

            # Count H1s
            if [[ $level -eq 1 ]]; then
                h1_count=$((h1_count + 1))
                if [[ $h1_count -gt 1 ]]; then
                    print_error "line $line_num: Multiple H1 headings found (should have only one)"
                    errors=$((errors + 1))
                fi
                if [[ "$first_heading_found" == "true" ]]; then
                    print_error "line $line_num: H1 must be the first heading in the file"
                    errors=$((errors + 1))
                fi
            fi

            first_heading_found=true

            # Check for skipped levels
            if [[ ${#heading_levels[@]} -gt 0 ]]; then
                local prev_level=${heading_levels[-1]}
                if [[ $level -gt $((prev_level + 1)) ]]; then
                    print_error "line $line_num: Heading level skipped (previous: $prev_level, current: $level)"
                    errors=$((errors + 1))
                fi
            fi

            heading_levels+=("$level")

            # Check for blank line after heading
            # We'll check this on the next iteration
            prev_line="$line"
            continue
        fi

        # Check if previous line was a heading and this line is not blank
        # Skip attribute lines (starting with :) and other headings
        if [[ "$prev_line" =~ ^(=+)\ +(.+)$ ]] && [[ -n "$line" ]] && \
           [[ ! "$line" =~ ^: ]] && [[ ! "$line" =~ ^= ]]; then
            print_warn "line $((line_num-1)): Section heading not followed by blank line"
            warnings=$((warnings + 1))
        fi

        # Check for trailing whitespace
        if [[ "$line" =~ [[:space:]]$ ]]; then
            print_warn "line $line_num: Trailing whitespace"
            warnings=$((warnings + 1))
        fi

        # Check for bare URLs (not in link: macro or implicit URL macro)
        if [[ "$line" =~ https?:// ]] && [[ ! "$line" =~ link:https?:// ]]; then
            # Skip xref, image, include directives, and implicit URL macro (URL followed by [)
            if [[ ! "$line" =~ ^(xref:|image::|include::) ]] && [[ ! "$line" =~ https?://[^[:space:]]+\[ ]]; then
                print_warn "line $line_num: Bare URL not in link: macro"
                warnings=$((warnings + 1))
            fi
        fi

        # Check external links for window=_blank
        if [[ "$line" =~ link:(https?://[^[]+)\[([^\]]*)\] ]]; then
            local url="${BASH_REMATCH[1]}"
            local link_content="${BASH_REMATCH[2]}"
            if [[ ! "$link_content" =~ window=_blank ]]; then
                print_warn "line $line_num: External link missing window=_blank"
                warnings=$((warnings + 1))
            fi
        fi

        # Check for image without alt text
        if [[ "$line" =~ image::([^[]+)\[\] ]]; then
            print_warn "line $line_num: Image has no alt text: ${BASH_REMATCH[0]}"
            warnings=$((warnings + 1))
        fi

        # Check product name capitalization
        for wrong in "${!PRODUCT_NAMES[@]}"; do
            if [[ "$line" =~ $wrong ]]; then
                local correct="${PRODUCT_NAMES[$wrong]}"
                print_warn "line $line_num: '$wrong' should be '$correct'"
                warnings=$((warnings + 1))
            fi
        done

        # Check banned terminology
        for banned in "${!BANNED_TERMS[@]}"; do
            # Use word boundaries to avoid false positives
            if [[ "$line" =~ (^|[^a-zA-Z0-9])$banned([^a-zA-Z0-9]|$) ]]; then
                local replacement="${BANNED_TERMS[$banned]}"
                print_warn "line $line_num: Banned term '$banned' (use '$replacement')"
                warnings=$((warnings + 1))
            fi
        done

        # Check admonition capitalization
        if [[ "$line" =~ ^($ADMONITIONS):\ +([a-z]) ]]; then
            local admonition="${BASH_REMATCH[1]}"
            local first_char="${BASH_REMATCH[2]}"
            print_warn "line $line_num: Admonition should be followed by capitalized word: $admonition: ${first_char}"
            warnings=$((warnings + 1))
        fi

        prev_line="$line"
    done < "$file"

    # Check for trailing newline at EOF
    if [[ -n "$(tail -c 1 "$file")" ]]; then
        print_warn "File does not end with a newline character"
        ((warnings++))
    fi

    # Check for required sections (for tutorial pages)
    if [[ "$file" =~ modules/[^/]+/pages/[^/]+\.adoc ]] && \
       [[ ! "$file" =~ /index\.adoc$ ]] && \
       [[ ! "$file" =~ /nav\.adoc$ ]]; then

        local has_prerequisites=false
        local has_summary=false

        while IFS= read -r line; do
            if [[ "$line" =~ ^==\ +Prerequisites ]]; then
                has_prerequisites=true
            fi
            if [[ "$line" =~ ^==\ +(Summary|Verification) ]]; then
                has_summary=true
            fi
        done < "$file"

        if [[ "$has_prerequisites" == "false" ]]; then
            print_warn "Tutorial page missing '== Prerequisites' section"
            warnings=$((warnings + 1))
        fi
        if [[ "$has_summary" == "false" ]]; then
            print_warn "Tutorial page missing '== Summary' or '== Verification' section"
            warnings=$((warnings + 1))
        fi
    fi

    # Word count and read time (excluding code blocks)
    local word_count=0
    local in_block=false
    while IFS= read -r line; do
        if [[ "$line" =~ ^---- ]]; then
            if [[ "$in_block" == "false" ]]; then
                in_block=true
            else
                in_block=false
            fi
            continue
        fi

        if [[ "$in_block" == "false" ]] && [[ ! "$line" =~ ^// ]]; then
            local line_words=$(echo "$line" | wc -w)
            word_count=$((word_count + line_words))
        fi
    done < "$file"

    local read_time=$((word_count / 200))
    if [[ $read_time -eq 0 ]] && [[ $word_count -gt 0 ]]; then
        read_time=1
    fi

    print_info "Word count: $word_count | Estimated read time: $read_time min"
    echo ""

    TOTAL_ERRORS=$((TOTAL_ERRORS + errors))
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + warnings))

    return $errors
}

review_nav_file() {
    local nav_file="$1"
    local errors=0

    if [[ ! -f "$nav_file" ]]; then
        print_error "nav.adoc not found: $nav_file"
        return 1
    fi

    # Determine the module directory
    local module_dir=$(dirname "$nav_file")
    local pages_dir="$module_dir/pages"

    if [[ ! -d "$pages_dir" ]]; then
        print_error "Pages directory not found for $nav_file: $pages_dir"
        return 1
    fi

    # Extract all xref targets
    local line_num=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        line_num=$((line_num + 1))

        if [[ "$line" =~ xref:([^[]+)\[ ]]; then
            local target="${BASH_REMATCH[1]}"
            local target_file="$pages_dir/$target"

            if [[ ! -f "$target_file" ]]; then
                print_error "line $line_num in $nav_file: xref target does not exist: $target_file"
                errors=$((errors + 1))
            fi
        fi
    done < "$nav_file"

    TOTAL_ERRORS=$((TOTAL_ERRORS + errors))
    return $errors
}

validate_yaml_blocks() {
    local file="$1"
    local errors=0

    # Check if Python with PyYAML is available
    if ! python3 -c "import yaml" 2>/dev/null; then
        return 0
    fi

    # Extract YAML blocks and validate
    local in_yaml_header=false
    local in_yaml_content=false
    local yaml_content=""
    local block_start_line=0
    local line_num=0

    while IFS= read -r line || [[ -n "$line" ]]; do
        line_num=$((line_num + 1))

        # Detect start of YAML block
        if [[ "$line" =~ ^\[source,yaml ]]; then
            in_yaml_header=true
            yaml_content=""
            block_start_line=$line_num
            continue
        fi

        # Detect code block delimiter
        if [[ "$line" =~ ^---- ]]; then
            if [[ "$in_yaml_header" == "true" ]]; then
                # We're entering the YAML content
                in_yaml_header=false
                in_yaml_content=true
                continue
            elif [[ "$in_yaml_content" == "true" ]]; then
                # We're exiting the YAML block - validate it
                if [[ -n "$yaml_content" ]]; then
                    if ! echo "$yaml_content" | python3 -c "import sys, yaml; yaml.safe_load(sys.stdin.read())" 2>/dev/null; then
                        print_error "line $block_start_line: Invalid YAML syntax in code block"
                        errors=$((errors + 1))
                    fi
                fi
                yaml_content=""
                in_yaml_content=false
                continue
            fi
        fi

        # Accumulate YAML content
        if [[ "$in_yaml_content" == "true" ]]; then
            yaml_content+="$line"$'\n'
        fi
    done < "$file"

    TOTAL_ERRORS=$((TOTAL_ERRORS + errors))
    return $errors
}

# ── Main Script ───────────────────────────────────────────────────────────────

main() {
    local files=()
    local run_build_check=false

    # Parse arguments
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 [--all] [--build] <file1.adoc> [file2.adoc ...]"
        echo ""
        echo "Options:"
        echo "  --all     Review all .adoc files under modules/"
        echo "  --build   Run Antora build check (validates xrefs)"
        echo ""
        echo "Examples:"
        echo "  $0 modules/networking/pages/some-tutorial.adoc"
        echo "  $0 --all"
        echo "  $0 --build modules/*/pages/*.adoc"
        exit 0
    fi

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --all)
                # Find all .adoc files under modules/
                mapfile -t files < <(find modules -name "*.adoc" -type f 2>/dev/null | sort)
                shift
                ;;
            --build)
                run_build_check=true
                shift
                ;;
            *)
                files+=("$1")
                shift
                ;;
        esac
    done

    if [[ ${#files[@]} -eq 0 ]]; then
        echo "No files to review."
        exit 0
    fi

    # Review each file
    local file_errors=0
    for file in "${files[@]}"; do
        TOTAL_FILES=$((TOTAL_FILES + 1))

        review_file "$file" || file_errors=$((file_errors + 1))

        # Check nav.adoc files
        if [[ "$file" =~ /nav\.adoc$ ]]; then
            review_nav_file "$file" || file_errors=$((file_errors + 1))
        fi

        # Validate YAML blocks
        validate_yaml_blocks "$file" || file_errors=$((file_errors + 1))
    done

    # Run Antora build check if requested
    if [[ "$run_build_check" == "true" ]]; then
        echo "Running Antora build check..."
        if command -v pnpm &> /dev/null; then
            if pnpm run build 2>&1 | grep -i "error\|warning.*xref"; then
                print_error "Antora build produced errors or broken xrefs"
                file_errors=$((file_errors + 1))
            fi
        else
            print_warn "pnpm not found, skipping build check"
        fi
    fi

    # Print summary
    echo "════════════════════════════════════════════════════════════════"
    echo "Summary: $TOTAL_FILES file(s) reviewed | $TOTAL_ERRORS error(s) | $TOTAL_WARNINGS warning(s)"
    echo "════════════════════════════════════════════════════════════════"

    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        exit 1
    else
        exit 0
    fi
}

main "$@"
