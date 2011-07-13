@echo off
copy ..\send-sms-chat.py .
create_exe.py py2exe
del /f send-sms-chat.py
