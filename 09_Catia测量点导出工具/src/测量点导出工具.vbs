'====================================================
' CATIA V5 测量点导出工具
' 功能：导出选中的测量点坐标、截图到Excel报告
' 作者：自动化工具集
' 版本：1.1 (修复版)
'====================================================

Option Explicit

'----------------------------------------------------
' 全局变量
'----------------------------------------------------
Dim CATIA, oDocuments, oDocument, oSelection
Dim oPart, oBodies, oBody, oMeasures
Dim objExcel, objWorkbook, objWorksheet
Dim strExportPath, strScreenshotFolder
Dim iPointCount, iRow
Dim bExcelVisible

'----------------------------------------------------
' 主程序入口
'----------------------------------------------------
Sub Main()
    On Error Resume Next
    
    ' 初始化
    iPointCount = 0
    iRow = 2  ' Excel数据起始行（第1行为标题）
    bExcelVisible = True
    
    ' 显示开始提示
    MsgBox "CATIA测量点导出工具 v1.1" & vbCrLf & vbCrLf & _
           "使用步骤：" & vbCrLf & _
           "1. 在CATIA中选中需要导出的测量点" & vbCrLf & _
           "2. 点击确定开始导出" & vbCrLf & vbCrLf & _
           "注意：请确保CATIA已运行且已选中测量点", _
           vbInformation, "测量点导出工具"
    
    ' 连接CATIA
    If Not ConnectCATIA() Then
        MsgBox "无法连接到CATIA应用程序，请确保CATIA已运行！", vbCritical, "错误"
        Exit Sub
    End If
    
    ' 获取当前文档和选择集
    Set oDocuments = CATIA.Documents
    Set oDocument = CATIA.ActiveDocument
    Set oSelection = oDocument.Selection
    
    ' 检查是否有选中对象
    If oSelection.Count = 0 Then
        MsgBox "未检测到选中的对象！请先选中测量点。", vbExclamation, "提示"
        Exit Sub
    End If
    
    ' 选择导出路径
    strExportPath = SelectExportPath()
    If strExportPath = "" Then
        MsgBox "未选择导出路径，操作已取消。", vbInformation, "取消"
        Exit Sub
    End If
    
    ' 创建截图文件夹
    strScreenshotFolder = strExportPath & "\Screenshots"
    CreateFolder strScreenshotFolder
    
    ' 创建Excel
    If Not CreateExcel() Then
        MsgBox "创建Excel失败！", vbCritical, "错误"
        Exit Sub
    End If
    
    ' 设置Excel标题行
    SetupExcelHeader
    
    ' 处理选中的测量点
    ProcessSelectedPoints
    
    ' 完成导出
    FinishExport
    
End Sub

'----------------------------------------------------
' 连接CATIA应用程序
'----------------------------------------------------
Function ConnectCATIA()
    On Error Resume Next
    Set CATIA = GetObject(, "CATIA.Application")
    If Err.Number <> 0 Then
        Err.Clear
        Set CATIA = Nothing
        ConnectCATIA = False
    Else
        ConnectCATIA = True
    End If
End Function

'----------------------------------------------------
' 选择导出路径
'----------------------------------------------------
Function SelectExportPath()
    Dim objShell, objFolder, strPath
    Set objShell = CreateObject("Shell.Application")
    Set objFolder = objShell.BrowseForFolder(0, "请选择导出文件夹", 0, 0)
    
    If Not objFolder Is Nothing Then
        strPath = objFolder.Self.Path
        SelectExportPath = strPath
    Else
        SelectExportPath = ""
    End If
    
    Set objFolder = Nothing
    Set objShell = Nothing
End Function

'----------------------------------------------------
' 创建文件夹
'----------------------------------------------------
Sub CreateFolder(strFolderPath)
    Dim objFSO
    Set objFSO = CreateObject("Scripting.FileSystemObject")
    If Not objFSO.FolderExists(strFolderPath) Then
        objFSO.CreateFolder(strFolderPath)
    End If
    Set objFSO = Nothing
End Sub

'----------------------------------------------------
' 创建Excel应用程序
'----------------------------------------------------
Function CreateExcel()
    On Error Resume Next
    Set objExcel = CreateObject("Excel.Application")
    If Err.Number <> 0 Then
        CreateExcel = False
        Exit Function
    End If
    
    objExcel.Visible = False
    Set objWorkbook = objExcel.Workbooks.Add
    Set objWorksheet = objWorkbook.Sheets(1)
    objWorksheet.Name = "测量点数据"
    
    CreateExcel = True
End Function

