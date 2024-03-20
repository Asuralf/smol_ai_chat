# 如果 ./dist 存在，则删除并重新创建
if (Test-Path .\dist) {
    Remove-Item -Path .\dist -Recurse -Force
}
New-Item -ItemType Directory -Path .\dist

$distDirPath = ".\dist\chat"
New-Item -ItemType Directory -Path $distDirPath

# pack app
pyinstaller -i .\icon.png -w chat.py

# 复制 configs.json 文件到 ./dist/chat
Copy-Item -Path .\api_config.json -Destination $distDirPath

# 复制 icon.png 文件到 ./dist/chat/icon.png
Copy-Item -Path .\icon.png -Destination $distDirPath

# 检查是否安装了7-zip
$7zipInstalled = Test-Path "C:\Program Files\7-Zip\7z.exe"

# 获取当前日期并格式化为 "yyyyMMdd" 格式
$dateSuffix = Get-Date -Format "yyyyMMdd"
$outputCompressedFilePath = if ($7zipInstalled) { "${distDirPath}_${dateSuffix}.7z" } else { "${distDirPath}_${dateSuffix}.zip" }

# 使用7-zip进行压缩（如果安装），否则使用Compress-Archive
if ($7zipInstalled) {
    & "C:\Program Files\7-Zip\7z.exe" a -r $outputCompressedFilePath "$distDirPath\*"
} else {
    Compress-Archive -Path $distDirPath -DestinationPath $outputCompressedFilePath -Force
}