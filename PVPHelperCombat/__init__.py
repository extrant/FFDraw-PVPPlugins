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
    me_pos = me.pos  # 对位置进行缓存，每一次调用actor.pos都会进行一次内存读取，因此一帧内的逻辑中尽量缓存重复使用的数据
     
    inv_status_ids = {3039, 2413, 1302, 150}  # 使用set查找“是否包括数据”比list更快
     
    def target_validator(a: Actor) -> bool:  # 目标验证器
        if not m.is_enemy(me, a): return False  # 如果不是敌人，直接返回False
        real_hp = a.shield * a.max_hp / 100 + a.current_hp  # 先计算护盾，因为内存读取量比遍历status小
        if real_hp > a.max_hp: return False
     
        has_select_status = False  # 这里要做两件事，一是判断是否有自己施加的斩铁剑的状态，二是判断有没有无敌状态
        for status_id, param, remain, source_id in a.status:  # 遍历status
            if status_id in inv_status_ids: return False  # 如果status_id在无敌状态列表中，直接返回False
            if status_id == select_status_id and source_id == me.id:  # 如果status_id是斩铁剑，且来源是自己，就设置has_select_status为True；不直接返回True是为了遍历完整个status确定没有无敌
                has_select_status = True
        return has_select_status  # 如果遍历完整个status，has_select_status还是False，就返回False（如果存在无敌就在上面返回false）
     
    it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor))  # 生成器表达式，用于生成一个满足target_validator的actor的迭代器
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

        
