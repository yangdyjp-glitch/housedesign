# Download only. Review the handoff before running on the new computer.
$ErrorActionPreference = 'Stop'
$projectParent = Join-Path $env:USERPROFILE 'Documents'
$projectRoot = Join-Path $projectParent 'HomeDesign'

function Invoke-ProjectGit {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]] $GitArguments)
    & git @GitArguments
    if ($LASTEXITCODE -ne 0) { throw "Git 操作失败，退出码 $LASTEXITCODE" }
}

if (Test-Path -LiteralPath $projectRoot) {
    throw '目标目录已存在。请检查原内容，或选择另一个空目录；不要直接覆盖。'
}

Invoke-ProjectGit -c core.longpaths=true -c core.autocrlf=false clone --recurse-submodules --no-single-branch https://github.com/yangdyjp-glitch/housedesign.git $projectRoot
Invoke-ProjectGit -C $projectRoot config --local core.longpaths true
Invoke-ProjectGit -C $projectRoot config --local core.autocrlf false
Invoke-ProjectGit -C $projectRoot fetch --all --tags --prune
Invoke-ProjectGit -C $projectRoot submodule update --init --recursive
Invoke-ProjectGit -C $projectRoot rev-parse --is-shallow-repository
Invoke-ProjectGit -C $projectRoot status --short --branch
Invoke-ProjectGit -C $projectRoot fsck --full
Invoke-ProjectGit -C $projectRoot merge-base --is-ancestor 323f294aecf255b77f2262af95bf626e17d09b87 HEAD
