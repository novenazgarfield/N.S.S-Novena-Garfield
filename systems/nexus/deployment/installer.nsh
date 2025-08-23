; NEXUS Research Workstation NSIS Installer Script
; 支持用户自定义安装路径和管理员权限请求

!include "MUI2.nsh"
!include "FileFunc.nsh"

; 安装程序信息
Name "NEXUS Research Workstation"
OutFile "NEXUS-Setup.exe"
InstallDir "$PROGRAMFILES64\NEXUS Research Workstation"
InstallDirRegKey HKLM "Software\NEXUS\Research Workstation" "InstallPath"
RequestExecutionLevel admin

; 界面配置
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; 安装页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

; 版本信息
VIProductVersion "1.0.0.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "NEXUS Research Workstation"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "Research Workstation Team"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© 2025 Research Workstation Team"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "NEXUS Research Workstation Installer"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "1.0.0.0"

; 安装组件
Section "NEXUS Core" SecCore
  SectionIn RO
  
  ; 设置输出路径
  SetOutPath "$INSTDIR"
  
  ; 安装文件
  File /r "${BUILD_RESOURCES_DIR}\*"
  
  ; 创建注册表项
  WriteRegStr HKLM "Software\NEXUS\Research Workstation" "InstallPath" "$INSTDIR"
  WriteRegStr HKLM "Software\NEXUS\Research Workstation" "Version" "1.0.0"
  
  ; 创建卸载程序
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; 添加到控制面板的程序列表
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NEXUS" "DisplayName" "NEXUS Research Workstation"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NEXUS" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NEXUS" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NEXUS" "Publisher" "Research Workstation Team"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NEXUS" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NEXUS" "NoRepair" 1
  
SectionEnd

Section "Desktop Shortcut" SecDesktop
  CreateShortCut "$DESKTOP\NEXUS Research Workstation.lnk" "$INSTDIR\NEXUS Research Workstation.exe"
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
  CreateDirectory "$SMPROGRAMS\NEXUS Research Workstation"
  CreateShortCut "$SMPROGRAMS\NEXUS Research Workstation\NEXUS Research Workstation.lnk" "$INSTDIR\NEXUS Research Workstation.exe"
  CreateShortCut "$SMPROGRAMS\NEXUS Research Workstation\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

; 组件描述
LangString DESC_SecCore ${LANG_ENGLISH} "Core NEXUS Research Workstation files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create a desktop shortcut"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Create start menu shortcuts"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; 卸载程序
Section "Uninstall"
  ; 删除文件
  RMDir /r "$INSTDIR"
  
  ; 删除快捷方式
  Delete "$DESKTOP\NEXUS Research Workstation.lnk"
  RMDir /r "$SMPROGRAMS\NEXUS Research Workstation"
  
  ; 删除注册表项
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NEXUS"
  DeleteRegKey HKLM "Software\NEXUS\Research Workstation"
  
SectionEnd

; 安装前检查
Function .onInit
  ; 检查是否已安装
  ReadRegStr $R0 HKLM "Software\NEXUS\Research Workstation" "InstallPath"
  StrCmp $R0 "" done
  
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "NEXUS Research Workstation is already installed. $\n$\nClick OK to remove the previous version or Cancel to cancel this upgrade." \
    IDOK uninst
  Abort
  
uninst:
  ClearErrors
  ExecWait '$R0\Uninstall.exe _?=$R0'
  
  IfErrors no_remove_uninstaller done
    Delete $R0\Uninstaller.exe
    RMDir $R0
  no_remove_uninstaller:
  
done:
FunctionEnd