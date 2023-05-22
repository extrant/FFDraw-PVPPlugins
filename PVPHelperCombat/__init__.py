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

strategy_map = {}     #存储职业和是否为PvP状态



def select_closest_enemy_with_status(m: CombatMem, status_id: int) -> Optional[Actor]:   #选择器
    me = m.me
    return_actor: Optional[Actor] = None
    shortest_dist = float('inf')
    not_status_ids = [3186, 3130, 3221, 3164, 3224, 3110, 3109, 3087, 3088, 3097, 3098, 3173]  #过滤id
    #风遁 3186    原初 3130     磁暴 3221     神秘纹 2861    刃舞 3164     守护之光 3224     血印 3110 均衡诊断 3109 鼓舞激励 3087 3088  大天使 3097 3098
    #黑盾1308     魔三连3234 3235 3236   轻身步法 3173
    for actor in m.mem.actor_table.iter_actor_by_type(1):
        if not m.is_enemy(me, actor):
            continue

        if actor.status.has_status(status_id=status_id) and actor.status.find_status_source(status_id=status_id) == me.id:
            if any(actor.status.has_status(status_id=not_id) for not_id in not_status_ids):
                continue
            dist = glm.distance(me.pos, actor.pos)
            if dist < shortest_dist:
                shortest_dist = dist
                return_actor = actor

    return return_actor





def register_strategy(class_job_id, is_pvp=True):    #is_pvp默认值为False
    def wrapper(func):                                #定义了一个名为wrapper的函数
        strategy_map[(class_job_id, is_pvp)] = func
        return func

    return wrapper


#@register_strategy(32)
#def dark_knight_pve(m: CombatMem):
#    if (me := m.me) is None: return 4                                  #判断自己是否为空，如果为空则返回4
#    if (target := m.targets.current) is None: return "无目标！"                 #判断目标是否为空，如果为空则返回5
#    if not m.is_enemy(me, target): return 6                            #判断目标是否为敌，如果不是则返回6
#    if m.action_state.stack_has_action: return "动作执行中"                       #判断是否在进行另外一个动作，如果是则返回7
#    gcd_remain = m.action_state.get_cool_down_by_action(3617).remain   
#    if gcd_remain > .5: return 8                                       #判断技能冷却是否结束，如果还未结束则返回8#
#
#    if me.level >= 26 and m.action_state.combo_action == 3623:          #等级大于26且释放了 吸收斩，则打出噬魂斩
#        return m.action_state.use_action(3632, target.id)
#    if me.level >= 2 and m.action_state.combo_action == 3617:           #等级大于2且释放了 重斩，则打出吸收斩
#        return m.action_state.use_action(3623, target.id)
#    return m.action_state.use_action(3617, target.id)                   #打出 重斩

@register_strategy(34)
def samurai_pvp(m: CombatMem, is_pvp=True):
    actor_table = m.mem.actor_table
    
    if (me := m.me) is None: return 4                                  
    if (target := m.targets.current) is None: return "无目标！"       
    if not m.is_enemy(me, target): return 6                           
    if m.action_state.stack_has_action: return "动作执行中"                      
    gcd_remain = m.action_state.get_cool_down_by_action(29537).remain   
    if gcd_remain > .5: return 8   
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

#@register_strategy(24)
#def whm_test(m: CombatMem):
#    actor_table = m.mem.actor_table
#    
#    if (me := m.me) is None: return 4                                  
#    if (target := m.targets.current) is None: return "无目标！"       
#    if not m.is_enemy(me, target): return 6                           
#    if m.action_state.stack_has_action: return "动作执行中"                      
#    gcd_remain = m.action_state.get_cool_down_by_action(3617).remain   
#    if gcd_remain > .5: return 8   
#    target_enemy = select_closest_enemy_with_status(m, 158)
#    
#    if target_enemy:
#        m.targets.current = target_enemy
#        m.action_state.use_action(3570, target_enemy.id)
#    else:
#        return "非匹配条件目标"
#        pass

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

    def draw_panel(self):
        _, self.enable = imgui.checkbox('Enable', self.enable)
        imgui.same_line()
        imgui.text(f"Combat:{self.res}")
        #clicked, self.window_up = imgui.checkbox('Make Window Float', self.float_kaiguan)
        
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
        imgui.text_colored("注意！正常情况下请在非PVP区域关闭这个功能。", 1, 0, 0)
        imgui.text_colored("注意！最好在有武士LB时开启这个功能。", 1, 0, 0)
        imgui.text_colored("注意！本组件为FFDraw插件且完全免费，如果想支持我就去", 1, 0, 0)
        imgui.text_colored("discord找我请我喝杯奶茶 OAO ", 1, 0, 0)
        
