; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Spine Toolbox"
#define MyAppVersion "0.3-beta.2"
#define MyAppPublisher "Spine Project Consortium"
#define MyAppURL "https://github.com/Spine-project"
#define MyAppExeName "spinetoolbox.exe"
#define MyAppRegKey "Software\SpineProject"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{F16FFBAA-F643-48F1-B1A6-EDA13D2467FA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\Spine Toolbox
DefaultGroupName=Spine Toolbox
AllowNoIcons=yes
LicenseFile=COPYING.LESSER
OutputBaseFilename=spine-toolbox-{#MyAppVersion}-x64
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
OutputDir=spinetoolbox\dist
ArchitecturesInstallIn64BitMode=x64 ia64
ArchitecturesAllowed=x64 ia64 arm64
UsePreviousAppDir=yes

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if RegKeyExists(HKEY_CURRENT_USER, '{#MyAppRegKey}') then
      if MsgBox('Do you want to delete Spine Toolbox settings from registry?',
        mbConfirmation, MB_YESNO) = IDYES
      then
        RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, '{#MyAppRegKey}');
  end;
end;

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "spinetoolbox\build\exe.win-amd64-3.6\spinetoolbox.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "spinetoolbox\build\exe.win-amd64-3.6\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Dirs]
Name: "{app}\projects"; Permissions: users-full
Name: "{app}\work"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName} {#MyAppVersion}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName} {#MyAppVersion}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

