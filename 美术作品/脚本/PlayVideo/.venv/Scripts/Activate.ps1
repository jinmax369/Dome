<#
.Synopsis
Activate a Python virtual environment for the current PowerShell session.

.Description
Pushes the python executable for a virtual environment to the front of the
$Env:PATH environment variable and sets the prompt to signify that you are
in a Python virtual environment. Makes use of the command line switches as
well as the `pyvenv.cfg` file values present in the virtual environment.

.Parameter VenvDir
Path to the directory that contains the virtual environment to activate. The
default value for this is the parent of the directory that the Activate.ps1
script is located within.

.Parameter Prompt
The prompt prefix to display when this virtual environment is activated. By
default, this prompt is the name of the virtual environment folder (VenvDir)
surrounded by parentheses and followed by a single space (ie. '(.venv) ').

.Example
Activate.ps1
Activates the Python virtual environment that contains the Activate.ps1 script.

.Example
Activate.ps1 -Verbose
Activates the Python virtual environment that contains the Activate.ps1 script,
and shows extra information about the activation as it executes.

.Example
Activate.ps1 -VenvDir C:\Users\MyUser\Common\.venv
Activates the Python virtual environment located in the specified location.

.Example
Activate.ps1 -Prompt "MyPython"
Activates the Python virtual environment that contains the Activate.ps1 script,
and prefixes the current prompt with the specified string (surrounded in
parentheses) while the virtual environment is active.

.Notes
On Windows, it may be required to enable this Activate.ps1 script by setting the
execution policy for the user. You can do this by issuing the following PowerShell
command:

PS C:\> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

For more information on Execution Policies: 
https://go.microsoft.com/fwlink/?LinkID=135170

#>
Param(
    [Parameter(Mandatory = $false)]
    [String]
    $VenvDir,
    [Parameter(Mandatory = $false)]
    [String]
    $Prompt
)

<# Function declarations --------------------------------------------------- #>

<#
.Synopsis
Remove all shell session elements added by the Activate script, including the
addition of the virtual environment's Python executable from the beginning of
the PATH variable.

.Parameter NonDestructive
If present, do not remove this function from the global namespace for the
session.

#>
function global:deactivate ([switch]$NonDestructive) {
    # Revert to original values

    # The prior prompt:
    if (Test-Path -Path Function:_OLD_VIRTUAL_PROMPT) {
        Copy-Item -Path Function:_OLD_VIRTUAL_PROMPT -Destination Function:prompt
        Remove-Item -Path Function:_OLD_VIRTUAL_PROMPT
    }

    # The prior PYTHONHOME:
    if (Test-Path -Path Env:_OLD_VIRTUAL_PYTHONHOME) {
        Copy-Item -Path Env:_OLD_VIRTUAL_PYTHONHOME -Destination Env:PYTHONHOME
        Remove-Item -Path Env:_OLD_VIRTUAL_PYTHONHOME
    }

    # The prior PATH:
    if (Test-Path -Path Env:_OLD_VIRTUAL_PATH) {
        Copy-Item -Path Env:_OLD_VIRTUAL_PATH -Destination Env:PATH
        Remove-Item -Path Env:_OLD_VIRTUAL_PATH
    }

    # Just remove the VIRTUAL_ENV altogether:
    if (Test-Path -Path Env:VIRTUAL_ENV) {
        Remove-Item -Path env:VIRTUAL_ENV
    }

    # Just remove VIRTUAL_ENV_PROMPT altogether.
    if (Test-Path -Path Env:VIRTUAL_ENV_PROMPT) {
        Remove-Item -Path env:VIRTUAL_ENV_PROMPT
    }

    # Just remove the _PYTHON_VENV_PROMPT_PREFIX altogether:
    if (Get-Variable -Name "_PYTHON_VENV_PROMPT_PREFIX" -ErrorAction SilentlyContinue) {
        Remove-Variable -Name _PYTHON_VENV_PROMPT_PREFIX -Scope Global -Force
    }

    # Leave deactivate function in the global namespace if requested:
    if (-not $NonDestructive) {
        Remove-Item -Path function:deactivate
    }
}

<#
.Description
Get-PyVenvConfig parses the values from the pyvenv.cfg file located in the
given folder, and returns them in a map.

For each line in the pyvenv.cfg file, if that line can be parsed into exactly
two strings separated by `=` (with any amount of whitespace surrounding the =)
then it is considered a `key = value` line. The left hand string is the key,
the right hand is the value.

If the value starts with a `'` or a `"` then the first and last character is
stripped from the value before being captured.

