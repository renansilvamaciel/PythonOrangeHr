Set-Location -Path (Resolve-Path "$PSScriptRoot\..")
$exclude = @("venv", ".env", ".gitignore", "temp", "output", "build", "PythonOrangeHrm.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "PythonOrangeHrm.zip" -Force