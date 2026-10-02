#Requires -RunAsAdministrator
<#
    Disk and network benchmarks for a Windows guest on OpenShift Virtualization.
    Tested on Windows Server 2022 and Windows 11 23H2.

    Expects DiskSpd (diskspd.exe) and NTttcp (ntttcp.exe) in C:\bench.
    Download them from the Microsoft GitHub releases pages.

    Usage:
        .\windows-benchmark.ps1                      # disk only
        .\windows-benchmark.ps1 -PeerAddress 10.0.0.5 # disk + network sender
#>

param(
    [string] $BenchDir = 'C:\bench',
    [string] $TestFile = 'C:\bench\diskspd.dat',
    [string] $PeerAddress = ''
)

$ErrorActionPreference = 'Stop'
$DiskSpd = Join-Path $BenchDir 'diskspd.exe'
$Ntttcp = Join-Path $BenchDir 'ntttcp.exe'

if (-not (Test-Path $DiskSpd)) { throw "diskspd.exe not found in $BenchDir" }

Write-Host '=== 4K random read, queue depth 32, 4 threads ==='
& $DiskSpd -c4G -b4K -r4K -o32 -t4 -d60 -w0 -Sh -L -D $TestFile

Write-Host ''
Write-Host '=== 4K random write, queue depth 32, 4 threads ==='
& $DiskSpd -b4K -r4K -o32 -t4 -d60 -w100 -Sh -L $TestFile

Write-Host ''
Write-Host '=== 128K sequential read, queue depth 8, 2 threads ==='
& $DiskSpd -b128K -si -o8 -t2 -d60 -w0 -Sh -L $TestFile

Write-Host ''
Write-Host '=== 128K sequential write, queue depth 8, 2 threads ==='
& $DiskSpd -b128K -si -o8 -t2 -d60 -w100 -Sh -L $TestFile

Remove-Item -Path $TestFile -Force -ErrorAction SilentlyContinue

if ($PeerAddress) {
    if (-not (Test-Path $Ntttcp)) { throw "ntttcp.exe not found in $BenchDir" }
    Write-Host ''
    Write-Host "=== Network throughput to $PeerAddress (sender, 8 threads, 60s) ==="
    Write-Host "Start the receiver first:  ntttcp.exe -r -m 8,*,$PeerAddress -t 60"
    & $Ntttcp -s -m 8,*,$PeerAddress -t 60
}

Write-Host ''
Write-Host 'Benchmarks complete.'