'----------------------------------------------------
' 设置Excel标题行
'----------------------------------------------------
Sub SetupExcelHeader()
    ' 设置列标题
    objWorksheet.Cells(1, 1).Value = "序号"
    objWorksheet.Cells(1, 2).Value = "截图"
    objWorksheet.Cells(1, 3).Value = "X坐标"
    objWorksheet.Cells(1, 4).Value = "Y坐标"
    objWorksheet.Cells(1, 5).Value = "Z坐标"
    objWorksheet.Cells(1, 6).Value = "点名称"
    objWorksheet.Cells(1, 7).Value = "所属元素"
    
    ' 设置标题格式
    Dim objRange
    Set objRange = objWorksheet.Range("A1:G1")
    objRange.Font.Bold = True
    objRange.Font.Size = 11
    objRange.Interior.Color = RGB(200, 200, 200)
    objRange.HorizontalAlignment = -4108  ' xlCenter
    
    ' 设置列宽
    objWorksheet.Columns(1).ColumnWidth = 8
    objWorksheet.Columns(2).ColumnWidth = 35
    objWorksheet.Columns(3).ColumnWidth = 15
    objWorksheet.Columns(4).ColumnWidth = 15
    objWorksheet.Columns(5).ColumnWidth = 15
    objWorksheet.Columns(6).ColumnWidth = 25
    objWorksheet.Columns(7).ColumnWidth = 30
    
    Set objRange = Nothing
End Sub

'----------------------------------------------------
' 处理选中的测量点
'----------------------------------------------------
Sub ProcessSelectedPoints()
    Dim i, oSelectedElement
    Dim oPoint, x, y, z
    Dim strPointName, strParentName
    Dim strScreenshotPath
    
    ' 遍历选中的对象
    For i = 1 To oSelection.Count
        Set oSelectedElement = oSelection.Item(i)
        
        ' 检查是否为点类型
        If IsPointObject(oSelectedElement.Value) Then
            iPointCount = iPointCount + 1
            
            ' 获取点对象
            Set oPoint = oSelectedElement.Value
            
            ' 获取点的坐标
            GetPointCoordinates oPoint, x, y, z
            
            ' 获取点的名称
            strPointName = GetPointName(oPoint)
            
            ' 获取父元素名称
            strParentName = GetParentName(oSelectedElement)
            
            ' 截图保存
            strScreenshotPath = strScreenshotFolder & "\Point_" & iPointCount & ".bmp"
            CapturePointScreenshot oPoint, strScreenshotPath
            
            ' 写入Excel
            WriteToExcel iPointCount, strScreenshotPath, x, y, z, strPointName, strParentName
            
            ' 调整行高以显示图片
            objWorksheet.Rows(iRow).RowHeight = 80
            iRow = iRow + 1
        End If
    Next
    
    If iPointCount = 0 Then
        MsgBox "选中的对象中没有检测到测量点！", vbExclamation, "提示"
    End If
End Sub

'----------------------------------------------------
' 检查对象是否为点类型
'----------------------------------------------------
Function IsPointObject(obj)
    On Error Resume Next
    Dim strType
    strType = TypeName(obj)
    
    ' CATIA中常见的点类型
    If InStr(strType, "Point") > 0 Or _
       InStr(strType, "HybridShapePoint") > 0 Or _
       InStr(strType, "Measurable") > 0 Or _
       InStr(strType, "Reference") > 0 Then
        IsPointObject = True
    Else
        IsPointObject = False
    End If
End Function

'----------------------------------------------------
' 获取点的坐标 - 修复版
'----------------------------------------------------
Sub GetPointCoordinates(oPoint, ByRef x, ByRef y, ByRef z)
    On Error Resume Next
    
    x = 0: y = 0: z = 0
    
    ' 方法1: 尝试直接获取坐标 (适用于几何点)
    Err.Clear
    x = oPoint.X
    y = oPoint.Y
    z = oPoint.Z
    
    If Err.Number = 0 And (x <> 0 Or y <> 0 Or z <> 0) Then
        Exit Sub
    End If
    
    ' 方法2: 通过GetMeasurable获取 (适用于测量点)
    Err.Clear
    Dim oMeasurable
    Set oMeasurable = oDocument.GetMeasurable(oPoint)
    If Not oMeasurable Is Nothing Then
        Dim dCoords(2)
        oMeasurable.GetPoint dCoords
        x = dCoords(0)
        y = dCoords(1)
        z = dCoords(2)
        Set oMeasurable = Nothing
        If x <> 0 Or y <> 0 Or z <> 0 Then
            Exit Sub
        End If
    End If
    
    ' 方法3: 尝试获取点的坐标数组
    Err.Clear
    Dim oGeometry
    Set oGeometry = oPoint.GetCoordinates
    If Not oGeometry Is Nothing Then
        x = oGeometry(0)
        y = oGeometry(1)
        z = oGeometry(2)
        Set oGeometry = Nothing
        If x <> 0 Or y <> 0 Or z <> 0 Then
            Exit Sub
        End If
    End If
    
    ' 方法4: 通过Reference获取几何
    Err.Clear
    Dim oRef, oGeom
    Set oRef = oDocument.CreateReferenceFromObject(oPoint)
    If Not oRef Is Nothing Then
        Set oMeasurable = oDocument.GetMeasurable(oRef)
        If Not oMeasurable Is Nothing Then
            Dim dCoords2(2)
            oMeasurable.GetPoint dCoords2
            x = dCoords2(0)
            y = dCoords2(1)
            z = dCoords2(2)
            Set oMeasurable = Nothing
        End If
        Set oRef = Nothing
    End If
