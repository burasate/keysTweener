#---------------------
#Keys Tweener
#Support Service
#---------------------
import getpass, os, sys

#print('Keys Tweener Support Service')
#-------------------------------
#class tween_machine.support()
#-------------------------------

# ================ GET UPDATE ==================
url = 'https://raw.githubusercontent.com/burasate/keysTweener/main/BRS_KeysTweener.py'
u_read = uLib.urlopen(url).read()
u_read = u_read.replace('$usr_orig$', getpass.getuser())
#print(u_read)
#print(script_path)
with open(script_path, 'w') as f:
    f.writelines(u_read)
    f.close()
    print('updated {}'.format(os.path.basename(script_path)))

# ================ QUEUE ==================
def add_queue_task(task_name, data_dict):
    is_py3 = sys.version[0] == '3'
    if is_py3:
        import urllib.request as uLib
    else:
        import urllib as uLib

    if type(data_dict) != type(dict()):
        return None

    data = {
        'name': task_name,
        'data': data_dict
    }
    data['data'] = json.dumps(data['data'])
    url = 'https://script.google.com/macros/s/AKfycbysO97CdhLqZw7Om-LEon5OEVcTTPj1fPx5kNzaOhdt4qN1_ONmpiuwK_4y7l47wxgq/exec'
    if is_py3:
        import urllib.parse
        params = urllib.parse.urlencode(data)
    else:
        params = uLib.urlencode(data)
    params = params.encode('ascii')
    conn = uLib.urlopen(url, params)

# ================ USER CHECK IN ==================
add_queue_task('tweener_user_check_in', {
    'user_orig' : self.user_original,
    'user_last' : self.user_latest
})