'====================================================
' CATIA测量点导出工具 - 使用示例
' 功能：展示如何在代码中调用导出功能
'====================================================

Option Explicit

' 示例：如何在自己的脚本中集成测量点导出功能

Sub Example_ExportPoints()
    Dim objExport
    
    ' 方式1: 直接调用主脚本
    ' CreateObject("WScript.Shell").Run "src\测量点导出工具.vbs"
    
    ' 方式2: 作为库引用（需要提取公共函数）
    ' 详见 src\测量点导出工具.vbs 中的函数实现
    
    MsgBox "请直接运行 src\测量点导出工具.vbs 文件", vbInformation, "使用提示"
End Sub

' 示例：CATIA选择点的代码片段
Sub Example_SelectPoints()
    Dim CATIA, oDocument, oSelection
    
    On Error Resume Next
    Set CATIA = GetObject(, "CATIA.Application")
    If CATIA Is Nothing Then
        MsgBox "CATIA未运行", vbExclamation
        Exit Sub
    End If
    
    Set oDocument = CATIA.ActiveDocument
    Set oSelection = oDocument.Selection
    
    ' 清空当前选择
    oSelection.Clear
    
    ' 用户可以通过界面选择点
    MsgBox "请在CATIA中选择测量点，然后运行导出工具", vbInformation
    
    Set oSelection = Nothing
    Set oDocument = Nothing
    Set CATIA = Nothing
End Sub

' 运行示例
' Example_ExportPoints