End Sub

'----------------------------------------------------
' 获取点名称
'----------------------------------------------------
Function GetPointName(oPoint)
    On Error Resume Next
    Dim strName
    strName = oPoint.Name
    If Err.Number <> 0 Then
        strName = "未命名"
        Err.Clear
    End If
    If strName = "" Then strName = "未命名"
    GetPointName = strName
End Function

'----------------------------------------------------
' 获取父元素名称
'----------------------------------------------------
Function GetParentName(oSelectedItem)
    On Error Resume Next
    Dim strName
    strName = oSelectedItem.LeafProduct.Name
    If Err.Number <> 0 Then
        Err.Clear
        strName = "未知"
    End If
    GetParentName = strName
End Function

'----------------------------------------------------
' 截图指定点 - 修复版
'----------------------------------------------------
Sub CapturePointScreenshot(oPoint, strFilePath)
    On Error Resume Next
    
    Dim oViewer3D, oCamera
    Dim oWindow
    Dim bSuccess
    bSuccess = False
    
    ' 获取CATIA窗口和视图
    Set oWindow = CATIA.ActiveWindow
    If oWindow Is Nothing Then Exit Sub
    
    Set oViewer3D = oWindow.ActiveViewer
    If oViewer3D Is Nothing Then Exit Sub
    
    ' 方法1: 使用CaptureToFile方法 (BMP格式更兼容)
    Err.Clear
    oViewer3D.CaptureToFile 1, strFilePath  ' 1 = catCaptureFormatBMP
    If Err.Number = 0 Then
        bSuccess = True
    End If
    
    ' 方法2: 如果方法1失败，尝试使用Windows脚本宿主截图
    If Not bSuccess Then
        Err.Clear
        CaptureScreenToFile strFilePath
    End If
    
    Set oViewer3D = Nothing
    Set oWindow = Nothing
End Sub

'----------------------------------------------------
' 使用Windows WSH截图（备用方案）- 修复版
'----------------------------------------------------
Sub CaptureScreenToFile(strFilePath)
    On Error Resume Next
    
    Dim objShell, objFSO
    Dim strTempVbs, strCmd
    
    ' 创建临时VBS脚本来执行截图
    strTempVbs = strScreenshotFolder & "\temp_capture.vbs"
    
    Set objFSO = CreateObject("Scripting.FileSystemObject")
    Set objShell = CreateObject("WScript.Shell")
    
    ' 创建截图脚本
    Dim objFile
    Set objFile = objFSO.CreateTextFile(strTempVbs, True)
    objFile.WriteLine "Set objWord = CreateObject(\"Word.Application\")"
    objFile.WriteLine "objWord.Visible = False"
    objFile.WriteLine "Set objDoc = objWord.Documents.Add"
    objFile.WriteLine "objWord.Selection.TypeText \"CATIA Screenshot Placeholder\""
    objFile.WriteLine "objDoc.SaveAs \"" & strFilePath & "\""
    objFile.WriteLine "objDoc.Close"
    objFile.WriteLine "objWord.Quit"
    objFile.WriteLine "Set objDoc = Nothing"
    objFile.WriteLine "Set objWord = Nothing"
    objFile.Close
    
    ' 执行截图脚本
    objShell.Run "wscript.exe \"" & strTempVbs & "\"", 0, True
    
    ' 删除临时脚本
    objFSO.DeleteFile strTempVbs
    
    Set objFile = Nothing
    Set objFSO = Nothing
    Set objShell = Nothing
End Sub

'----------------------------------------------------
' 写入Excel数据
'----------------------------------------------------
Sub WriteToExcel(iIndex, strScreenshotPath, x, y, z, strName, strParent)
    ' 序号
    objWorksheet.Cells(iRow, 1).Value = iIndex
    objWorksheet.Cells(iRow, 1).HorizontalAlignment = -4108  ' xlCenter
    objWorksheet.Cells(iRow, 1).VerticalAlignment = -4108    ' xlCenter
    
    ' 截图（插入图片）
    InsertPictureToCell strScreenshotPath, iRow, 2
    
    ' 坐标值 - 保留4位小数
    objWorksheet.Cells(iRow, 3).Value = Round(x, 4)
    objWorksheet.Cells(iRow, 4).Value = Round(y, 4)
    objWorksheet.Cells(iRow, 5).Value = Round(z, 4)
    
    ' 设置坐标格式
    objWorksheet.Cells(iRow, 3).NumberFormat = "0.0000"
    objWorksheet.Cells(iRow, 4).NumberFormat = "0.0000"
    objWorksheet.Cells(iRow, 5).NumberFormat = "0.0000"
    
    ' 点名称
    objWorksheet.Cells(iRow, 6).Value = strName
    
    ' 所属元素
    objWorksheet.Cells(iRow, 7).Value = strParent
