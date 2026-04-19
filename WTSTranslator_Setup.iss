; ============================================================================
;  WTS Translator — Inno Setup Script
;  Autor: Mateo Neufeld (SoyMante)
;  Asistencia: Claude (Anthropic)
; ============================================================================

#define AppName      "WTS Translator"
#define AppVersion   "1.0.0"
#define AppPublisher "SoyMante"
#define AppURL       "https://github.com/ItsMante"
#define AppExe       "WTS Translator.exe"
#define AppIcon      "logo.ico"

[Setup]
AppId={{A3F8C2D1-74E5-4B9A-8F3D-2C1E6A9B0D47}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoAfterFile=CREDITS.txt
OutputDir=.
OutputBaseFilename=WTSTranslator_Setup_v1.0.0
SetupIconFile={#AppIcon}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardImageFile=compiler:WizModernImage.bmp
WizardSmallImageFile=compiler:WizModernSmallImage.bmp
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}

; Mostrar la version en el titulo del instalador
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Installer

[Languages]
Name: "spanish";  MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english";  MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "{cm:CreateDesktopIcon}";    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon";  Description: "Crear acceso directo en el Menú Inicio"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "installollama";  Description: "Descargar e instalar Ollama (recomendado, ~1.8 GB)"; GroupDescription: "Dependencias opcionales:"; Flags: unchecked
Name: "downloadgemma";  Description: "Descargar modelo gemma2 tras la instalación (requiere Ollama, ~5 GB)"; GroupDescription: "Dependencias opcionales:"; Flags: unchecked

[Files]
; Archivos principales de la app
Source: "dist\WTS Translator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\glossary.json";      DestDir: "{app}"; Flags: ignoreversion
Source: "dist\logo.png";           DestDir: "{app}"; Flags: ignoreversion
Source: "dist\logo.ico";           DestDir: "{app}"; Flags: ignoreversion

; Archivos informativos — los creamos mas abajo en el script
Source: "LICENSE.txt";  DestDir: "{app}"; Flags: ignoreversion
Source: "CREDITS.txt";  DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Acceso directo en el menu inicio
Name: "{group}\{#AppName}";         Filename: "{app}\{#AppExe}"; IconFilename: "{app}\{#AppIcon}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"

; Acceso directo en el escritorio (opcional)
Name: "{autodesktop}\{#AppName}";   Filename: "{app}\{#AppExe}"; IconFilename: "{app}\{#AppIcon}"; Tasks: desktopicon

[Run]
; Abrir instalador de Ollama si el usuario lo eligio
Filename: "{tmp}\OllamaSetup.exe"; Description: "Instalando Ollama..."; \
  Flags: waituntilterminated shellexec skipifsilent; \
  Tasks: installollama; Check: OllamaDownloaded

; Abrir terminal para descargar gemma2 si el usuario lo eligio
Filename: "{cmd}"; Parameters: "/k ollama pull gemma2"; \
  Description: "Descargando modelo gemma2 (~5 GB, puede tardar varios minutos)..."; \
  Flags: shellexec skipifsilent; \
  Tasks: downloadgemma

; Ofrecer abrir la app al terminar
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; \
  Flags: nowait postinstall skipifsilent

[Code]
// ============================================================================
//  Variables globales
// ============================================================================
var
  OllamaDownloadedFlag: Boolean;

function OllamaDownloaded: Boolean;
begin
  Result := OllamaDownloadedFlag;
end;

// ============================================================================
//  Descarga de Ollama antes de instalar (si el usuario lo pidio)
// ============================================================================
procedure CurStepChanged(CurStep: TSetupStep);
var
  OllamaURL:    String;
  OllamaDest:   String;
  ResultCode:   Integer;
  DownloadPage: TDownloadWizardPage;
begin
  if CurStep = ssInstall then
  begin
    OllamaDownloadedFlag := False;

    if IsTaskSelected('installollama') then
    begin
      OllamaURL  := 'https://ollama.com/download/OllamaSetup.exe';
      OllamaDest := ExpandConstant('{tmp}\OllamaSetup.exe');

      // Mostrar pagina de descarga con barra de progreso
      DownloadPage := CreateDownloadPage(
        'Descargando Ollama',
        'Por favor espera mientras se descarga Ollama (~1.8 GB)...',
        nil);

      DownloadPage.Clear;
      DownloadPage.Add(OllamaURL, 'OllamaSetup.exe', '');
      DownloadPage.Show;

      try
        DownloadPage.Download;
        OllamaDownloadedFlag := True;
      except
        MsgBox(
          'No se pudo descargar Ollama.' + #13#10 +
          'Verifica tu conexion a internet e intentalo de nuevo,' + #13#10 +
          'o descargalo manualmente desde https://ollama.com',
          mbError, MB_OK);
        OllamaDownloadedFlag := False;
      finally
        DownloadPage.Hide;
      end;
    end;
  end;
end;

// ============================================================================
//  Aviso de peso antes de confirmar la descarga de gemma2
// ============================================================================
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = wpSelectTasks then
  begin
    if IsTaskSelected('downloadgemma') and not IsTaskSelected('installollama') then
    begin
      // Verificar si Ollama ya esta instalado en el sistema
      if not FileExists(ExpandConstant('{pf}\Ollama\ollama.exe')) and
         not FileExists(ExpandConstant('{localappdata}\Programs\Ollama\ollama.exe')) then
      begin
        if MsgBox(
          'Has seleccionado descargar gemma2 pero Ollama no parece estar instalado.' + #13#10 +
          'gemma2 requiere Ollama para funcionar.' + #13#10#13#10 +
          'Recomendamos tambien marcar "Descargar e instalar Ollama".' + #13#10#13#10 +
          'Continuar de todas formas?',
          mbConfirmation, MB_YESNO) = IDNO then
        begin
          Result := False;
          Exit;
        end;
      end;
    end;

    if IsTaskSelected('downloadgemma') then
    begin
      MsgBox(
        'Aviso: El modelo gemma2 pesa aproximadamente 5 GB.' + #13#10 +
        'La descarga se realizara al finalizar la instalacion' + #13#10 +
        'a traves de una ventana de terminal.' + #13#10#13#10 +
        'Asegurate de tener buena conexion a internet y espacio en disco.',
        mbInformation, MB_OK);
    end;
  end;
end;

// ============================================================================
//  Inicializacion del instalador
// ============================================================================
procedure InitializeWizard;
begin
  OllamaDownloadedFlag := False;
end;
