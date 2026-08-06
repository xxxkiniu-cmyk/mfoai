#!/bin/bash
cd ~/.mfo
git add -A
git commit -m "$1"
git push origin master
echo "✅ Gotowe! Wysłano na GitHub."
