set /p armamods=< jointtxt.txt

cd /d "C:\Program Files (x86)\Steam\steamapps\common\Arma 3

start "" arma3server.exe -client -connect=arma3.combinedarms.co.uk -port=2302 -password=CA -mod=%armamods%

exit