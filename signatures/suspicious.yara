rule SuspiciousExe {
    meta:
        description = "Detects suspicious executable patterns"
        author = "TitanDefender"
    strings:
        $a = "cmd.exe /c" nocase
        $b = "powershell -enc" nocase
        $c = "rundll32" nocase
    condition:
        2 of them
}
