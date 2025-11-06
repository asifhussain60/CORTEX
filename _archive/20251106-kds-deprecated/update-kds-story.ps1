$filePath = 'D:\PROJECTS\KDS\prompts\user\kds.md'
$newStoryPath = 'D:\PROJECTS\KDS\temp_story_replacement.md'

# Read the entire file
$content = Get-Content -Path $filePath -Raw

# Read the new story
$newStory = Get-Content -Path $newStoryPath -Raw

# Define the section to replace (from line 38 to before 'Who's who')
$pattern = '(?s)## 🧚 A story for humans:.*?### Who''s who \(quick reference\)'
$replacement = $newStory + \"

### Who's who (quick reference)\"

# Perform the replacement
$newContent = $content -replace $pattern, $replacement

# Write back to file
Set-Content -Path $filePath -Value $newContent -NoNewline

Write-Host \"✅ Successfully updated kds.md story section\" -ForegroundColor Green
