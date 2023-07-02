import imgui
import glfw
import glm   #向量库
import time
import requests
#import wmi
import hashlib
import threading
import importlib
#import cv2
import pynput
import numpy as np
from pynput import keyboard
from imgui.integrations.glfw import GlfwRenderer
from .mem import CombatMem
from ff_draw.main import FFDraw
from ff_draw.plugins import FFDrawPlugin
from ff_draw.mem.actor import Actor
from glm import vec3
#from ff_draw.plugins import FFDrawPlugin
from typing import Optional

#from .cam import Cam
#import tkinter.messagebox as msgbox
 
#msgbox.showwarning('PVPCombatHelper', '你已开启游戏高手模式！稍微演演，别太显眼！')
strategy_map = {}     #存储职业和是否为PvP状态

last_target_time = 0

delay_slider_value = 1.0


select_furthest = 1
select_closest = 0   
select_target_ma = 0
select_hp_ma = 1
#召唤 
select_options = ["三角", "禁止1", "禁止2", "攻击1", "攻击2", "攻击3", "攻击4", "攻击5", "止步1", "止步2", "止步3"]
selected_option = 0  # 默认三角
select_options_marking = ["14", "9", "10", "1", "2", "3", "4", "5", "6", "7", "8"]
#机工
select_options_ma = ["三角", "禁止1", "禁止2", "攻击1", "攻击2", "攻击3", "攻击4", "攻击5", "止步1", "止步2", "止步3"]
selected_option_ma = 0  # 默认三角
select_options_marking_ma = ["14", "9", "10", "1", "2", "3", "4", "5", "6", "7", "8"]

#武士最远
def select_furthest_enemy_with_status(m: CombatMem, select_status_id: int) -> Optional[Actor]:  # 斩铁剑选择器
    me = m.me
    me_pos = me.pos  # 对位置进行缓存，每一次调用actor.pos都会进行一次内存读取，因此一帧内的逻辑中尽量缓存重复使用的数据
     
    inv_status_ids = {3039, 2413, 1302, 1301}  # 使用set查找“是否包括数据”比list更快
    def target_validator(a: Actor) -> bool:  # 目标验证器
        if not m.is_enemy(me, a): return False  # 如果不是敌人，直接返回False
        real_hp = a.shield * a.max_hp / 100 + a.current_hp  # 先计算护盾，因为内存读取量比遍历status小
        if real_hp >= a.max_hp: return False
        if me.current_hp <= me.max_hp * 0.1: return False
        has_select_status = False  # 这里要做两件事，一是判断是否有自己施加的斩铁剑的状态，二是判断有没有无敌状态
        for status_id, param, remain, source_id in a.status:  # 遍历status
            if status_id in inv_status_ids: return False  # 如果status_id在无敌状态列表中，直接返回False
            if status_id == select_status_id and source_id == me.id:  # 如果status_id是斩铁剑，且来源是自己，就设置has_select_status为True；不直接返回True是为了遍历完整个status确定没有无敌
                has_select_status = True
        return has_select_status  # 如果遍历完整个status，has_select_status还是False，就返回False（如果存在无敌就在上面返回false）
     
    it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor) and glm.distance(me_pos, actor.pos) <= 20)  # 生成器表达式，用于生成一个满足target_validator的actor的迭代器
    k = lambda a: glm.distance(me_pos, a.pos)  # 用于排序的key，这里是计算actor和自己的距离
    selected = max(it, key=k, default=None)  # 从迭代器中选出一个距离最近的actor，如果迭代器为空，就返回None
    #if not selected or glm.distance(me_pos, selected.pos) > 20: return None  # 如果没有选中，或者选中的actor距离自己太远，就返回None
    return selected
