import glm   #向量库
from ff_draw.gui.text import TextPosition
from ff_draw.plugins import FFDrawPlugin
import imgui
import math
import numpy as np


class PVPHelper(FFDrawPlugin):     #定义一个Radar
    def __init__(self, main):
        super().__init__(main)
        self.print_name = self.data.setdefault('print_name', True)
        self.show_imgui_window = True
        self.show_for_ditian = True
        self.show_for_bengpo = True
        self.show_for_posui = True
        self.show_for_hp = False
        
    def display_colored_text(text, r, g, b):
        imgui.text_colored(text, r, g, b)
        
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
        imgui.text_colored("请务必开启raidhelper", 1, 0, 0)
        clicked, self.show_for_ditian = imgui.checkbox("地天绘制", self.show_for_ditian)
        clicked, self.show_for_bengpo = imgui.checkbox("崩破绘制", self.show_for_bengpo)
        clicked, self.show_for_posui = imgui.checkbox("天穹破碎绘制", self.show_for_posui)
        clicked, self.show_for_hp = imgui.checkbox("半血绘制", self.show_for_hp)
        imgui.text("FFDrawPlugin-PVPHelper")
        imgui.text("支持功能：")
        imgui.text("1、地天检测")
        imgui.text("2、崩破斩铁剑检测")
        imgui.text("3、龙骑天穹破碎检测")
        imgui.text_colored("注意！人多时会严重影响性能，请在非PVP区域关闭这个功能。", 1, 0, 0)
        imgui.text_colored("注意！本组件为FFDraw插件，作者为NicoCHANY。", 1, 0, 0)
        
                                        
        
        #imgui Test
        #values = []
        #for i in range(0, 100):
        #    value = int(50 * math.cos(i * math.pi / 180.0 * 60))
        #    value = min(max(value, 0), 255)
        #    values.append(value)
        #values_float = np.array(values, dtype=np.float32)
        #imgui.plot_lines("Test0", values_float, len(values_float))
        # 
        #x = np.linspace(-1, 1, 500)
        #y = np.linspace(-1, 1, 500)
        #X, Y = np.meshgrid(x, y)
        #Z = (X ** 2 + Y ** 2 - 1) ** 3 - X ** 2 * Y ** 3
        #values_float = Z.astype(np.float32).flatten()
        #imgui.plot_lines("Test1", values_float, len(values_float))

#崩破检测
    def update(self, main):   
        
        view = main.gui.get_view()
        actor_table = main.mem.actor_table
        if self.show_for_bengpo:
        # 遍历所有角色，检查是否有指定状态，并且状态来源为当前玩家角色
            for actor in actor_table.iter_actor_by_type(1):#actor_table:
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
                    surface_color=glm.vec4(0, 1, 0, .3),
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
                    
        if self.show_for_ditian:

    #地天检测
            for actor in actor_table.iter_actor_by_type(1):#actor_table:
                pos = actor.pos
                if not actor.status.has_status(status_id=1240): continue
                
                main.gui.add_3d_shape(
                    0x10000,
                    #(0x10000,
                    glm.translate(pos),
                    point_color=glm.vec4(1, 0, 0, .7),
                    line_color=glm.vec4(1, 0, 0, .7),
                    surface_color=glm.vec4(1, 0, 0, .3),
                    line_width=float(10.0),
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
                    
        if self.show_for_posui:
    #天穹破碎(龙骑LB)检测
            for actor in actor_table.iter_actor_by_type(1):#actor_table:
                pos = actor.pos
                if not actor.status.has_status(status_id=3180): continue
                
                scale_factor = glm.vec3(5.0, 5.0, 5.0)
                main.gui.add_3d_shape(
                    0x10000,
                    #(0x10000,
                    glm.translate(pos) * glm.scale(scale_factor),
                    point_color=glm.vec4(0, 0, 1, .7),
                    line_color=glm.vec4(0, 0, 1, .7),
                    surface_color=glm.vec4(0, 0, 1, .3),
                    line_width=float(3.0),
                )
                if self.print_name:
                    text_pos, valid = view.world_to_screen(*pos)
                    if not valid: continue
                    self.main.gui.render_text(
                        "天穹破碎",
                        (text_pos * glm.vec2(1, -1) + 1) * view.screen_size / 2,
                        color=(0, 0, 1),
                        at=TextPosition.left_bottom
                    )
                    
                  
    #半血绘制       
        if self.show_for_hp:
            for actor in actor_table.iter_actor_by_type(1):#actor_table:
                pos = actor.pos
                real_hp = actor.current_hp 
                if real_hp >= actor.max_hp * 0.48: continue
                #if not actor.status.has_status(status_id=3180): continue
                
                scale_factor = glm.vec3(.5, .5, .5)
                main.gui.add_3d_shape(
                    0x10000,
                    #(0x10000,
                    glm.translate(pos) * glm.scale(scale_factor),
                    line_color=glm.vec4(1, 0, 1, .7),
                    surface_color=glm.vec4(1, 0, 1, .3),
                    line_width=float(3.0),
                )
                if self.print_name:
                    text_pos, valid = view.world_to_screen(*pos)
                    if not valid: continue
                    self.main.gui.render_text(
                        "半血HP",
                        (text_pos * glm.vec2(1, -1) + 1) * view.screen_size / 2,
                        color=(1, 0, 1),
                        at=TextPosition.left_bottom
                    )
                
                #指路：add_3d_shape部分
                
    #def add_3d_shape(self, shape: int, transform: glm.mat4, surface_color: glm.vec4 = None, line_color: glm.vec4 = None,
    #                 line_width: float = 3.0, point_color: glm.vec4 = None, point_size: float = 5.0):
    
    
    
                #指路：原始Radar部分
    
    
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

                #指路：角色状态ID部分


#case 'actor_has_status':
#            return f'(int(main.mem.actor_table.get_actor_by_id({make_value(parser, value.get("id", 0), res, args)}).status.has_status({make_value(parser, value.get("status_id", 0), res, args)},{make_value(parser, value.get("source_id", 0), res, args)})))'

#case 'actor_status_source':
#            return f'(main.mem.actor_table.get_actor_by_id({make_value(parser, value.get("id", 0), res, args)}).status.find_status_source({make_value(parser, value.get("status_id", 0), res, args)}))'
