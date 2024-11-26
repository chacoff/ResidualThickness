Icon "buildMachine\ResOverlay.ico"

!include "MUI2.nsh"
!include "FileFunc.nsh"

SetCompressor /SOLID lzma

Name "Residual Corrosion App"
OutFile "buildMachine\ResidualCorrosionApp.exe"
InstallDir "$LOCALAPPDATA\ResidualApp"

RequestExecutionLevel user

!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Main Section" SEC01

  StrCpy $1 "$INSTDIR\ResidualCorrosionApp"
  SetOutPath "$INSTDIR\ResidualCorrosionApp"
  CreateDirectory "$INSTDIR"
  
  ; Add the 7z executable to the plugins directory
  File /oname=$PLUGINSDIR\7z.exe "buildMachine\7z.exe"
  
  ; Copy the zip file to the plugins directory
  File /oname=$PLUGINSDIR\ResidualCorrosionApp.zip "buildMachine\ResidualCorrosionApp.zip"
  
  ; Extract the zip file using 7z
  ExecWait '"$PLUGINSDIR\7z.exe" x "$PLUGINSDIR\ResidualCorrosionApp.zip" -o"$INSTDIR\" -y'
  
  ; Check if extraction succeeded
  IfErrors 0 +2
    MessageBox MB_OK "Extraction failed. Installation will not proceed."
  
  ; Delete temporary files
  Delete "$PLUGINSDIR\7z.exe"
  Delete "$PLUGINSDIR\ResidualCorrosionApp.zip"
  
  CreateShortcut "$DESKTOP\Residual Corrosion.lnk" "$1\main.exe" "" "$1\main.exe" 0 SW_SHOWNORMAL "" "$1"
  
  WriteUninstaller "$INSTDIR\uninstaller.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\Residual Corrosion.lnk"
  
  RMDir /r "$INSTDIR"
SectionEnd

Function .onInit
  ; Check for previous installation and offer to remove it
  ReadRegStr $R0 HKCU "Software\ResidualCorrosionApp" "InstallPath"
  ${If} $R0 != ""
    MessageBox MB_YESNO "An existing installation was detected. Would you like to remove it first?" IDNO NoUninstall
      ; Attempt to silently uninstall previous version
      ExecWait '$R0\uninstaller.exe /S'
    NoUninstall:
  ${EndIf}
FunctionEnd

Function .onInstSuccess
  ; Open application after installation
  Exec "$INSTDIR\ResidualCorrosionApp\main.exe"
FunctionEnd
