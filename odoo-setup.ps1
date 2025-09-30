# ===============================================
# PowerShell Script to Setup Odoo 17 Environment
# ===============================================

# Stop on errors
$ErrorActionPreference = "Stop"

# Step 1: Activate or create virtual environment
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
} else {
    Write-Host "Virtual environment already exists."
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

# Step 2: Upgrade pip, setuptools, wheel
Write-Host "Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# Step 3: Install requirements
$requirementsPath = "C:\Program Files\Odoo 17.0.20250819\server\requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "Installing Odoo dependencies..."
    pip install -r $requirementsPath
} else {
    Write-Host "ERROR: requirements.txt not found at $requirementsPath"
    exit 1
}

# Step 4: Check if odoo.conf exists
if (-Not (Test-Path "odoo.conf")) {
    Write-Host "Creating minimal odoo.conf..."
    @"
[options]
addons_path = $PWD\addons
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
"@ | Out-File -Encoding UTF8 odoo.conf
}

Write-Host "Setup complete! Run Odoo with:"
Write-Host "python odoo-bin -c odoo.conf"
