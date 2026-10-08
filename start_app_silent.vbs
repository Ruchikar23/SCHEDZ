Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)

If fso.FolderExists(strDir & "\SCHEDZ") Then
    WshShell.CurrentDirectory = strDir & "\SCHEDZ"
Else
    WshShell.CurrentDirectory = strDir
End If

WshShell.Run "pythonw main.py", 0, False
