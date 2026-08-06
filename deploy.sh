#!/bin/bash
cd ~/.mfo
git add -A
git commit -m "$1"
git push origin main
echo "✅ Gotowe! Wysłano na GitHub."
