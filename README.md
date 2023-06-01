![logo.png](https://raw.githubusercontent.com/extrant/IMGSave/main/2023/05/18-15-54-09-logo.png)

# FFDraw>PVPPlugin

> A PVPPlugin For FFDraw 

重磅更新：增加[PVPHelperCombat]([GitHub - extrant/FFDraw-PVPPlugins: A PVPPlugin For FFDraw Discord：NicoCHANY#0020](https://github.com/extrant/FFDraw-PVPPlugins#PVPHelperCombat))，自动选择斩铁剑。

2023/5/22 再次更新：增加斩铁剑盾值过滤，增加斩铁时选中敌人（变的更像绿玩一些

2023/5/28 更新：使用头子给出的代码，性能更好，误判率好像低了许多。

2023/6/1   更新：增加忍者半血选择器（PVPSelect），增加绘制控制开关。

    Tips：可以在源码中自行编辑想要过滤的id和去掉不想要过滤的id，盾值id使用内置的盾值检测，不再通过Buff id检测。现在只过滤无敌状态和被保护状态。

 https://discord.gg/HRahvu6HqJ

### 安装 >

首先需要自行配置好FFDraw

> [GitHub - nyaoouo/FFDraw: A Drawing Framework for ffxiv](https://github.com/nyaoouo/FFDraw)

根据具头子给的食用方式安装好后，将本工程的<u>PVPHelper.py</u>放入<u>FFDraw</u>的<u>Plugin</u>文件夹下即可开始食用。

将<u>PVPHelperCombat</u>文件夹放入<u>FFDraw</u>的<u>Plugin</u>文件夹下即可开始食用。

### 使用 >

在FFDPanel界面里找到PVPHelper，启动即可。

插件界面：

![-3c949bdf6496674e.jpg](https://raw.githubusercontent.com/extrant/IMGSave/main/2023/05/18-13-08-17--3c949bdf6496674e.jpg)

需要注意的是，关闭功能并不是关闭那个地天检测开关，而是在FFDraw这个标签栏里将PVPHelper关闭。

### 效果>

> 崩破斩铁剑检测是检测到谁触碰了你的地天，并且脚下绿圈显示。

> 地天检测是检测谁开了地天，脚下红圈显示。

> 龙骑天穹破碎检测是以蓝圈显示龙骑LB范围。

自己去狼狱试！源码全可见。有能力的自行添加代码或者修改代码，颜色是RGB颜色，自行更改。

### 已知问题>

- [x] ~~忘记只筛选玩家角色了，所以在物件多的地方会影响性能。~~  已经解决
  
  > 解决方式：for actor in actor_table.iter_actor_by_type(1):   仅筛选玩家

- [x] ~~地天检测add_shape多打了一个s~~ 已经解决

- [ ] 偶尔会出现斩不死的问题。大多情况为开LB时，对面刚刚好开启了无敌/血盾。十分少见，条件是写好的，也可能是FF14的服务器问题。

![QQ图片20230518130717.gif](https://raw.githubusercontent.com/extrant/IMGSave/main/2023/05/18-13-24-07-QQ%E5%9B%BE%E7%89%8720230518130717.gif)

### PVPHelperCombat>

> 战场辅助工具

在FFDPanel界面里找到PVPHelperCombat，启动即可。

![](https://raw.githubusercontent.com/extrant/IMGSave/main/2023/05/20-22-21-16-2023-05-20-22-21-02-QQ%E6%88%AA%E5%9B%BE20230520221959.jpg)

建议两个插件都启动。插件界面：

![](https://raw.githubusercontent.com/extrant/IMGSave/main/2023/05/20-22-21-57-2023-05-20-22-21-53-QQ%E6%88%AA%E5%9B%BE20230520222023.jpg)

![](https://raw.githubusercontent.com/extrant/IMGSave/main/2023/06/01-13-19-45-2023-06-01-13-19-33-QQ%E6%88%AA%E5%9B%BE20230601131914.jpg)

使用方式：

Enable启动，但是建议在LB时开启。同时建议开启窗口置顶。

与绘制原理一致，如果选中了有崩破的人。且如果这个人中的是你的崩破便会直接斩过去。由于PVPHelper会绿圈绘制崩破，所以直接选中被画了绿圈的人就可以了。

2023/5/21更新：如果有人中的是你的崩破便自动选取最近的人斩铁剑。

2023/5/22 更新：增加斩铁剑过滤id，增加斩铁时选中敌人（变的更像绿玩一些

2323/6/1   更新：增加忍者选择器。

**但需要注意的是：**

**1、不会判断斩铁剑是否就绪，默认是有人中了你的崩破便会斩铁剑。建议在LB时开启。**

**2、演一演。**

**3、斩之前需要选中任意目标。**

**4、忍者不会自动斩，仅仅会选择半血目标。**

### 参考内容>

源码文件：

> [FFDraw/func_parser.py at master · nyaoouo/FFDraw · GitHub](https://github.com/nyaoouo/FFDraw/blob/master/ff_draw/func_parser.py)
> 
> [FFDraw/__init__.py at master · nyaoouo/FFDraw · GitHub](https://github.com/nyaoouo/FFDraw/blob/master/ff_draw/gui/__init__.py)

gui.add_3d_shape部分参数参考：

    def add_3d_shape(self, shape: int, transform: glm.mat4, surface_color: glm.vec4 = None, line_color: glm.vec4 = None,
                     line_width: float = 3.0, point_color: glm.vec4 = None, point_size: float = 5.0):
        shape_type = shape >> 16
        shape_value = shape & 0xFFFF
    
    
    glm.translate(pos) * glm.rotate(facing, glm.vec3(0, 1, 0)) * glm.scale(scale)

surface_color为内圈填充

line_color为线的颜色

line_width为线的宽度

point_color同理

glm.scale为图形大小

            scale_factor = glm.vec3(5.0, 5.0, 5.0)
            main.gui.add_3d_shape(
                0x10000,
                #(0x10000,
                glm.translate(pos) * glm.scale(scale_factor),
                point_color=glm.vec4(0, 0, 1, .7),
                line_color=glm.vec4(0, 0, 1, .7),
                surface_color=glm.vec4(0, 0, 1, .3),
                line_width=float(3.0),
    
    action_type_to_shape_default = {
        2: 0x10000,  # circle
        3: 0x50000 | 90,  # fan
        4: 0x20000,  # rect
        5: 0x10000,  # circle
        6: 0x10000,  # circle
        7: 0x10000,  # circle
        # 8: 0x20000,  # rect to target
        10: 0x10000 | int(.5 * 0xffff),  # donut
        11: 0x20002,  # cross
        12: 0x20000,  # rect
        13: 0x50000 | 90,  # fan
    }

注意的是，有line则用线画图。有point则用点画图。代码中0x10000为圆形

scale_factor = glm.vec3(5.0, 5.0, 5.0) 为设置5倍大小，对应游戏中的米数。

> 指路：原始Radar部分

    def update(self, main):         #遍历
        view = main.gui.get_view()    #获取窗口视角
        for actor in main.mem.actor_table:   #遍历游戏中的所有角色
            pos = actor.pos                  #获取角色三轴坐标
            main.gui.add_3d_shape(              #绘制几何形
                0x90000,
                glm.translate(pos),
                point_color=glm.vec4(1, 1, 1, .7),
            )
            if self.print_name:        #判断，如果说被启动的话
                text_pos, valid = view.world_to_screen(*pos)         #3D转2D，同时返回pos到Valid
                if not valid: continue
                self.main.gui.render_text(
                    actor.name,
                    (text_pos * glm.vec2(1, -1) + 1) * view.screen_size / 2,
                    color=(1, 0, 1),    #紫色
                    at=TextPosition.center_bottom
                )

> 指路：角色状态ID部分

```
case 'actor_has_status':
            return f'(int(main.mem.actor_table.get_actor_by_id({make_value(parser, value.get("id", 0), res, args)}).status.has_status({make_value(parser, value.get("status_id", 0), res, args)},{make_value(parser, value.get("source_id", 0), res, args)})))'

case 'actor_status_source':
            return f'(main.mem.actor_table.get_actor_by_id({make_value(parser, value.get("id", 0), res, args)}).status.find_status_source({make_value(parser, value.get("status_id", 0), res, args)}))'
```
