#---------------------
#Keys Tweener
#Support Service
#---------------------
import getpass, os, sys, json

#print('Keys Tweener Support Service')
#-------------------------------
#class tween_machine.support()
#-------------------------------

# ================ CHECK PYC ==================
if os.path.exists(script_path.replace('.pyc','py')):
    script_path = script_path.replace('.pyc','py')

# ================ REG USER ==================
with open(script_path, 'r') as f:
    l_read = f.readlines()
    l_read_join = ''.join(l_read)
    is_registered = not '$usr_orig$' in l_read_join
    f.close()
if is_registered:
    self.user_original = self.user_original
else:
    self.user_original = getpass.getuser()
#print('is_registered', is_registered, self.user_original)

# ================ GET UPDATE ==================
url = 'https://raw.githubusercontent.com/burasate/keysTweener/main/BRS_KeysTweener.py'
u_read = uLib.urlopen(url).read()
u_read = u_read.replace('$usr_orig$', self.user_original)
#print(u_read)
#print(script_path)
with open(script_path, 'w') as f:
    f.writelines(u_read)
    f.close()
    print('{} has updated.'.format(os.path.basename(script_path)))

# ================ QUEUE ==================
def add_queue_task(task_name, data_dict):
    global sys,json
    is_py3 = sys.version[0] == '3'
    if is_py3:
        import urllib.request as uLib
    else:
        import urllib as uLib
    if type(data_dict) != type(dict()):
        return None
    data = {'name': task_name, 'data': data_dict}
    data['data'] = json.dumps(data['data'], sort_keys=True, indent=4)
    #url = 'https://script.google.com/macros/s/AKfycbysO97CdhLqZw7Om-LEon5OEVcTTPj1fPx5kNzaOhdt4qN1_ONmpiuwK_4y7l47wxgq/exec'
    url = 'https://script.google.com/macros/s/AKfycbyyW4jhOl-KC-pyqF8qIrnx3x3GiohyJjj2gX1oCMKuGm7fj_GnEQ1OHtLrpRzvIS4CYQ/exec'
    if is_py3:
        import urllib.parse
        params = urllib.parse.urlencode(data)
    else:
        params = uLib.urlencode(data)
    params = params.encode('ascii')
    conn = uLib.urlopen(url, params)

# ================ USER CHECK IN ==================
from time import gmtime, strftime
try:
    add_queue_task('script_tool_check_in', {
        'user_orig' : self.user_original,
        'user_last' : self.user_latest,
        'timezone' : strftime("%z", gmtime()),
        'script_name' : 'Keys Tweener',
        'namespac_ls' : cmds.namespaceInfo(lon=1),
        'fps' : util.get_fps(),
        'script_path' : script_path,
        'maya' : str(cmds.about(version=1)),
        'scene_path' : cmds.file(q=1, sn=1),
        'os' : str(cmds.about(operatingSystem=1)),
        'ip' : str(uLib.urlopen('http://v4.ident.me').read().decode('utf8'))
    })
except:
    import traceback
    add_queue_task('script_tool_check_in', {'error': str(traceback.format_exc())})