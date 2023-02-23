#---------------------
#Keys Tweener
#Support Service
#---------------------

print('Keys Tweener Support Service')
#-------------------------------
#class tween_machine.support()
#-------------------------------

# ================ GET UPDATE ==================
import getpass
url = 'https://raw.githubusercontent.com/burasate/keysTweener/main/BRS_KeysTweener.py'
u_read = uLib.urlopen(url).read()
u_read = u_read.replace('$usr_orig$', getpass.getuser())
print(u_read)