#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Checking workflow downloads and experiment-workflows-flat organization..."
echo

# Expected workflow types based on the matrix
declare -A WORKFLOW_TYPES=(
    ["ubuntu-24.04"]="Ubuntu Default"
    ["ubuntu-24.04-shared"]="Ubuntu Shared"
    ["buildjet-2vcpu-ubuntu-2204"]="BuildJet Default"
    ["buildjet-2vcpu-ubuntu-2204-shared"]="BuildJet Shared"
)

if [ ! -d "experiment-workflows-gh" ]; then
    echo -e "${RED}✗ experiment-workflows-gh directory not found${NC}"
    echo "  Run ./workflows-download.sh first"
    exit 1
fi

if [ ! -d "experiment-workflows-flat" ]; then
    echo -e "${RED}✗ experiment-workflows-flat directory not found${NC}"
    exit 1
fi

# Track overall status
HAS_ERRORS=0

echo "📊 Checking downloaded artifacts in experiment-workflows-gh..."
declare -A DOWNLOAD_COUNTS
for dir in experiment-workflows-gh/gatling-report-*; do
    if [ -d "$dir" ]; then
        # Extract workflow type from directory name
        # Pattern: gatling-report-{workflow-type}-{run-id}-{commit-sha}
        basename_dir=$(basename "$dir")
        # Remove prefix and suffix to get workflow type
        workflow_type=$(echo "$basename_dir" | sed -E 's/^gatling-report-(.+)-[0-9]+-[a-f0-9]+$/\1/')
        ((DOWNLOAD_COUNTS[$workflow_type]++))
    fi
done

for workflow_type in "${!WORKFLOW_TYPES[@]}"; do
    count="${DOWNLOAD_COUNTS[$workflow_type]:-0}"
    if [ "$count" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} ${WORKFLOW_TYPES[$workflow_type]}: $count artifacts downloaded"
    else
        echo -e "  ${RED}✗${NC} ${WORKFLOW_TYPES[$workflow_type]}: No artifacts found"
        HAS_ERRORS=1
    fi
done
echo

echo "📁 Checking experiment-workflows-flat organization..."
for workflow_type in "${!WORKFLOW_TYPES[@]}"; do
    if [ -d "experiment-workflows-flat/$workflow_type" ]; then
        # Count runs in flat directory
        flat_count=$(find "experiment-workflows-flat/$workflow_type" -mindepth 1 -maxdepth 1 -type d | wc -l)

        # Count expected runs from downloads
        expected_count=0
        for dir in experiment-workflows-gh/gatling-report-*; do
            if [ -d "$dir" ]; then
                # Extract workflow type from this directory
                basename_dir=$(basename "$dir")
                dir_workflow_type=$(echo "$basename_dir" | sed -E 's/^gatling-report-(.+)-[0-9]+-[a-f0-9]+$/\1/')
                if [ "$dir_workflow_type" = "$workflow_type" ]; then
                    ((expected_count++))
                fi
            fi
        done

        if [ "$flat_count" -eq "$expected_count" ] && [ "$expected_count" -gt 0 ]; then
            echo -e "  ${GREEN}✓${NC} $workflow_type: $flat_count runs present"
        elif [ "$expected_count" -eq 0 ]; then
            echo -e "  ${YELLOW}⚠${NC}  $workflow_type: No downloaded artifacts to flatten"
        else
            echo -e "  ${RED}✗${NC} $workflow_type: Found $flat_count runs, expected $expected_count"
            HAS_ERRORS=1
        fi
    else
        # Check if there are any downloads for this type
        has_downloads=0
        for dir in experiment-workflows-gh/gatling-report-*; do
            if [ -d "$dir" ]; then
                basename_dir=$(basename "$dir")
                dir_workflow_type=$(echo "$basename_dir" | sed -E 's/^gatling-report-(.+)-[0-9]+-[a-f0-9]+$/\1/')
                if [ "$dir_workflow_type" = "$workflow_type" ]; then
                    has_downloads=1
                    break
                fi
            fi
        done

        if [ "$has_downloads" -eq 1 ]; then
            echo -e "  ${RED}✗${NC} $workflow_type: Directory missing in experiment-workflows-flat"
            HAS_ERRORS=1
        else
            echo -e "  ${YELLOW}⚠${NC}  $workflow_type: No artifacts to check"
        fi
    fi
done
echo

# Check individual runs for completeness
echo "🔎 Checking individual runs for required files..."
MISSING_FILES=0
for workflow_type in "${!WORKFLOW_TYPES[@]}"; do
    if [ -d "experiment-workflows-flat/$workflow_type" ]; then
        for run_dir in experiment-workflows-flat/$workflow_type/trackerexportertests-*; do
            if [ -d "$run_dir" ]; then
                # Check for required files
                missing=""
                [ ! -f "$run_dir/index.html" ] && missing="$missing index.html"
                [ ! -f "$run_dir/simulation.log" ] && missing="$missing simulation.log"
                [ ! -f "$run_dir/simulation.csv" ] && missing="$missing simulation.csv"
                [ ! -f "$run_dir/req_events--1291329255.html" ] && missing="$missing req_events--1291329255.html"

                if [ -n "$missing" ]; then
                    echo -e "  ${RED}✗${NC} $(basename "$run_dir") missing:$missing"
                    MISSING_FILES=1
                    HAS_ERRORS=1
                fi
            fi
        done
    fi
done

if [ "$MISSING_FILES" -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} All runs contain required files"
fi
echo

echo "📋 Summary:"
if [ "$HAS_ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo "All workflows have been downloaded and properly organized in experiment-workflows-flat"
else
    echo -e "${RED}❌ Some checks failed${NC}"
    echo "Please review the errors above and run the appropriate scripts to fix them"
    exit 1
fi
