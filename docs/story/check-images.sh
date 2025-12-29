#!/bin/bash
# Check all story chapter images

cd "$(dirname "$0")"

echo "🔍 Checking Story Images..."
echo "================================"

# Check JavaScript-configured images
echo ""
echo "📋 JavaScript-configured images (story-viewer.js):"
grep -o "src: '[^']*'" story-viewer.js | sed "s/src: '//;s/'//" | while read path; do
  if [ -f "$path" ]; then
    echo "✅ $path"
  else
    echo "❌ MISSING: $path"
  fi
done

# Check embedded HTML images
echo ""
echo "📋 Embedded HTML images (in markdown files):"
for chapter in Prologue Chapter-{01..13}; do
  if [ -f "$chapter/index.md" ]; then
    count=$(/usr/bin/grep -c '<img src=' "$chapter/index.md" 2>/dev/null || echo "0")
    if [ "$count" -gt 0 ]; then
      echo ""
      echo "=== $chapter ($count images) ==="
      /usr/bin/grep -o 'src="[^"]*"' "$chapter/index.md" | sed 's/src="//;s/"$//' | while read imgpath; do
        # Convert relative path to absolute from chapter directory
        if [[ "$imgpath" == ../* ]]; then
          actualpath="${imgpath#../}"
          if [ -f "$actualpath" ]; then
            echo "  ✅ $imgpath"
          else
            echo "  ❌ MISSING: $imgpath (looking for $actualpath)"
          fi
        fi
      done
    fi
  fi
done

echo ""
echo "================================"
echo "✅ Check complete!"
