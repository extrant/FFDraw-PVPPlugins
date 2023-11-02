try:
    import glm   #向量库
    import imgui
    import math
    import threading
    import time
    import numpy as np
    import sys
    from ff_draw.main import FFDraw
    from ff_draw.gui.text import TextPosition
    from ff_draw.plugins import FFDrawPlugin
    from .mem import CombatMem
    from plugins.raid_helper import RaidHelper
    import nylib.utils.imgui.ctx as imgui_ctx
    from fpt4.utils.sqpack.utils import icon_path
except ImportError:
    print("警告：你的插件可能从小店获取！或者说你没有正确安装SirenPVP！")
    print("如果是从小店获取，请退款并自行寻找正确版本！")    
actors_by_battalion = {}
result_list = []
result_dict = {}
mark_dict = {}
mark_list = []
show_battalion_1 = False
show_battalion_2 = False
show_battalion_3 = False
flash_time = 5.0
radar = False


target_icon_attack_1 = 61201
target_icon_bind_1 = 61211
target_icon_stop_1 = 61221
target_icon_square = 61231  # square, circle,cross,triangle
target_icons = [
    target_icon_attack_1 + 0,  # attack 1
    target_icon_attack_1 + 1,  # attack 2
    target_icon_attack_1 + 2,  # attack 3
    target_icon_attack_1 + 3,  # attack 4
    target_icon_attack_1 + 4,  # attack 5
    target_icon_bind_1 + 0,  # bind 1
    target_icon_bind_1 + 1,  # bind 2
    target_icon_bind_1 + 2,  # bind 3
    target_icon_stop_1 + 0,  # stop 1
    target_icon_stop_1 + 1,  # stop 2
    target_icon_square,  # square
    target_icon_square + 1,  # circle
    target_icon_square + 2,  # cross
    target_icon_square + 3,  # triangle
    target_icon_attack_1 + 5,  # attack 6
    target_icon_attack_1 + 6,  # attack 7
    target_icon_attack_1 + 7,  # attack 8
]
class PVPHelper(FFDrawPlugin):
    def __init__(self, main):    
        super().__init__(main)
        self.mem = CombatMem(self)      
        self.lock = threading.Lock()  # 用于多线程同步的锁对象
        self.timer_thread = threading.Thread(target=self.timer_function)  # 创建定时器线程
        self.timer_thread.daemon = True 
        self.timer_thread.start()
        self.is_open = False
    def hello_world(self):
        global radar
        radar = not radar    
        time.sleep(.5)  
        radar = False
    def timer_function(self):
        global flash_time
        while True:
            start_time = time.time()  # 记录开始时间

            self.hello_world()

            end_time = time.time()  # 记录结束时间
            elapsed_time = end_time - start_time  

            if elapsed_time < 1.0:
                time.sleep(flash_time - elapsed_time)       
    def update(self, main):
        global send_success, actors_by_battalion, result_list, result_dict, radar, show_battalion_1, show_battalion_2, show_battalion_3, flash_time, target_icons, mark_dict, mark_list
        hw = 0
        ss = 0
        hh = 0
        id_ma1 = False               
        style = imgui.get_style()
        if not self.is_open:
            imgui.set_next_window_size(style.window_padding.x * 2 + 100, style.window_padding.y * 2 + 100)
            with imgui_ctx.Window(
                    "FrontlineRadar",
                    flags=imgui.WINDOW_NO_FOCUS_ON_APPEARING |
                          imgui.WINDOW_NO_TITLE_BAR |
                          imgui.WINDOW_NO_RESIZE |
                          imgui.WINDOW_NO_BACKGROUND
            ):
                cursor = imgui.get_cursor_screen_pos()
                self.main.gui.game_image.icon_image(199701, 100, 100)
                imgui.set_cursor_screen_pos(cursor)
                if imgui.invisible_button("##icon_button", 100, 100):
                    self.is_open = True

                                   
        else:
            imgui.set_next_window_size(style.window_padding.x * 2 + 500, style.window_padding.y * 2 + 600)
            with imgui_ctx.Window("FrontlineRadar"):
                if imgui.button("Close"):
                    self.is_open = False
                clicked, id_ma1 = imgui.checkbox('清空玩家列表', id_ma1 )
                if clicked:
                    result_list = []  
                    result_dict = {}
                    mark_dict = {}
                    mark_list = []
                #result_str = "\n".join([f"Actor: {id_name}, Battalion Key: {battalion_key}" for id_name, battalion_key in result_list])
                #imgui.text(result_str) 
                imgui.same_line()
                self.main.gui.game_image.icon_image(46,30,30)
                _, flash_time = imgui.slider_float("雷达扫描间隔", flash_time, 1, 10, "%.0f")
                
                with imgui.begin_tab_bar("tabBar") as tab_bar:
                    if tab_bar.opened:
                        with imgui.begin_tab_item(f"黑涡") as item1:
                            if item1.selected:
                                imgui.columns(2)
                                for id_name, battalion_key, class_job, class_job_icon, level_score in result_list:
                                    if battalion_key == 0:
                                        hw += level_score
                                        self.main.gui.game_image.icon_image(class_job_icon,30,30)
                                        imgui.same_line()
                                        imgui.text(f"{self.get_class_job_name(class_job)} 名称: {id_name} ")
                                        imgui.same_line()
                                        self.main.gui.game_image.icon_image(level_score,15,20)    
                                        imgui.next_column()
                                imgui.columns(1)
                        with imgui.begin_tab_item(f"双蛇") as item2:
                            if item2.selected:
                                imgui.columns(2)
                                for id_name, battalion_key, class_job, class_job_icon, level_score in result_list:
                                    if battalion_key == 1:
                                        ss += level_score                              
                                        self.main.gui.game_image.icon_image(class_job_icon,30,30)
                                        imgui.same_line()
                                        imgui.text(f"{self.get_class_job_name(class_job)} 名称: {id_name} ")
                                        imgui.same_line()
                                        self.main.gui.game_image.icon_image(level_score,15,20)                          
                                        imgui.next_column()
                                imgui.columns(1)
                        with imgui.begin_tab_item(f"恒辉") as item3:
                            if item3.selected:
                                imgui.columns(2)
                                for id_name, battalion_key, class_job, class_job_icon, level_score in result_list:
                                    if battalion_key == 2:
                                        hh += level_score                           
                                        self.main.gui.game_image.icon_image(class_job_icon,30,30)
                                        imgui.same_line()
                                        imgui.text(f"{self.get_class_job_name(class_job)} 名称: {id_name} ")
                                        imgui.same_line()
                                        self.main.gui.game_image.icon_image(level_score,15,20)           #3:4                           
                                        imgui.next_column()
                                imgui.columns(1)    
                        with imgui.begin_tab_item('头顶标记情报') as item4:
                            if item4.selected:
                                for id_id, icon_id, id_home in mark_list:
                                    imgui.text(f"名称: {id_id}@{self.get_home_world_name(id_home)}")   
                                    imgui.same_line()
                                    self.main.gui.game_image.icon_image(icon_id,20,20)                                     

        if radar is True:
            #imgui.text("Test")
            view = main.gui.get_view()
            actor_table = main.mem.actor_table
            me = main.mem.actor_table.me
            if me is None: return False  

            target_icon_map = {}
            for i, icon_id in enumerate(target_icons):
                if target_id := self.main.mem.marking.head_mark_target(i + 1):
                    target_icon_map[target_id] = icon_id

            for actor in actor_table.iter_actor_by_type(1):
                id_name = actor.name                                
                class_job = actor.class_job
                class_job_name = self.get_class_job_name(class_job)
                class_job_icon = 62000 + class_job
                status = actor.status
                plugin = self.main.plugins.get("raid_helper/RaidHelper")
                battalion_key = plugin.get_battalion_key(actor, 0)

                if icon_id := target_icon_map.get(actor.id):
                    id_id = actor.name
                    id_home = actor.home_world
                    #id_id_name = self.main.mem.actor_table.get_actor_by_id(source_id).name
                    if icon_id in mark_dict:
                        mark_dict[icon_id] = (id_id, icon_id, id_home)
                    else:
                        mark_dict[icon_id] = (id_id, icon_id, id_home)
                
                Level1 = actor.status.has_status(status_id=2131)
                Level2 = actor.status.has_status(status_id=2132)
                Level3 = actor.status.has_status(status_id=2133)
                Level4 = actor.status.has_status(status_id=2134)
                Level5 = actor.status.has_status(status_id=2135)
    #            if (id_name, battalion_key, class_job, class_job_icon) not in result_list:  # 检查结果是否已经存在于列表中
    #                result_list.append((id_name, battalion_key, class_job, class_job_icon))
                level_score = 0  # 初始化等级分数为0

                # 根据玩家的等级计算分数
                if Level1 is False and Level2 is False and Level3 is False and Level4 is False and Level5 is False:
                    level_score = 14979
                if Level1:
                    level_score = 14877
                elif Level2:
                    level_score = 14878
                elif Level3:
                    level_score = 14879
                elif Level4:
                    level_score = 14880
                elif Level5:
                    level_score = 14881

                #result_dict = {}

                if id_name in result_dict:
                    # 如果存在，则更新其他属性的值
                    result_dict[id_name] = (id_name, battalion_key, class_job, class_job_icon, level_score)
                else:
                    # 如果不存在，则添加新的角色数据
                    result_dict[id_name] = (id_name, battalion_key, class_job, class_job_icon, level_score)


            result_list = list(result_dict.values())
            mark_list = list(mark_dict.values())    
    def draw_panel(self):
        global result_list, show_battalion_1, show_battalion_2, show_battalion_3, flash_time, result_dict, mark_dict, mark_list
        hw = 0
        ss = 0
        hh = 0
        id_ma1 = False
        clicked, id_ma1 = imgui.checkbox('清空玩家列表', id_ma1 )
        if clicked:
            result_list = []  
            result_dict = {}
            mark_dict = {}
            mark_list = []
        #result_str = "\n".join([f"Actor: {id_name}, Battalion Key: {battalion_key}" for id_name, battalion_key in result_list])
        #imgui.text(result_str) 
        imgui.same_line()
        self.main.gui.game_image.icon_image(46,30,30)
        imgui.same_line()
        _, flash_time = imgui.slider_float("雷达扫描间隔", flash_time, 1, 10, "%.0f")
        
        with imgui.begin_tab_bar("tabBar") as tab_bar:
            if tab_bar.opened:
                with imgui.begin_tab_item(f"黑涡") as item1:
                    if item1.selected:
                        imgui.columns(2)
                        for id_name, battalion_key, class_job, class_job_icon, level_score in result_list:
                            if battalion_key == 0:
                                hw += level_score
                                self.main.gui.game_image.icon_image(class_job_icon,30,30)
                                imgui.same_line()
                                imgui.text(f"{self.get_class_job_name(class_job)} 名称: {id_name} ")
                                imgui.same_line()
                                self.main.gui.game_image.icon_image(level_score,15,20)    
                                imgui.next_column()
                        imgui.columns(1)
                with imgui.begin_tab_item(f"双蛇") as item2:
                    if item2.selected:
                        imgui.columns(2)
                        for id_name, battalion_key, class_job, class_job_icon, level_score in result_list:
                            if battalion_key == 1:
                                ss += level_score                              
                                self.main.gui.game_image.icon_image(class_job_icon,30,30)
                                imgui.same_line()
                                imgui.text(f"{self.get_class_job_name(class_job)} 名称: {id_name} ")
                                imgui.same_line()
                                self.main.gui.game_image.icon_image(level_score,15,20)                          
                                imgui.next_column()
                        imgui.columns(1)
                with imgui.begin_tab_item(f"恒辉") as item3:
                    if item3.selected:
                        imgui.columns(2)
                        for id_name, battalion_key, class_job, class_job_icon, level_score in result_list:
                            if battalion_key == 2:
                                hh += level_score                           
                                self.main.gui.game_image.icon_image(class_job_icon,30,30)
                                imgui.same_line()
                                imgui.text(f"{self.get_class_job_name(class_job)} 名称: {id_name} ")
                                imgui.same_line()
                                self.main.gui.game_image.icon_image(level_score,15,20)           #3:4                           
                                imgui.next_column()
                        imgui.columns(1)    
                with imgui.begin_tab_item('头顶标记情报') as item4:
                    if item4.selected:
                        for id_id, icon_id , id_home in mark_list:
                            imgui.text(f"名称: {id_id}@{self.get_home_world_name(id_home)}") 
                            imgui.same_line()
                            self.main.gui.game_image.icon_image(icon_id,20,20)    



    def get_class_job_name(self, class_job):
        class_job_mapping = {
            19: "骑士",
            20: "武僧",
            21: "战士",
            22: "龙骑",
            23: "诗人",
            24: "白魔",
            25: "黑魔",
            27: "召唤",
            28: "学者",
            30: "忍者",
            31: "机工",
            32: "黑骑",
            33: "占星",
            34: "武士",
            35: "赤魔",
            37: "绝枪",
            38: "舞者",
            39: "镰刀",
            40: "贤者"
        }
        return class_job_mapping.get(class_job, "")  
        
        
        
        
    def get_home_world_name(self, id_home):
        home_world_mapping = {
            1074: "水晶塔",
            1050: "银泪湖",
            1048: "太阳海岸",
            1057: "伊修加德",
            1056: "红茶川",
            1043: "紫水栈桥",
            1069: "延夏",
            1106: "静语庄园",
            1045: "摩杜纳",
            1177: "海猫茶屋",
            1178: "柔风海湾",
            1179: "琥珀原",
            1170: "潮风亭",
            1171: "神拳痕",
            1172: "白银乡",
            1076: "白金幻象",
            1113: "旅人栈桥",
            1121: "拂晓之间",
            1166: "龙巢神殿",
            1176: "梦羽宝境",
            1042: "拉诺西亚",
            1044: "幻影群岛",
            1081: "神意之地",
            1060: "萌芽池",
            1067: "红玉海",
            1173: "宇宙和音",
            1174: "沃仙曦染",
            1175: "晨曦王座"
        }
        return home_world_mapping.get(id_home, "")          