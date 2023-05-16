import glm   #向量库
from ff_draw.gui.text import TextPosition
from ff_draw.plugins import FFDrawPlugin
import imgui


class Radar(FFDrawPlugin):     #定义一个Radar
    def __init__(self, main):
        super().__init__(main)
        self.print_name = self.data.setdefault('print_name', True)
        self.show_imgui_window = True

    def draw_panel(self):          #初始化
        if not self.show_imgui_window: return
        # if imgui.button("show name" if self.print_name else "not show name"):
        #     self.print_name = not self.print_name
        #     self.main.config.setdefault('radar', {})['print_name'] = self.print_name
        #     self.main.save_config()
        clicked, self.print_name = imgui.checkbox("地天检测，崩破检测开关", self.print_name)
        if clicked:
            self.data['print_name'] = self.print_name
            self.storage.save()
#赞美头子，大爱头子。鸣大钟三次，FFD乃真神也。速速加入FFD教会。
#崩破检测
    def update(self, main):          
        view = main.gui.get_view()
        actor_table = main.mem.actor_table

        # 遍历所有角色，检查是否有指定状态，并且状态来源为当前玩家角色
        for actor in actor_table:
            pos = actor.pos
            if not actor.status.has_status(status_id=3202) or actor.status.find_status_source(status_id=3202) != main.mem.actor_table.me.id: 
                continue
            
            #if not actor.status.has_status(status_id=158) or actor.status.source_id != main.mem.actor_table.me.id: 
            
            #continue
            
            # 获取状态来源id，对比查看是否成功。目前没用。
            source_id = actor.status.find_status_source(status_id=3202)
            source_me = main.mem.actor_table.me.id
            
            # 绘制一个绿色的点
            main.gui.add_3d_shape(
                0x10000,
                glm.translate(pos),
                point_color=glm.vec4(0, 1, 0, 1),
            )

            # 显示斩杀提示
            if self.print_name:
                text_pos, valid = view.world_to_screen(*pos)
                if not valid:
                    continue
                self.main.gui.render_text(
                    #str(source_id),
                    str("斩杀"),
                    (text_pos * glm.vec2(1, -1) + 1) * view.screen_size / 2,
                    color=(1, 0, 1),
                    at=TextPosition.center_bottom
                )
                

#地天检测
        for actor in actor_table:
            pos = actor.pos
            if not actor.status.has_status(status_id=1240): continue
            main.gui.add_3d_shape(
                0x10000,
                glm.translate(pos),
                point_color=glm.vec4(1, 0, 0, .7),
            )
            if self.print_name:
                text_pos, valid = view.world_to_screen(*pos)
                if not valid: continue
                self.main.gui.render_text(
                    "地天答辩",
                    (text_pos * glm.vec2(1, -1) + 1) * view.screen_size / 2,
                    color=(1, 0, 0),
                    at=TextPosition.left_bottom
                )
                
                
#地天检测
        for actor in actor_table:
            pos = actor.pos
            if not actor.status.has_status(status_id=3180): continue
            main.gui.add_3d_shape(
                0x10000,
                glm.translate(pos),
                point_color=glm.vec4(1, 0, 0, .7),
            )
            if self.print_name:
                text_pos, valid = view.world_to_screen(*pos)
                if not valid: continue
                self.main.gui.render_text(
                    "天穹破碎",
                    (text_pos * glm.vec2(1, -1) + 1) * view.screen_size / 2,
                    color=(1, 0, 0),
                    at=TextPosition.left_bottom
                )
                
#    def update(self, main):         #遍历
#        view = main.gui.get_view()    #获取窗口视角
#        for actor in main.mem.actor_table:   #遍历游戏中的所有角色
#            pos = actor.pos                  #获取角色三轴坐标
#            main.gui.add_3d_shape(              #绘制几何形
#                0x90000,
#                glm.translate(pos),
#                point_color=glm.vec4(1, 1, 1, .7),
#            )
#            if self.print_name:        #判断，如果说被启动的话
#                text_pos, valid = view.world_to_screen(*pos)         #3D转2D，同时返回pos到Valid
#                if not valid: continue
#                self.main.gui.render_text(
#                    actor.name,
#                    (text_pos * glm.vec2(1, -1) + 1) * view.screen_size / 2,
#                    color=(1, 0, 1),    #紫色
#                    at=TextPosition.center_bottom
#                )