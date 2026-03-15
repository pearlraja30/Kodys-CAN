#define MyAppName "Kodys Foot Clinik V2"
#define MyAppVersion "V2"
#define MyAppPublisher "Kodys Foot Clinik"
#define MyAppExeName "run"

[Setup]
AppId={{2F7C5CFB-FAD2-427B-85A5-4AEB28544B55}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
OutputDir=Z:\Users\rajasekaran\Projects\KODYS\build_output\my_workspace
OutputBaseFilename="Kodys Foot Clinik Installer"
Compression=lzma
SolidCompression=yes
WizardStyle=modern


[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "Z:\Users\rajasekaran\Projects\KODYS\Source Code\p232\p232\appsource\dist\run\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

