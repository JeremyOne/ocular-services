#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Updates the version number across all project files.

.DESCRIPTION
    This script updates version numbers in:
    - mcp/LLM_SERVICE_DOCUMENTATION.md (Documentation Version)
    - mcp/llm_service_schema.json (version and last_updated)
    - Creates/updates VERSION file
    
.PARAMETER Version
    The new version number in semantic versioning format (e.g., 1.0.0, 0.2.1)

.EXAMPLE
    .\update-version.ps1 -Version "1.0.0"
    Updates version to 1.0.0 and updates dates
    
.EXAMPLE
    .\update-version.ps1 -Version "1.1.0" -Commit
    Updates version to 1.1.0 and creates a git commit
    
.EXAMPLE
    .\update-version.ps1 -Version "1.0.1" -UpdateDate:$false
    Updates version to 1.0.1 without changing dates
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$Version
)


# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir

# Files to update
$files = @(
    @{
        Path = Join-Path $projectRoot "mcp\LLM_SERVICE_DOCUMENTATION.md"
        Updates = @(
            @{
                Pattern = '- \*\*Documentation Version:\*\* \d+\.\d+\.\d+'
                Replacement = "- **Documentation Version:** $Version"
                Description = "Documentation version"
            }
        )
    },
    @{
        Path = Join-Path $projectRoot "mcp\llm_service_schema.json"
        Updates = @(
            @{
                Pattern = '"version":\s*"[\d\.]+"'
                Replacement = "`"version`": `"$Version`""
                Description = "Schema version"
            }
        )
    },
    @{
        Path = Join-Path $projectRoot "mcp\server.py"
        Updates = @(
            @{
                Pattern = 'version\s*=\s*"[\d\.]+"'
                Replacement = "version=`"$Version`""
                Description = "Server version"
            }
        )
    }
)


Write-Host "Updating project to version $Version" -ForegroundColor Cyan
Write-Host ""

$filesChanged = @()

# Process each file
foreach ($fileInfo in $files) {
    $filePath = $fileInfo.Path
    
    if (-not (Test-Path $filePath)) {
        Write-Warning "File not found: $filePath"
        continue
    }
    
    Write-Host "Processing: $($filePath.Replace($projectRoot, '.'))" -ForegroundColor Yellow
    
    $content = Get-Content $filePath -Raw
    $originalContent = $content
    $changed = $false
    
    foreach ($update in $fileInfo.Updates) {
        if ($content -match $update.Pattern) {
            $content = $content -replace $update.Pattern, $update.Replacement
            Write-Host "  ✓ Updated $($update.Description)" -ForegroundColor Green
            $changed = $true
        } else {
            Write-Host "  ✗ Pattern not found: $($update.Description)" -ForegroundColor Red
        }
    }
    
    if ($changed) {
        Set-Content -Path $filePath -Value $content -NoNewline
        $filesChanged += $filePath
        Write-Host ""
    }
}

# Create/Update VERSION file
$versionFilePath = Join-Path $projectRoot "VERSION"
Write-Host "Creating VERSION file..." -ForegroundColor Yellow
Set-Content -Path $versionFilePath -Value $Version -NoNewline
Write-Host "  ✓ Created/Updated VERSION file" -ForegroundColor Green
$filesChanged += $versionFilePath
Write-Host ""

# Summary
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor White
Write-Host "  Files changed: $($filesChanged.Count)" -ForegroundColor White
Write-Host ""

Write-Host "Version update complete! ✨" -ForegroundColor Green