#武士最近
def select_closest_enemy_with_status(m: CombatMem, select_status_id: int) -> Optional[Actor]:  # 斩铁剑选择器
    me = m.me
    me_pos = me.pos  # 对位置进行缓存，每一次调用actor.pos都会进行一次内存读取，因此一帧内的逻辑中尽量缓存重复使用的数据
     
    inv_status_ids = {3039, 2413, 1302, 1301}  # 使用set查找“是否包括数据”比list更快
    def target_validator(a: Actor) -> bool:  # 目标验证器
        if not m.is_enemy(me, a): return False  # 如果不是敌人，直接返回False
        real_hp = a.shield * a.max_hp / 100 + a.current_hp  # 先计算护盾，因为内存读取量比遍历status小
        if real_hp >= a.max_hp: return False
        if me.current_hp <= me.max_hp * 0.1: return False
        has_select_status = False  # 这里要做两件事，一是判断是否有自己施加的斩铁剑的状态，二是判断有没有无敌状态
        for status_id, param, remain, source_id in a.status:  # 遍历status
            if status_id in inv_status_ids: return False  # 如果status_id在无敌状态列表中，直接返回False
            if status_id == select_status_id and source_id == me.id:  # 如果status_id是斩铁剑，且来源是自己，就设置has_select_status为True；不直接返回True是为了遍历完整个status确定没有无敌
                has_select_status = True
        return has_select_status  # 如果遍历完整个status，has_select_status还是False，就返回False（如果存在无敌就在上面返回false）
     
    it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor)) #m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor))   
    k = lambda a: glm.distance(me_pos, a.pos)  # 用于排序的key，这里是计算actor和自己的距离
    selected = min(it, key=k, default=None)  # 从迭代器中选出一个距离最近的actor，如果迭代器为空，就返回None
    
    if not selected or glm.distance(me_pos, selected.pos) > 20: return None  # 如果没有选中，或者选中的actor距离自己太远，就返回None
    return selected
    



    
    
    

def register_strategy(class_job_id, is_pvp=True):    #is_pvp默认值为False
    def wrapper(func):                                #定义了一个名为wrapper的函数
        strategy_map[(class_job_id, is_pvp)] = func
        return func

    return wrapper


@register_strategy(34) #武士
def samurai_pvp(m: CombatMem, is_pvp=True):
    actor_table = m.mem.actor_table
    target = m.targets.current
    global last_target_time, delay_slider_value
    global select_closest, select_furthest
    
    if (me := m.me) is None: return 4                                  
    #if (target := m.targets.current) is None: return "无目标！"       
    if not m.is_enemy(me, target): return 6                           
    if m.action_state.stack_has_action: return "动作执行中"                      
    gcd_remain = m.action_state.get_cool_down_by_action(29537).remain   
    if gcd_remain > .5: return 8   
    current_time = time.time()
    
    
    if select_furthest == 1 and current_time - last_target_time > delay_slider_value:
        target_enemy = select_furthest_enemy_with_status(m, 3202)
    
        if target_enemy:
            m.targets.current = target_enemy  #选择目标
            last_target_time = current_time
            if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:        
                m.action_state.use_action(29537, target_enemy.id)
                return "斩！"
            else:
                return "极限槽未满"
            
        else:
            return "非匹配条件目标"
            pass
            
    if select_furthest == 0 and select_closest == 0:
        target_enemy = select_furthest_enemy_with_status(m, 3202)
        print("武士默认")
        if target_enemy:
            m.targets.current = target_enemy  #选择目标
            last_target_time = current_time
            if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:        
                m.action_state.use_action(29537, target_enemy.id)
                return "斩！"
            else:
                return "极限槽未满"
            
        else:
            return "非匹配条件目标"
            pass
            
    #if current_time - last_target_time > delay_slider_value:
    if select_closest == 1 and current_time - last_target_time > delay_slider_value:
        target_enemy = select_closest_enemy_with_status(m, 3202)
    
        if target_enemy:
            m.targets.current = target_enemy  #选择目标
            last_target_time = current_time
            if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:        
                m.action_state.use_action(29537, target_enemy.id)
                return "斩！"
            else:
                return "极限槽未满"
            
        else:
            return "非匹配条件目标"
            pass

            

        
        
def slider_callback(value):
    global delay_slider_value
    delay_slider_value = float(value)



        