.Parameter ConfigDir
Path to the directory that contains the `pyvenv.cfg` file.
#>
function Get-PyVenvConfig(
    [String]
    $ConfigDir
) {
    Write-Verbose "Given ConfigDir=$ConfigDir, obtain values in pyvenv.cfg"

    # Ensure the file exists, and issue a warning if it doesn't (but still allow the function to continue).
    $pyvenvConfigPath = Join-Path -Resolve -Path $ConfigDir -ChildPath 'pyvenv.cfg' -ErrorAction Continue

    # An empty map will be returned if no config file is found.
    $pyvenvConfig = @{ }

    if ($pyvenvConfigPath) {

        Write-Verbose "File exists, parse `key = value` lines"
        $pyvenvConfigContent = Get-Content -Path $pyvenvConfigPath

        $pyvenvConfigContent | ForEach-Object {
            $keyval = $PSItem -split "\s*=\s*", 2
            if ($keyval[0] -and $keyval[1]) {
                $val = $keyval[1]

                # Remove extraneous quotations around a string value.
                if ("'""".Contains($val.Substring(0, 1))) {
                    $val = $val.Substring(1, $val.Length - 2)
                }

                $pyvenvConfig[$keyval[0]] = $val
                Write-Verbose "Adding Key: '$($keyval[0])'='$val'"
            }
        }
    }
    return $pyvenvConfig
}


<# Begin Activate script --------------------------------------------------- #>

# Determine the containing directory of this script
$VenvExecPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VenvExecDir = Get-Item -Path $VenvExecPath

Write-Verbose "Activation script is located in path: '$VenvExecPath'"
Write-Verbose "VenvExecDir Fullname: '$($VenvExecDir.FullName)"
Write-Verbose "VenvExecDir Name: '$($VenvExecDir.Name)"

# Set values required in priority: CmdLine, ConfigFile, Default
# First, get the location of the virtual environment, it might not be
# VenvExecDir if specified on the command line.
if ($VenvDir) {
    Write-Verbose "VenvDir given as parameter, using '$VenvDir' to determine values"
}
else {
    Write-Verbose "VenvDir not given as a parameter, using parent directory name as VenvDir."
    $VenvDir = $VenvExecDir.Parent.FullName.TrimEnd("\\/")
    Write-Verbose "VenvDir=$VenvDir"
}

# Next, read the `pyvenv.cfg` file to determine any required value such
# as `prompt`.
$pyvenvCfg = Get-PyVenvConfig -ConfigDir $VenvDir

# Next, set the prompt from the command line, or the config file, or
# just use the name of the virtual environment folder.
if ($Prompt) {
    Write-Verbose "Prompt specified as argument, using '$Prompt'"
}
else {
    Write-Verbose "Prompt not specified as argument to script, checking pyvenv.cfg value"
    if ($pyvenvCfg -and $pyvenvCfg['prompt']) {
        Write-Verbose "  Setting based on value in pyvenv.cfg='$($pyvenvCfg['prompt'])'"
        $Prompt = $pyvenvCfg['prompt'];
    }
    else {
        Write-Verbose "  Setting prompt based on parent's directory's name. (Is the directory name passed to venv module when creating the virtual environment)"
        Write-Verbose "  Got leaf-name of $VenvDir='$(Split-Path -Path $venvDir -Leaf)'"
        $Prompt = Split-Path -Path $venvDir -Leaf
    }
}

Write-Verbose "Prompt = '$Prompt'"
Write-Verbose "VenvDir='$VenvDir'"

# Deactivate any currently active virtual environment, but leave the
# deactivate function in place.
deactivate -nondestructive

# Now set the environment variable VIRTUAL_ENV, used by many tools to determine
# that there is an activated venv.
$env:VIRTUAL_ENV = $VenvDir

if (-not $Env:VIRTUAL_ENV_DISABLE_PROMPT) {

    Write-Verbose "Setting prompt to '$Prompt'"

    # Set the prompt to include the env name
    # Make sure _OLD_VIRTUAL_PROMPT is global
    function global:_OLD_VIRTUAL_PROMPT { "" }
    Copy-Item -Path function:prompt -Destination function:_OLD_VIRTUAL_PROMPT
    New-Variable -Name _PYTHON_VENV_PROMPT_PREFIX -Description "Python virtual environment prompt prefix" -Scope Global -Option ReadOnly -Visibility Public -Value $Prompt

    function global:prompt {
        Write-Host -NoNewline -ForegroundColor Green "($_PYTHON_VENV_PROMPT_PREFIX) "
        _OLD_VIRTUAL_PROMPT
    }
    $env:VIRTUAL_ENV_PROMPT = $Prompt
}

