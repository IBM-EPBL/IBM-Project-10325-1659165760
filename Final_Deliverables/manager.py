import subprocess

try:
	import ibm_db
except ImportError:
	subprocess([
		"apt"
		"install"
		"-y"
		"python3-dev"
		"python-dev"
	])


subprocess.run([
	"flask",
	"run",
	"--host",
	"0.0.0.0",
	"--port",
	"5000"
])