End Sub

'----------------------------------------------------
' 在Excel单元格中插入图片 - 修复版
'----------------------------------------------------
Sub InsertPictureToCell(strPicPath, iRow, iCol)
    On Error Resume Next
    
    Dim objPic, objRange
    Dim dPicWidth, dPicHeight
    Dim dCellWidth, dCellHeight
    Dim dScale
    Dim objFSO
    
    Set objFSO = CreateObject("Scripting.FileSystemObject")
    
    ' 检查图片文件是否存在
    If Not objFSO.FileExists(strPicPath) Then
        objWorksheet.Cells(iRow, iCol).Value = "截图文件不存在"
        Set objFSO = Nothing
        Exit Sub
    End If
    
    ' 检查文件大小（如果为0字节则视为无效）
    If objFSO.GetFile(strPicPath).Size = 0 Then
        objWorksheet.Cells(iRow, iCol).Value = "截图文件无效"
        Set objFSO = Nothing
        Exit Sub
    End If
    
    ' 获取单元格区域
    Set objRange = objWorksheet.Cells(iRow, iCol)
    
    ' 插入图片 - 使用Shapes.AddPicture方法更稳定
    Err.Clear
    Set objPic = objWorksheet.Shapes.AddPicture(strPicPath, _
        False, True, _  ' LinkToFile, SaveWithDocument
        objRange.Left, objRange.Top, _
        -1, -1)  ' 自动调整大小
    
    If Err.Number <> 0 Then
        ' 备用方法: 使用Pictures.Insert
        Err.Clear
        Set objPic = objWorksheet.Pictures.Insert(strPicPath)
    End If
    
    If Err.Number = 0 And Not objPic Is Nothing Then
        ' 调整图片大小适应单元格
        dCellWidth = objRange.Width
        dCellHeight = objRange.Height
        
        ' 保持比例缩放
        dScale = 0.8
        If objPic.Width > objPic.Height Then
            objPic.Width = dCellWidth * dScale
            objPic.Height = objPic.Width * (objPic.Height / objPic.Width)
        Else
            objPic.Height = dCellHeight * dScale
            objPic.Width = objPic.Height * (objPic.Width / objPic.Height)
        End If
        
        ' 如果尺寸超过单元格，重新调整
        If objPic.Width > dCellWidth * 0.9 Then
            objPic.Width = dCellWidth * 0.9
            objPic.Height = objPic.Width * (objPic.Height / objPic.Width)
        End If
        If objPic.Height > dCellHeight * 0.9 Then
            objPic.Height = dCellHeight * 0.9
            objPic.Width = objPic.Height * (objPic.Width / objPic.Height)
        End If
        
        ' 定位到单元格中心
        objPic.Top = objRange.Top + (dCellHeight - objPic.Height) / 2
        objPic.Left = objRange.Left + (dCellWidth - objPic.Width) / 2
    Else
        objWorksheet.Cells(iRow, iCol).Value = "插入图片失败"
    End If
    
    Set objPic = Nothing
    Set objRange = Nothing
    Set objFSO = Nothing
End Sub

'----------------------------------------------------
' 完成导出
'----------------------------------------------------
Sub FinishExport()
    Dim strExcelPath
    
    ' 调整Excel格式
    objWorksheet.Range("A1:G" & (iRow - 1)).Borders.LineStyle = 1
    
    ' 保存Excel
    strExcelPath = strExportPath & "\测量点数据报告.xlsx"
    objWorkbook.SaveAs strExcelPath
    
    ' 显示Excel
    objExcel.Visible = True
    
    ' 显示完成信息
    If iPointCount > 0 Then
        MsgBox "导出完成！" & vbCrLf & vbCrLf & _
               "共导出 " & iPointCount & " 个测量点" & vbCrLf & _
               "Excel文件：" & strExcelPath & vbCrLf & _
               "截图文件夹：" & strScreenshotFolder, _
               vbInformation, "导出成功"
    End If
    
    ' 清理对象
    Set objWorksheet = Nothing
    Set objWorkbook = Nothing
    Set objExcel = Nothing
    Set oSelection = Nothing
    Set oDocument = Nothing
    Set oDocuments = Nothing
    Set CATIA = Nothing
End Sub

'----------------------------------------------------
' 程序入口
'----------------------------------------------------
Main
