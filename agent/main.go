package main

import (
	"fmt"
	"os"
	"os/exec"
)

func main() {
	fmt.Println("TitanDefender Agent v0.1.0")
	// Check for engine binary
	if _, err := os.Stat("titan.exe"); err != nil {
		fmt.Println("Engine not found; running in dev mode")
	}
	// Example: trigger scan
	cmd := exec.Command("titan", "scan", ".", "--quick")
	out, _ := cmd.Output()
	fmt.Println(string(out))
}
