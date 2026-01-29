# Extract CORTEX dashboard from archive/CORTEX-5.0
$source_branch = 'archive/CORTEX-5.0'
$target_dir = '_workspaces\dashboard'

# Get list of all files in dashboard
$files = git ls-tree -r $source_branch --name-only -- cortex/brain/dashboard | Where-Object { $_ -notmatch '^cortex/brain/dashboard/frontend/__init__|^cortex/brain/dashboard/frontend/css/__init__|^cortex/brain/dashboard/frontend/js/__init__|^cortex/brain/dashboard/frontend/js/components/__init__' }

# Extract each file
foreach ($file in $files) {
  $target_path = $target_dir + '\' + ($file -replace '^cortex/brain/dashboard/', '')
  $target_folder = Split-Path $target_path -Parent
  
  # Create folder if needed
  if (-not (Test-Path $target_folder)) {
    New-Item -ItemType Directory -Path $target_folder -Force | Out-Null
  }
  
  # Extract file
  git show \$source_branch:\$file > \$target_path 2>
  Write-Host 'Extracted:' $file
}
Write-Host 'Dashboard extraction complete!'