# Clear PYTHONHOME
if (Test-Path -Path Env:PYTHONHOME) {
    Copy-Item -Path Env:PYTHONHOME -Destination Env:_OLD_VIRTUAL_PYTHONHOME
    Remove-Item -Path Env:PYTHONHOME
}

# Add the venv to the PATH
Copy-Item -Path Env:PATH -Destination Env:_OLD_VIRTUAL_PATH
$Env:PATH = "$VenvExecDir$([System.IO.Path]::PathSeparator)$Env:PATH"

#-----BEGIN-SIGNATURE-----
# TQoAADCCCkkGCSqGSIb3DQEHAqCCCjowggo2AgEBMQ8wDQYJKoZIhvcNAQELBQAw
# CwYJKoZIhvcNAQcBoIIHZTCCB2EwggVJoAMCAQICEAf+q645FYLSHMpcP88Z7u0w
# DQYJKoZIhvcNAQELBQAwaTELMAkGA1UEBhMCVVMxFzAVBgNVBAoTDkRpZ2lDZXJ0
# LCBJbmMuMUEwPwYDVQQDEzhEaWdpQ2VydCBUcnVzdGVkIEc0IENvZGUgU2lnbmlu
# ZyBSU0E0MDk2IFNIQTM4NCAyMDIxIENBMTAeFw0yNDAxMjkwMDAwMDBaFw0yNTAx
# MjgyMzU5NTlaMGkxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpDYWxpZm9ybmlhMRMw
# EQYDVQQHEwpTYW4gUmFmYWVsMRcwFQYDVQQKEw5BdXRvZGVzaywgSW5jLjEXMBUG
# A1UEAxMOQXV0b2Rlc2ssIEluYy4wggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIK
# AoICAQC0RxrB/ltX22+FLPkE5TvZGoUNMh4MS8IuVzCX1frS9SXLKfVSvPbK2hko
# NL5h4OEKFDZwdgkjQWUtqGeJofdPN4wDkR/OPz/1bYuHCLtVBcBTQsZ7NlmHaJX0
# hsDJrItSjDgocxuxvioKBwqvmXwAJ4fbvOuNx73MkuyU8w8ZeSjtWZM3FENRzjoV
# JgwJerWJbVkpxKTU80tsOSTzZ8WvYp1M6/0joYD5+VH88YUSYLMWiNTJSWubZGAS
# sNDkAgyHu3JaVStUskhv9NAlnhJaq5lSZFEqpc80noAlxQOYQyJlD1J5Mn+z6AUF
# L9Rd3AYw0ofXYh8fFWqnwFjrS/XKqixdF7nt5enEJPfkEkNqTJEdyeFy/fu9SQ8M
# S1KfYugbtnyEv1ycIwWQepN4TxuKi/R3sL7xczeKu+1RhrjBGoWNztWFxqGVDhbA
# OuUtWN5qF7BWvIyQ91YbNIcmvvB5TkFgwZKZjNnydik317UB50qbHXMx8Az2+07s
# zl4wkDVp9p3Bli01iPZn/oQceRse33o/Uomab5cezVB5nvsGILwUhHSH5C30Oj3U
# /Y6bCSjzIYV8jDcJBb9MN9mvDGuMW+hu68bcW7N/6ZopHzV1mnev4yH3wSTV595c
# twUVl+axNVAE0qR9NzXFze1TcZ9qnuQPU8s9KDRrih7lJSrCmQIDAQABo4ICAzCC
# Af8wHwYDVR0jBBgwFoAUaDfg67Y7+F8Rhvv+YXsIiGX0TkIwHQYDVR0OBBYEFLvQ
# k6uXtIxMbptXKFi9ul6yfaHsMD4GA1UdIAQ3MDUwMwYGZ4EMAQQBMCkwJwYIKwYB
# BQUHAgEWG2h0dHA6Ly93d3cuZGlnaWNlcnQuY29tL0NQUzAOBgNVHQ8BAf8EBAMC
# B4AwEwYDVR0lBAwwCgYIKwYBBQUHAwMwgbUGA1UdHwSBrTCBqjBToFGgT4ZNaHR0
# cDovL2NybDMuZGlnaWNlcnQuY29tL0RpZ2lDZXJ0VHJ1c3RlZEc0Q29kZVNpZ25p
# bmdSU0E0MDk2U0hBMzg0MjAyMUNBMS5jcmwwU6BRoE+GTWh0dHA6Ly9jcmw0LmRp
# Z2ljZXJ0LmNvbS9EaWdpQ2VydFRydXN0ZWRHNENvZGVTaWduaW5nUlNBNDA5NlNI
# QTM4NDIwMjFDQTEuY3JsMIGUBggrBgEFBQcBAQSBhzCBhDAkBggrBgEFBQcwAYYY
# aHR0cDovL29jc3AuZGlnaWNlcnQuY29tMFwGCCsGAQUFBzAChlBodHRwOi8vY2Fj
# ZXJ0cy5kaWdpY2VydC5jb20vRGlnaUNlcnRUcnVzdGVkRzRDb2RlU2lnbmluZ1JT
# QTQwOTZTSEEzODQyMDIxQ0ExLmNydDAJBgNVHRMEAjAAMA0GCSqGSIb3DQEBCwUA
# A4ICAQBW3pC8sfzMhKHTYPYe6UqU0IX/tPfIFJNdtGQoeYdBBjbLAowcdlzQ1KLM
# 9HC/93aXV9q8iONYwFY8oajmFASaNc6Zk7vZQTPA8ug96a8ynTWXsdasfTYK9z0U
# JF6J8jg/NJMHQq8lx0RX3JtyfJpf5JDll6M6h5B3FhN/QtBaRTNJ+DT8hjQ0p+eu
# fYJmnWH1GyiVmLTGnM0KnMFLplpNrPDiE5iVy7B+lynlR27oKvc+NZD8O2Ly/KSO
# ayY7paYZd/tH+nU6E2w4qy8CNclXlVxPFf2dt41Nik6slu/rQSVnjRJ/EKvOIOrQ
# 0nPUAx3oNUkgHtDO8/jnZ06H/bUMUvtmp96RIyzYXPfCfKKlzRvvpwNOUPuN9+ka
# 6JyN2iNpe/ZNH41YGMFvr/y9pg+qN1lYhsjvA6+uVKFbIerPFdJ9gSpRzpmFQUHh
# 11DHn6OPnO/hCJyWg50uDhQ9C7nvVRbsoZ/2Hz9uwUKcJiBE8RTFK4hvopa/nVSi
# eiKQwyadDgwRkKmPSB3ezKXDeYU3TOG7ugP9WHLgUIL20hKhN5nGom8REHPsCJI7
# xewV44xlWDOu5/00WH9Y70s4qvXjQchpGMEluCyj3jKpYVxPO1cUnGl+8l03Ntdu
# 80MDBkfVy9kc9SAvG0wxas1/UM7SUNa0gl7M+mkRue0rjKRqOzGCAqgwggKkAgEB
# MH0waTELMAkGA1UEBhMCVVMxFzAVBgNVBAoTDkRpZ2lDZXJ0LCBJbmMuMUEwPwYD
# VQQDEzhEaWdpQ2VydCBUcnVzdGVkIEc0IENvZGUgU2lnbmluZyBSU0E0MDk2IFNI
# QTM4NCAyMDIxIENBMQIQB/6rrjkVgtIcylw/zxnu7TANBgkqhkiG9w0BAQsFADAN
# BgkqhkiG9w0BAQEFAASCAgAuwUU/vDhi+Z5pshBgH/pZXDk/1oC2vhjRqwSL0Bm8
# 2rxEw2SJxDU1MpFa1K0FMZWF7kHHOUfBrF2jpJC0QW5W+Oeu9onPZGGgfyBgRiz9
# UnK6+ZmTBPKX7umNBQDcccqxCYE8d09D0Kiq1zDLTEuPUtpFaZLEb6YXLqCrFblG
# isqBcqrbwMiDI2lxDXLGTrfd3t0pqpzsF778hGEOviDQHCoRAHROljyiE9KdGcVg
# r+Xtp5rKoRZmqZFHpJegRyB1jWt9+ZN6pOmoB3EvPWGxWHw3SlL1x/wjB8IAMC5G
# 1MfFOiSXLL5Umk01WOMQ/shRYgIooGIolMuS35RhYrF5ygcaQhVKLJIiGZrAoimi
# fscEe6k6R/hNdSmMfsJUegfzJFkOJErrclYGudKkPjF5EX0M6+9TQ4MFred790+T
# atgCHKNjhLeTylbFhHlnpN19ooaqTLTvZSGXM/JfJ5yzleg8BCdD0nKla34/Fn8L
# hccwsggobLZCKBYwTCVYgQ8WU6iD4Y6UJo6oB61lomajyuqSvShJNPkm3NuCs7Iv
# Cat6n4H8/A3KgTOFGVMOnoHpqnHtR7QCsowuG6DZ4huBqOKlfRJ/oLtdkuT7Rnwb
# hXS+lpJjGsXgjns4Yh2fvIayJqtGfZ/aniVQ18nhDoTM8BJys+rtzBJVQqgIQsbv
# aQ==
# -----END-SIGNATURE-----