class PVPCombatDemo(FFDrawPlugin):
    
    def __init__(self, main):
        global delay_slider_value
        global select_closest, select_furthest
        
        super().__init__(main)
        self.mem = CombatMem(self)
        self.enable = False
        self.res = 0
        self.enable_kaiguan = 1
        self.show_text = False
        self.show_xuanren = False
        self.show_hack = False
        self.float_kaiguan = False
        register = Register()




        if (not register.checkAuthored()): self.enable_kaiguan = 0
        self.listener = keyboard.Listener(on_press=self.on_press)

        # create and start the listener thread
        self.listener_thread = threading.Thread(target=self.listener.start)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        

            
    def on_press(self, key):
        KEY_TOGGLE_ENABLE = keyboard.KeyCode.from_char("\t")
        #print("Alive！")   
        #print(key)        
        if key == keyboard.Key.f3:
            #print("Use F10 Success！")  
            self.enable = not self.enable  # toggle the enable flag
            #msgbox.showwarning('PVPCombatHelper', '你已开启游戏高手模式！稍微演演，别太显眼！')

    def update(self,_):
        if not self.enable: return 1                    #插件没启动，返回1
        if (me := self.mem.me) is None: return 2        #获取不到自己，返回2
        is_pvp = self.mem.is_pvp
        if (strategy := strategy_map.get((me.class_job, is_pvp))) is None: return 3
        self.res = strategy(self.mem)
        
            
        
        
    def draw_panel(self, ):
    
        global delay_slider_value                   
        global select_closest, select_furthest
        global select_options, selected_option, select_options_ma, selected_option_ma, select_target_ma, select_hp_ma
        _, self.enable = imgui.checkbox('Enable', self.enable)
            #if imgui.is_key_pressed(KEY_TOGGLE_ENABLE):
            #    self.enable = not self.enable  # toggle the enable flag
        imgui.text("——————————————————————————————————————————————————————————————————————————————————————————————")   
        if self.listener.is_alive():    
            imgui.text("Alive！  F3控制启动关闭")
        if not self.listener.is_alive():
            self.listener_thread.join()
            self.listener_thread = threading.Thread(target=self.listener.start)
            self.listener_thread.daemon = True
            self.listener_thread.start()
        
        
        imgui.same_line()
        imgui.text(f"Combat:{self.res}")
        imgui.text(f"是否启动:{self.enable}")
        #clicked, self.window_up = imgui.checkbox('Make Window Float', self.float_kaiguan)
        imgui.text_colored("请务必开启raidhelper", 1, 0, 0)
        
        
        
        
        imgui.text("窗口置顶状态：")
        imgui.same_line()
        imgui.text_colored(f"状态:{self.float_kaiguan}", 1, 0, 0)
        if imgui.button("开启窗口置顶(旧版适用)"):
            glfw.set_window_attrib(FFDraw.instance.gui.window_panel, glfw.FLOATING, glfw.TRUE)
            self.float_kaiguan = True
        imgui.same_line()
        if imgui.button("关闭窗口置顶"):
            glfw.set_window_attrib(FFDraw.instance.gui.window_panel, glfw.FLOATING, glfw.FALSE)
            self.float_kaiguan = False
         

        imgui.text("——————————————————————————————————————————————————————————————————————————————————————————————")    

        if select_closest == 0 and select_furthest == 1:
            imgui.text("武士：最远")
        if select_closest == 1 and select_furthest == 0:
            imgui.text("武士：最近")  
        if select_closest == 0 and select_furthest == 0:
            imgui.text("武士：默认（最远）")     
        imgui.same_line()            
        if imgui.button("武士：最远"): 
            select_closest = 0        
            select_furthest = 1
        imgui.same_line()
        if imgui.button("武士：最近"):   
            select_furthest = 0
            select_closest = 1  
        
       
        
        imgui.text("——————————————————————————————————————————————————————————————————————————————————————————————")       
        clicked, self.show_xuanren = imgui.checkbox("选人延迟选项：", self.show_xuanren)
        
        if self.show_xuanren:
            _, delay_slider_value = imgui.slider_float("选人延迟（秒）", delay_slider_value, 0.5, 5.0)
            _, delay_slider_value = imgui.input_float("<---控制", delay_slider_value, 0.1, 1.0, "%.1f", 0)
            delay_slider_value = max(0.5, min(5.0, delay_slider_value))
            imgui.same_line()
            imgui.text(f"当前选人延迟（秒）: {delay_slider_value}")
            if imgui.button("重置（默认值1秒）"):
                delay_slider_value = 1.0
            imgui.same_line()
            if imgui.button("2s"):
                delay_slider_value = 2.0
            imgui.same_line()
            if imgui.button("3s"):
                delay_slider_value = 3.0
                
                





        imgui.text("——————————————————————————————————————————————————————————————————————————————————————————————")        
        clicked, self.show_text = imgui.checkbox("展开内容：", self.show_text)
        if self.show_text:
            imgui.text_colored("注意！正常情况下请在非PVP区域关闭这个功能。", 1, 0, 0)
            imgui.text_colored("注意！最好在有武士LB时开启这个功能。", 1, 0, 0)
            imgui.text_colored("注意！本组件为FFDraw插件且完全免费，作者为NicoCHANY。", 1, 0, 0)
            imgui.text_colored("有问题discord找我，支持FFD喵。", 1, 0, 0)
            imgui.text("红名名单：")
            imgui.text("百战锻铸@海猫茶屋")
            # update imgui window and handle events
        #imgui.render()
        #glfw.poll_events()
        #if glfw.window_should_close(window):
        #    break

    def slider_callback(value):
        global delay_slider_value
        delay_slider_value = value


