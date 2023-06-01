import imgui
import glfw
import glm   #向量库
from .mem import CombatMem
from ff_draw.main import FFDraw
from ff_draw.plugins import FFDrawPlugin
from ff_draw.mem.actor import Actor
from glm import vec3
#from ff_draw.plugins import FFDrawPlugin
from typing import Optional
#import tkinter.messagebox as msgbox
 
#msgbox.showwarning('PVPCombatHelper', '你已开启游戏高手模式！稍微演演，别太显眼！')
strategy_map = {}     #存储职业和是否为PvP状态






def select_closest_enemy_with_status(m: CombatMem, select_status_id: int) -> Optional[Actor]:  # 斩铁剑选择器
    me = m.me
    me_pos = me.pos  
     
    inv_status_ids = {3039, 2413, 1302, 150} 
     
    def target_validator(a: Actor) -> bool:  
        if not m.is_enemy(me, a): return False  
        real_hp = a.shield * a.max_hp / 100 + a.current_hp  
        if real_hp >= a.max_hp: return False
     
        has_select_status = False  
        for status_id, param, remain, source_id in a.status: 
            if status_id in inv_status_ids: return False 
            if status_id == select_status_id and source_id == me.id: 
                has_select_status = True
        return has_select_status  
     
    it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor))  
    k = lambda a: glm.distance(me_pos, a.pos)  
    selected = min(it, key=k, default=None)  
    if not selected or glm.distance(me_pos, selected.pos) > 20: return None  
    return selected


    

def select_closest_enemy_with_real_hp(m: CombatMem) -> Optional[Actor]:    #忍者选择器  LB选人阶段
    me = m.me
    me_pos = me.pos  
     
    inv_status_ids = {3039, 2413, 1302, 150}  
     
    def target_validator(a: Actor) -> bool:  
        if not m.is_enemy(me, a): return False  
        real_hp = a.current_hp 
        if real_hp >= a.max_hp * 0.5: return False
     
        has_select_target = False  
        for status_id, param, remain, source_id in a.status:  
            if status_id in inv_status_ids: return False 
            if real_hp <= a.max_hp * 0.48: 
                has_select_target = True
        return has_select_target  
     
    it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor)) 
    k = lambda a: glm.distance(me_pos, a.pos) 
    selected = min(it, key=k, default=None)  
    if not selected or glm.distance(me_pos, selected.pos) > 15: return None  
    return selected

def select_closest_enemy_with_status2(m: CombatMem) -> Optional[Actor]:    #忍者选择器  星遁天诛连击阶段  未完成
    
    return_actor: Optional[Actor] = None
    shortest_dist = float('inf')
    not_status_ids = [3039, 2413, 1302, 150]
    for sub1_actor in m.mem.actor_table.iter_actor_by_type(1):
        #imgui.text(str(sub1_actor.class_job))
        me = m.me
        #if not m.is_enemy(me, sub1_actor):
        if not m.me.status.has_status(status_id=496):
            continue
        if m.is_enemy(me, sub1_actor):          
            sub1_shield = sub1_actor.shield * sub1_actor.max_hp / 100
            if any(sub1_actor.status.has_status(status_id=not_id) for not_id in not_status_ids):
                continue
            if sub1_actor.current_hp < sub1_actor.max_hp * 0.45:
                continue
            #imgui.text("success2")
            dist = glm.distance(me.pos, sub1_actor.pos)
            if dist < shortest_dist:
                shortest_dist = dist
                return_actor = sub1_actor
    return return_actor
    
    
    
    



def register_strategy(class_job_id, is_pvp=True):    #is_pvp默认值为False
    def wrapper(func):                                #定义了一个名为wrapper的函数
        strategy_map[(class_job_id, is_pvp)] = func
        return func

    return wrapper


