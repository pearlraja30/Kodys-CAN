#define MyAppName "Kodys Foot Clinik V2"
#define MyAppVersion "V2"
#define MyAppPublisher "Kodys Foot Clinik"
#define MyAppExeName "Kodys Foot Clinik.exe"

[Setup]
AppId={{2F7C5CFB-FAD2-427B-85A5-4AEB28544B55}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
SetupIconFile=..\app_assets\appicon.ico
OutputDir=..\Output
OutputBaseFilename="Kodys_Foot_Clinik_Setup"
Compression=lzma
SolidCompression=yes
WizardStyle=modern


[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\Kodys Foot Clinik\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

 


