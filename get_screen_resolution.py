import subprocess
cmd = ['xrandr']
cmd2 = ['grep', '*']
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
p.stdout.close()
resolution_string, junk = p2.communicate()
resolution = str(resolution_string.split()[0])
width, height = resolution.split('x')
x, y = 0, 0
for i in range(2, len(width)):
    x = x * 10 + int(width[i])
for i in range(0, len(height) - 1):
    y = y * 10 + int(height[i])

FILE = open('screen_resolution.txt', 'w')
FILE.write(str(x))
FILE.write(" ")
FILE.write(str(y))