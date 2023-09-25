import enum
import time

import imgui

from nylib.utils.imgui.window_mgr import Window
from .mem import CombatMem
from ff_draw.gui.default_style import set_style, pop_style
from ff_draw.plugins import FFDrawPlugin
from ff_draw.sniffer.utils.message import NetworkMessage, ActorControlMessage
from ff_draw.sniffer.message_structs import zone_server, actor_control, ZoneServer, ActorControlId
from ff_draw.sniffer.message_structs.zone_server import ActionEffect


#source_id = 0
#action_id = 0
enemy_actors = []
#赤魔  90s  29704
#技工  90s  29415
#黑魔  60s  29662
#白魔  60s  29230
#占星 105s  29255
#舞者  90s  29432
#召唤  60s  29673  29678
#学者  90s  29237
#绝枪  60s  29130
#武僧  75s  29485
#诗人 120s  29401
#贤者 120s  29266
#镰刀  75s  29553
#忍者 105s  29515
#黑骑 105s  29097
#武士 120s  29537
#战士  90s  29083
#龙骑  90s  29499
#骑士 120s  29069

#Map ID：角力学校：1032-1058     火山之心：1033-1059     九霄云上：1034-1060     机关大殿：1116-1117
Test技能 = [3570, 7433]
陆拾秒LB = [29662, 29230, 29673, 29678, 29130]
玖拾秒LB = [29704, 29415, 29432, 29237, 29083, 29499]
壹佰零伍秒LB = [29255, 29515, 29097]
壹佰贰拾秒LB = [29401, 29266, 29537, 29069]
伍伍对战区域 = [1032, 1058, 1033, 1059, 1034, 1060, 1116, 1117, 364]


class MiniWindow:
    def __init__(self, main: 'Siren55Counter'):
        self.main = main
        self.window = None

    def on_want_close(self, w):
        self.main.window = None
        self.window = None
        return True

    def before_draw_window(self, w):
        if self.window is None: self.window = w
        set_style()#(self.main.main.gui.panel.style_color)

    def after_draw_window(self, w):
        pop_style()

    def draw(self, w):
        self.main._draw_panel()
        
        
class Siren55Counter(FFDrawPlugin):

    def __init__(self, main):
        super().__init__(main)
        self.main.sniffer.on_action_effect.append(self.on_effect)
        self.tbl = {}
        self.mem = CombatMem(self)
        self.cooldowns = {}  
        self.cooldowns_to_remove = []  
        self.window = None

    def on_unload(self):
        try:
            self.window.window.close()
        except:
            pass        
    def _recv_on_cast(self, msg: NetworkMessage[zone_server.ActorCast]):
        #if msg.message.action_kind != 1: return
        print(str(msg.message.action_kind))
        print(str(msg.message.action_id))
        
    def on_effect(self, evt: NetworkMessage[ActionEffect]):
        #global source_id, action_id
        data = evt.message
        source_id = evt.header.source_id
        source = self.main.mem.actor_table.get_actor_by_id(source_id).name
        #source_name = source
        class_job = self.main.mem.actor_table.get_actor_by_id(source_id).class_job        
        action_id = data.action_id
        action = self.main.sq_pack.sheets.action_sheet[action_id]
        #print("人物ID：" + str(source) + "  " + "技能ID：" + str(action_id) + "  " + str(action) + "  " + str(class_job))        
        if source_id in enemy_actors and action_id in Test技能:
            cooldown = 30 
            self.cooldowns[(source_id, action_id)] = {
                'cooldown_time': time.time() + cooldown,
                'name': source,
                'class_job': class_job
            }
        if source_id in enemy_actors and action_id in 陆拾秒LB:
            cooldown = 60  
            self.cooldowns[(source_id, action_id)] = {
                'cooldown_time': time.time() + cooldown,
                'name': source,
                'class_job': class_job
            }
        if source_id in enemy_actors and action_id in 玖拾秒LB:
            cooldown = 90 
            self.cooldowns[(source_id, action_id)] = {
                'cooldown_time': time.time() + cooldown,
                'name': source,
                'class_job': class_job
            }
        if source_id in enemy_actors and action_id in 壹佰零伍秒LB:
            cooldown = 105 
            self.cooldowns[(source_id, action_id)] = {
                'cooldown_time': time.time() + cooldown,
                'name': source,
                'class_job': class_job
            }
        if source_id in enemy_actors and action_id in 壹佰贰拾秒LB:
            cooldown = 120  
            self.cooldowns[(source_id, action_id)] = {
                'cooldown_time': time.time() + cooldown,
                'name': source,
                'class_job': class_job
            }            
    def update(self, main):
        global enemy_actors
        me = self.main.mem.actor_table.me
        enemy_actors.clear()
        if me is None:
            enemy_actors.clear()
            return False
        if self.main.mem.territory_info.map_id not in 伍伍对战区域:
            return False
        for actor in self.main.mem.actor_table.iter_actor_by_type(1):
            if self.mem.is_enemy(me, actor):
                enemy_actors.append(actor.id)

    def _draw_panel(self):
        #imgui.text(str(enemy_actors))

        for (source_id, action_id), cooldown_data in self.cooldowns.items():
            remaining_time = cooldown_data['cooldown_time'] - time.time()
            if remaining_time > 0:
                source_name = cooldown_data['name']
                class_job = cooldown_data['class_job']
                class_job_name = self.get_class_job_name(class_job)
                remaining_time = round(remaining_time, 0)
                imgui.text("技能ID：" + str(action_id) + " 剩余冷却时间：" + str(remaining_time) +
                           " 来源：" + source_name + " 职业：" + class_job_name)
            else:
                source_name = cooldown_data['name']
                class_job = cooldown_data['class_job']
                class_job_name = self.get_class_job_name(class_job)
                self.main.mem.do_text_command("/e " + "技能ID：" + str(action_id) + " LB冷却已完成" +
                           " 来源：" + source_name + " 职业：" + class_job_name + "<se.3><se.1><se.5>")
                self.cooldowns_to_remove.append((source_id, action_id))  # 将需要删除的项添加到临时列表中


        for item in self.cooldowns_to_remove:
            del self.cooldowns[item]
        self.cooldowns_to_remove.clear()
    def draw_panel(self):
        #imgui.text(str(enemy_actors))

        changed, new_val = imgui.checkbox('mini_window', self.window is not None)
        if changed:
            if new_val:
                self.window = MiniWindow(self)
                self.main.gui.window_manager.new_window(
                    '55MiniWindow',
                    self.window.draw,
                    before_window_draw=self.window.before_draw_window,
                    after_window_draw=self.window.after_draw_window,
                    on_want_close=self.window.on_want_close,
                )
            else:
                try:
                    self.window.window.close()
                except:
                    pass
                    
        if self.window is None:
            self._draw_panel()
    def get_class_job_name(self, class_job):
        class_job_mapping = {
            19: "骑士",
            20: "武僧",
            21: "战士",
            22: "龙骑士",
            23: "吟游诗人",
            24: "白魔法师",
            25: "黑魔法师",
            28: "学者",
            30: "忍者",
            31: "机工",
            32: "暗黑骑士",
            33: "占星术士",
            34: "武士",
            35: "赤魔法师",
            37: "绝枪战士",
            38: "舞者",
            39: "镰刀",
            40: "贤者"
        }
        return class_job_mapping.get(class_job, "")  