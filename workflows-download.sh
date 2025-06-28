#!/bin/bash
# Download all artifacts from the 4 matrix workflows

mkdir -p experiment-workflows-gh

echo "Downloading Ubuntu Default artifacts..."
gh run list --workflow="Tracker Performance - Ubuntu Default" --json databaseId --jq '.[].databaseId' | xargs -I {} gh run download {} --dir experiment-workflows-gh

echo "Downloading Ubuntu Shared artifacts..."
gh run list --workflow="Tracker Performance - Ubuntu Shared" --json databaseId --jq '.[].databaseId' | xargs -I {} gh run download {} --dir experiment-workflows-gh

echo "Downloading BuildJet Default artifacts..."
gh run list --workflow="Tracker Performance - BuildJet Default" --json databaseId --jq '.[].databaseId' | xargs -I {} gh run download {} --dir experiment-workflows-gh

echo "Downloading BuildJet Shared artifacts..."
gh run list --workflow="Tracker Performance - BuildJet Shared" --json databaseId --jq '.[].databaseId' | xargs -I {} gh run download {} --dir experiment-workflows-gh

echo "Download complete! Check ./experiment-workflows-gh folder"
