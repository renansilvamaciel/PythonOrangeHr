Set-Location -Path (Resolve-Path "$PSScriptRoot\..")
$exclude = @("venv", ".env", ".gitignore", "temp", "output", "build", "Nav_BeaPro.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "Nav_BeaPro.zip" -Force