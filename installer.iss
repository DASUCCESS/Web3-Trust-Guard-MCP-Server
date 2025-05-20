[Setup]
AppName=Web3 Trust Guard MCP Server
AppVersion=1.0
DefaultDirName={pf}\Web3TrustGuard
DefaultGroupName=Web3 Trust Guard MCP Server
OutputBaseFilename=Web3TrustGuardInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\web3trustguard.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Icons]
Name: "{group}\Web3 Trust Guard MCP Server"; Filename: "{app}\web3trustguard.exe"
Name: "{commondesktop}\Web3 Trust Guard MCP Server"; Filename: "{app}\web3trustguard.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Web3 Trust Guard MCP Server"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\web3trustguard.exe"; Description: "Launch Web3 Trust Guard MCP Server"; Flags: nowait postinstall skipifsilent
