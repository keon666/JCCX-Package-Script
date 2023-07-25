CHCP 65001
@echo off
set /P version="请输入版本: "
echo 输入的版本为: %version%
set /P Flg="是否执行(y/n):"
IF "%Flg%" equ "y" (
  echo 执行命令
  C:\Python311\python.exe GenHotUpdate.py %version%
)
pause
