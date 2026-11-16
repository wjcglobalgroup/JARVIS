Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Javis Command Center\jarvis-command-center"
sh.Run "cmd /c run_jarvis.cmd", 0, False
