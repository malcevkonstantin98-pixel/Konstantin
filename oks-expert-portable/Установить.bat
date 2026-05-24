@echo off
chcp 65001 >nul
title ОКС Эксперт - Установка

echo ================================================
echo    ОКС ЭКСПЕРТ - Система управления объектами
echo ================================================
echo.
echo Спасибо за выбор нашей системы!
echo.
echo Сейчас будет произведена настройка...
echo.

:: Получение пути к текущей папке
set "APP_DIR=%~dp0"
set "HTML_FILE=%APP_DIR%index.html"
set "DESKTOP=%USERPROFILE%\Desktop"

:: Проверка наличия файла
if not exist "%HTML_FILE%" (
    echo ОШИБКА: Файл index.html не найден!
    echo Убедитесь, что этот файл запущен из папки с программой.
    pause
    exit /b 1
)

echo [1/3] Проверка файлов... OK
echo.

:: Создание ярлыка на рабочем столе
echo [2/3] Создание ярлыка на рабочем столе...

set "VBS_FILE=%TEMP%\create_shortcut.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
echo Set oLink = WshShell.CreateShortcut("%DESKTOP%\ОКС Эксперт.lnk") >> "%VBS_FILE%"
echo oLink.TargetPath = "%HTML_FILE%" >> "%VBS_FILE%"
echo oLink.WorkingDirectory = "%APP_DIR%" >> "%VBS_FILE%"
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,14" >> "%VBS_FILE%"
echo oLink.Description = "Система управления объектами капитального строительства" >> "%VBS_FILE%"
echo oLink.Save >> "%VBS_FILE%"

cscript //nologo "%VBS_FILE%"
del "%VBS_FILE%" >nul 2>&1

echo Ярлык создан на рабочем столе!
echo.

:: Запуск приложения
echo [3/3] Запуск приложения...
echo.
echo ================================================
echo Приложение готово к работе!
echo.
echo Ярлык "ОКС Эксперт" создан на рабочем столе.
echo Вы также можете открыть файл index.html вручную.
echo.
echo Для работы требуется подключение к интернету
echo (для загрузки карт Яндекс и стилей).
echo ================================================
echo.
echo Запуск через 3 секунды...
timeout /t 3 /nobreak >nul

start "" "%HTML_FILE%"

echo.
echo Установка завершена успешно!
echo.
pause
