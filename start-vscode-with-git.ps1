$gitBin = "C:\Users\victo\Documents\pv program\git\mingw64\bin"
$codeCmd = "C:\Users\victo\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"

if (-not (Test-Path $gitBin)) {
    Write-Error "Git bin path not found: $gitBin"
    exit 1
}

if (-not (Test-Path $codeCmd)) {
    Write-Error "VS Code CLI not found: $codeCmd"
    exit 1
}

$env:PATH = "$gitBin;$env:PATH"
& $codeCmd "C:\Users\victo\Documents\pv program"