@register_strategy(34) #武士
def samurai_pvp(m: CombatMem, is_pvp=True):
    actor_table = m.mem.actor_table
    global last_target_time
    
    if (me := m.me) is None: return 4                                  
    if (target := m.targets.current) is None: return "无目标！"       
    if not m.is_enemy(me, target): return 6                           
    if m.action_state.stack_has_action: return "动作执行中"                      
    gcd_remain = m.action_state.get_cool_down_by_action(29537).remain   
    if gcd_remain > .5: return 8   
    current_time = time.time()
    if current_time - last_target_time > 1:
        target_enemy = select_closest_enemy_with_status(m, 3202)
    
        if target_enemy:
            m.targets.current = target_enemy  #选择目标
            m.action_state.use_action(29537, target_enemy.id)
        else:
            return "非匹配条件目标"
            pass
        
    #for actor in actor_table.iter_actor_by_type(1):#actor_table:
        #pos = actor.pos
        #if actor.status.has_status(status_id=3202) and actor.status.find_status_source(status_id=3202) == m.mem.actor_table.me.id:
            #return m.action_state.use_action(29537, target.id)
            
@register_strategy(30) #忍者
def ninjia_pvp(m: CombatMem, is_pvp=True):
    global last_target_time
    actor_table = m.mem.actor_table
    
    if (me := m.me) is None: return 4                                  
    if (target := m.targets.current) is None: return "无目标！"       
    if not m.is_enemy(me, target): return "非敌对目标"                           
    if m.action_state.stack_has_action: return "动作执行中"                      
    gcd_remain = m.action_state.get_cool_down_by_action(2248).remain   
    if gcd_remain > .5: return 8   
    current_time = time.time()
    if current_time - last_target_time > 2:
        target_enemy = select_closest_enemy_with_real_hp(m)
        if target_enemy:
            m.targets.current = target_enemy  #选择目标
            last_target_time = current_time
    else:
        return "没有匹配的LB目标"
        
    #if target_enemy2:
    #    m.targets.current = target_enemy2  #选择目标
    #    #imgui.text("success3")
    #    m.action_state.use_action(2248, target_enemy2.id)
    #else:
    #    return "正在搜寻斩杀对象"
    #    pass
    
    #3912星遁天诛预备             29516星遁天诛预备后的
    #target_enemy = select_closest_enemy_with_status(m, 3202)
    #if target_enemy:
    #    m.targets.current = target_enemy  #选择目标
    #    m.action_state.use_action(29537, target_enemy.id)


class PVPCombatDemo(FFDrawPlugin):
    def __init__(self, main):
        super().__init__(main)
        self.mem = CombatMem(self)
        self.enable = False
        self.res = 0
        self.float_kaiguan = False

    def update(self,_):
        if not self.enable: return 1                    #插件没启动，返回1
        if (me := self.mem.me) is None: return 2        #获取不到自己，返回2
        is_pvp = self.mem.is_pvp
        if (strategy := strategy_map.get((me.class_job, is_pvp))) is None: return 3
        self.res = strategy(self.mem)

    def draw_panel(self, ):
        _, self.enable = imgui.checkbox('Enable', self.enable)
        imgui.same_line()
        imgui.text(f"Combat:{self.res}")
        #clicked, self.window_up = imgui.checkbox('Make Window Float', self.float_kaiguan)
        imgui.text("请启动RaidHelper插件")
        imgui.text("窗口置顶状态：")
        imgui.same_line()
        imgui.text_colored(f"状态:{self.float_kaiguan}", 1, 0, 0)
        if imgui.button("开启窗口置顶"):
            glfw.set_window_attrib(FFDraw.instance.gui.window_panel, glfw.FLOATING, glfw.TRUE)
            self.float_kaiguan = True
        imgui.same_line()
        if imgui.button("关闭窗口置顶"):
            glfw.set_window_attrib(FFDraw.instance.gui.window_panel, glfw.FLOATING, glfw.FALSE)
            self.float_kaiguan = False
            
        imgui.text(str(strategy_map))
        imgui.text(str(select_closest_enemy_with_status))
        imgui.text_colored("注意！请开启raidhelper。", 1, 0, 0)
        imgui.text_colored("注意！正常情况下请在非PVP区域关闭这个功能。", 1, 0, 0)
        imgui.text_colored("注意！最好在有武士LB时开启这个功能。", 1, 0, 0)
        imgui.text_colored("注意！本组件为FFDraw插件且完全免费，如果想支持我就去", 1, 0, 0)
        imgui.text_colored("discord找我请我喝杯奶茶 OAO ", 1, 0, 0)

    

