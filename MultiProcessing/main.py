import subprocess

command = "echo 'Hi World'"
process = subprocess.Popen(command, shell=True)

print(f"Prozess wurde gestarted: (PID={process.pid})")
process.wait()
print("process done")
