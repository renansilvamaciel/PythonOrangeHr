$exclude = @("venv", "PythonOrangeHr.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "PythonOrangeHr.zip" -Force