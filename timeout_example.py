import shlex
from subprocess import Popen, PIPE
import os
from threading import Timer

process_status={}
def kill_and_set_flag(proc, id):
  process_status[id] = 'killed'
  print("%s killed" %(id))
  proc.kill

def pri(srt):
  print(srt)

def run(cmd, timeout_sec):
  proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
  aaa = os.getpid()
  print(aaa)
  timer = Timer(timeout_sec, kill_and_set_flag, [proc, aaa])
  try:
    timer.start()
    stdout, stderr = proc.communicate()
  finally:
    timer.cancel()
    print(process_status)
    if aaa in process_status and process_status[aaa] == 'killed':
      print('none')
    else:
      print('yeah')
    

# Examples: both take 1 second
run("sleep 5", 1)  # process ends normally at 1 second
run("echo 3", 10)  # timeout happens at 1 second
