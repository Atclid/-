import pygame
import random
import os
import sys
import pickle
import time
import subprocess
import traceback
import datetime
from pygame.locals import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# 资源路径处理函数（支持PyInstaller打包）
def get_resource_path(relative_path):
    """获取资源的绝对路径（兼容打包环境）"""
    if getattr(sys, 'frozen', False):  # 是否打包环境
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def generate_crash_report(exception, filename="crash_report.txt"):
    """生成崩溃报告，包含异常信息、时间、代码调用栈等"""
    crash_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== 崩溃报告 ===\n")
        f.write(f"时间: {crash_time}\n")
        f.write(f"异常类型: {type(exception).__name__}\n")
        f.write(f"异常信息: {str(exception)}\n\n")
        f.write(f"代码调用栈:\n")
        f.write(traceback.format_exc())
    print(f"崩溃报告已生成: {filename}")

# 智能字体创建函数（确保在Pygame初始化后调用）
def create_font(size):
    """创建支持中文的字体对象"""
    # 强制检查并初始化字体模块（关键修复）
    if not pygame.font.get_init():
        pygame.font.init()
    
    local_fonts = ["simhei.ttf", "msyh.ttf", "simfang.ttf"]
    for font_file in local_fonts:
        try:
            font_path = get_resource_path(font_file)
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
        except:
            continue
    system_fonts = ["SimHei", "Microsoft YaHei", "SimSun", "FangSong"]
    for font_name in system_fonts:
        try:
            return pygame.font.SysFont(font_name, size)
        except:
            continue
    return pygame.font.SysFont(None, size)

# 颜色定义
TRANSPARENT = (0, 0, 0, 0)
GRID_LINE = (150, 150, 150, 200)
UNREVEALED = (180, 180, 180, 200)
REVEALED = (220, 220, 220, 200)
MINECOLOR = (0, 0, 0, 255)
FLAG = (255, 0, 0, 255)
TEXT_COLOR = (0, 0, 0, 255)
NUM_COLORS = [
    (0, 0, 255, 255),    # 1 - 蓝色
    (0, 128, 0, 255),    # 2 - 绿色
    (255, 0, 0, 255),    # 3 - 红色
    (0, 0, 128, 255),    # 4 - 深蓝
    (128, 0, 0, 255),    # 5 - 深红
    (0, 128, 128, 255),  # 6 - 青色
    (0, 0, 0, 255),      # 7 - 黑色
    (128, 128, 128, 255) # 8 - 灰色
]
BUTTON_COLOR = (100, 150, 200, 200)
BUTTON_HOVER = (120, 170, 220, 200)
TOOL_COLOR = (200, 150, 100, 200)
TOOL_HOVER = (220, 170, 120, 200)
SCORE_COLOR = (50, 150, 50, 255)
CONFIG_BG = (180, 200, 220, 220)
INPUT_BG = (240, 240, 240, 240)
TIME_COLOR = (80, 80, 200, 255)
ERROR_COLOR = (255, 100, 100, 200)
WARNING_COLOR = (255, 165, 0, 200)
SIDEBAR_COLOR = (200, 200, 200, 200)

# 游戏常量
MIN_CELL_SIZE = 15
MAX_CELL_SIZE = 40
DEFAULT_CELL_SIZE = 25
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 30
SCORE_FILE = "minesweeper_score.dat"
SAVE_FILE = "minesweeper_save.dat"
CONFIG_FILE = "minesweeper_config.dat"
INSTRUCTIONS_FILE = "扫雷游戏说明书.txt"
FLAG_IMAGE_PATH = "images/flag.png"  # 建议将图片放入images文件夹
BACKGROUND_IMAGE_PATH = "images/background.png"
DEFAULT_SOUNDS = {
    "click": "sounds/click.wav",
    "reveal": "sounds/reveal.wav",
    "flag": "sounds/flag.wav",
    "win": "sounds/win.wav",
    "lose": "sounds/lose.wav",
    "tool": "sounds/tool.wav"
}

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.sound_paths = {}
        self.missing_sounds = []
        self.error_occurred = False
        
    def load_sounds(self, sound_dir="sounds"):
        """加载音效文件，缺失时记录但不影响游戏"""
        self.sound_paths = DEFAULT_SOUNDS.copy()
        for sound_name, filename in self.sound_paths.items():
            try:
                path = get_resource_path(filename)
                if os.path.exists(path):
                    self.sounds[sound_name] = pygame.mixer.Sound(path)
                    print(f"[INFO] 成功加载音效: {sound_name}")
                else:
                    self.missing_sounds.append((sound_name, path))
                    print(f"[WARNING] 音效文件不存在: {path}")
            except Exception as e:
                self.missing_sounds.append((sound_name, path))
                print(f"[ERROR] 加载音效 {sound_name} 失败: {e}")
        
        # 如果没有音效可用，自动禁用音效系统
        if not self.sounds:
            self.enabled = False
            self.error_occurred = True
            print("[INFO] 未找到任何音效文件，已自动禁用音效系统")
    
    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def get_missing_sounds(self):
        """返回缺失的音效列表"""
        return self.missing_sounds
    
    def has_errors(self):
        """检查是否有加载错误"""
        return self.error_occurred

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0
        self.is_hinted = False

class Minesweeper:
    def __init__(self, width=30, height=20, mine_percentage=0.15, cell_size=DEFAULT_CELL_SIZE, resizable=True):
        try:
            # 初始化Pygame核心模块（确保在创建字体前调用）
            if not pygame.get_init():
                pygame.init()  # 初始化Pygame核心
            if not pygame.font.get_init():
                pygame.font.init()  # 单独初始化字体模块（关键修复）
            
            # 尝试加载配置
            config = self.load_config()
            if config:
                width = config.get('width', width)
                height = config.get('height', height)
                mine_percentage = config.get('mine_percentage', mine_percentage)
                cell_size = config.get('cell_size', cell_size)
                show_time = config.get('show_time', True)
                sound_enabled = config.get('sound_enabled', True)
                tool_size = config.get('tool_size', 3)
            
            self.original_width = width
            self.original_height = height
            self.original_mine_percentage = mine_percentage
            self.original_cell_size = cell_size
            self.original_show_time = show_time
            self.original_sound_enabled = sound_enabled
            self.original_tool_size = tool_size

            self.width = min(max(10, width), 100)
            self.height = min(max(10, height), 60)
            self.cell_size = cell_size
            self.mine_percentage = mine_percentage
            self.resizable = resizable
            self.total_mines = int(self.width * self.height * mine_percentage)
            self.score = 0  # 单局积分
            self.total_score = self.load_score()  # 总积分
            self.game_over = False
            self.win = False
            self.first_click = True
            self.tool_active = False
            self.tool_cost = 1000  # 道具成本固定为1000分
            self.show_time = show_time if 'show_time' in locals() else True
            self.start_time = time.time()
            self.game_time = 0
            self.tool_size = tool_size if 'tool_size' in locals() else 3
            
            # 初始化字体（此时Pygame已初始化，避免报错）
            self.FONT = create_font(18)
            self.TITLE_FONT = create_font(24)
            self.SCORE_FONT = create_font(16)
            
            # 初始化声音管理器
            self.sound_manager = SoundManager()
            self.sound_manager.enabled = sound_enabled if 'sound_enabled' in locals() else True
            
            self.calculate_window_size()
            flags = pygame.RESIZABLE if self.resizable else 0
            self.screen = pygame.display.set_mode((self.window_width, self.window_height), flags)
            pygame.display.set_caption("扫雷游戏")
            
            self.board = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
            self.buttons = []
            self.create_buttons()
            
            # 加载旗子图片
            self.flag_image = self.load_flag_image()
            
            # 加载背景图片
            self.background_image = self.load_background_image()
            
            # 加载声音
            self.sound_manager.load_sounds()
            
            # 显示缺失资源警告
            self.display_resource_warnings()
            
            self.place_mines_after_first_click = True
            self.last_click_time = 0
            self.last_click_pos = None
        except Exception as e:
            generate_crash_report(e)
            raise
    
    def calculate_window_size(self):
        """计算窗口大小，动态调整标题栏高度"""
        effective_cell_size = self.cell_size
        # 动态计算标题栏高度（确保能容纳所有显示内容）
        title_height = self.TITLE_FONT.size("扫雷游戏")[1]
        score_height = self.FONT.size(f"单局积分: 0  总积分: 0")[1]
        time_height = self.FONT.size("时间: 00:00")[1]
        button_height = BUTTON_HEIGHT + 10  # 按钮高度+间距
        
        self.header_height = title_height + score_height + time_height + button_height + 20  # 增加安全间距
        global HEADER_HEIGHT
        HEADER_HEIGHT = self.header_height
        
        self.window_width = self.width * effective_cell_size + 20  # 预留边界
        self.window_height = self.height * effective_cell_size + self.header_height + 20
        self.effective_cell_size = effective_cell_size
    
    def create_buttons(self):
        """创建界面按钮，确保在标题栏内"""
        spacing = 10
        start_x = (self.window_width - (7 * BUTTON_WIDTH + 6 * spacing)) // 2
        button_y = self.header_height - BUTTON_HEIGHT - 10
        self.buttons = [
            ("tool", pygame.Rect(start_x + 0 * (BUTTON_WIDTH + spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            ("reset", pygame.Rect(start_x + 1 * (BUTTON_WIDTH + spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            ("save", pygame.Rect(start_x + 2 * (BUTTON_WIDTH + spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            ("load", pygame.Rect(start_x + 3 * (BUTTON_WIDTH + spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            ("config", pygame.Rect(start_x + 4 * (BUTTON_WIDTH + spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            ("customize", pygame.Rect(start_x + 5 * (BUTTON_WIDTH + spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            ("open_resources", pygame.Rect(start_x + 6 * (BUTTON_WIDTH + spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT))
        ]
    
    def load_flag_image(self, size=None):
        """加载旗子图标"""
        if size is None:
            size = (int(self.cell_size * 0.8), int(self.cell_size * 0.8))
        
        try:
            flag_path = get_resource_path(FLAG_IMAGE_PATH)
            if not os.path.exists(flag_path):
                return None
            flag_img = pygame.image.load(flag_path).convert_alpha()
            return pygame.transform.scale(flag_img, size)
        except:
            return None
    
    def load_background_image(self):
        """加载背景图片并根据窗口大小自动填充"""
        try:
            bg_path = get_resource_path(BACKGROUND_IMAGE_PATH)
            if os.path.exists(bg_path):
                bg_img = pygame.image.load(bg_path).convert_alpha()
                return pygame.transform.scale(bg_img, (self.window_width, self.window_height))
            return None
        except:
            return None
    
    def load_score(self):
        """加载总积分"""
        if os.path.exists(SCORE_FILE):
            try:
                with open(SCORE_FILE, 'rb') as f:
                    return pickle.load(f)
            except:
                return 0
        return 0
    
    def save_score(self):
        """保存总积分"""
        try:
            with open(SCORE_FILE, 'wb') as f:
                pickle.dump(self.total_score, f)
        except:
            pass
    
    def save_game(self):
        """保存游戏状态"""
        try:
            game_state = {
                'width': self.width,
                'height': self.height,
                'board': self.board,
                'score': self.score,
                'game_over': self.game_over,
                'win': self.win,
                'first_click': self.first_click,
                'total_score': self.total_score,
                'game_time': self.game_time,
                'show_time': self.show_time,
                'cell_size': self.cell_size,
                'tool_size': self.tool_size
            }
            with open(SAVE_FILE, 'wb') as f:
                pickle.dump(game_state, f)
            return True
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
    
    def load_game(self):
        """加载游戏存档"""
        if not os.path.exists(SAVE_FILE):
            return False
        try:
            with open(SAVE_FILE, 'rb') as f:
                game_state = pickle.load(f)
            self.width = game_state['width']
            self.height = game_state['height']
            self.board = game_state['board']
            self.score = game_state['score']
            self.game_over = game_state['game_over']
            self.win = game_state['win']
            self.first_click = game_state['first_click']
            self.total_score = game_state['total_score']
            self.game_time = game_state['game_time']
            self.show_time = game_state.get('show_time', True)
            self.cell_size = game_state.get('cell_size', DEFAULT_CELL_SIZE)
            self.tool_size = game_state.get('tool_size', 3)
            self.start_time = time.time() - self.game_time
            self.calculate_window_size()
            flags = pygame.RESIZABLE if self.resizable else 0
            self.screen = pygame.display.set_mode((self.window_width, self.window_height), flags)
            self.create_buttons()
            self.background_image = self.load_background_image()
            self.flag_image = self.load_flag_image()
            return True
        except Exception as e:
            print(f"加载游戏失败: {e}")
            return False
    
    def load_config(self):
        """加载游戏配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        return None
    
    def save_config(self):
        """保存游戏配置"""
        try:
            config = {
                'width': self.width,
                'height': self.height,
                'mine_percentage': self.mine_percentage,
                'cell_size': self.cell_size,
                'show_time': self.show_time,
                'sound_enabled': self.sound_manager.enabled,
                'tool_size': self.tool_size
            }
            with open(CONFIG_FILE, 'wb') as f:
                pickle.dump(config, f)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def reset_game(self):
        """重置游戏状态"""
        self.width = self.original_width
        self.height = self.original_height
        self.mine_percentage = self.original_mine_percentage
        self.cell_size = self.original_cell_size
        self.show_time = self.original_show_time
        self.sound_manager.enabled = self.original_sound_enabled
        self.tool_size = self.original_tool_size

        self.board = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.game_over = False
        self.win = False
        self.first_click = True
        self.tool_active = False
        self.place_mines_after_first_click = True
        self.start_time = time.time()
        self.game_time = 0

        self.calculate_window_size()
        flags = pygame.RESIZABLE if self.resizable else 0
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), flags)
        self.create_buttons()
        self.background_image = self.load_background_image()
        self.flag_image = self.load_flag_image()
    
    def place_mines(self, first_x, first_y):
        """放置地雷（避开首次点击区域）"""
        self.total_mines = int(self.width * self.height * self.mine_percentage)
        safe_zone = []
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ny, nx = first_y + dy, first_x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width:
                    safe_zone.append((ny, nx))
        mines_placed = 0
        while mines_placed < self.total_mines:
            y, x = random.randint(0, self.height-1), random.randint(0, self.width-1)
            if (y, x) not in safe_zone and not self.board[y][x].is_mine:
                self.board[y][x].is_mine = True
                mines_placed += 1
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.height and 0 <= nx < self.width:
                            self.board[ny][nx].neighbor_mines += 1
    
    def reveal(self, x, y, fast_reveal=False):
        """揭示单元格"""
        if not (0 <= y < self.height and 0 <= x < self.width):
            return
        cell = self.board[y][x]
        if cell.is_revealed or cell.is_flagged or self.win:
            return
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False
            self.place_mines_after_first_click = False
            self.start_time = time.time()
        cell.is_revealed = True
        if not self.sound_manager.has_errors():
            self.sound_manager.play("reveal")
        if cell.is_mine:
            self.game_over = True
            if not self.sound_manager.has_errors():
                self.sound_manager.play("lose")
            return
        if not self.win:
            self.score += 5 if not fast_reveal else 1
        if cell.neighbor_mines == 0:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    self.reveal(x + dx, y + dy, fast_reveal)
    
    def reveal_around(self, x, y):
        """根据标记数量揭示周围单元格"""
        cell = self.board[y][x]
        if not cell.is_revealed or cell.is_mine or cell.neighbor_mines == 0:
            return
        flag_count = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width:
                    if self.board[ny][nx].is_flagged:
                        flag_count += 1
        if flag_count == cell.neighbor_mines:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < self.height and 0 <= nx < self.width:
                        if not self.board[ny][nx].is_flagged:
                            self.reveal(nx, ny, fast_reveal=True)
    
    def toggle_flag(self, x, y):
        """切换旗帜标记"""
        if not (0 <= y < self.height and 0 <= x < self.width):
            return
        cell = self.board[y][x]
        if not cell.is_revealed:
            cell.is_flagged = not cell.is_flagged
            if not self.sound_manager.has_errors():
                self.sound_manager.play("flag")
    
    def use_tool(self, x, y):
        """使用扫雷道具（优先扣除单局积分，不足时扣除总积分）"""
        cost = self.tool_cost
        if self.score >= cost:
            self.score -= cost
            self.sound_manager.play("tool")
            self._apply_tool(x, y)
            self.tool_active = True
            return True
        else:
            remaining = cost - self.score
            if self.total_score >= remaining:
                self.total_score -= remaining
                self.score = 0
                self.sound_manager.play("tool")
                self._apply_tool(x, y)
                self.tool_active = True
                return True
            else:
                self.show_message(f"积分不足! 需要{cost}分，当前单局: {self.score}，总积分: {self.total_score}", 1500)
                return False
    
    def _apply_tool(self, x, y):
        """应用道具效果"""
        start_x = max(0, x - self.tool_size // 2)
        end_x = min(self.width, x + self.tool_size // 2 + 1)
        start_y = max(0, y - self.tool_size // 2)
        end_y = min(self.height, y + self.tool_size // 2 + 1)
        for y_idx in range(start_y, end_y):
            for x_idx in range(start_x, end_x):
                if self.board[y_idx][x_idx].is_mine:
                    self.board[y_idx][x_idx].is_flagged = True
    
    def check_win(self):
        """检查是否胜利"""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.board[y][x]
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True
    
    def show_message(self, message, duration=1500):
        """显示提示信息"""
        try:
            self.screen.fill(TRANSPARENT)
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
            self.draw_game_elements()
            msg_surface = pygame.Surface((self.window_width, 40), pygame.SRCALPHA)
            msg_surface.fill(ERROR_COLOR)
            msg_text = self.FONT.render(message, True, (255, 255, 255, 255))
            msg_surface.blit(msg_text, (self.window_width//2 - msg_text.get_width()//2, 10))
            self.screen.blit(msg_surface, (0, self.window_height//2 - 20))
            pygame.display.flip()
            pygame.time.delay(duration)
        except Exception as e:
            generate_crash_report(e)
            print(f"显示消息失败: {message}")
            pygame.time.delay(duration)
    
    def display_resource_warnings(self):
        """显示资源缺失警告"""
        try:
            warnings = []
            if self.flag_image is None:
                warnings.append(f"警告: 旗子图标缺失 ({get_resource_path(FLAG_IMAGE_PATH)})")
            missing_sounds = self.sound_manager.get_missing_sounds()
            if missing_sounds:
                warnings.append("警告: 缺失以下音效文件:")
                for name, path in missing_sounds:
                    warnings.append(f" - {name}: {path}")
            if not warnings:
                return
                
            panel_height = 100 + len(warnings) * 30
            panel = pygame.Surface((self.window_width, panel_height), pygame.SRCALPHA)
            panel.fill(WARNING_COLOR)
            title = self.TITLE_FONT.render("资源缺失警告", True, (255, 255, 255, 255))
            panel.blit(title, (self.window_width//2 - title.get_width()//2, 20))
            y_offset = 60
            for warning in warnings:
                text = self.FONT.render(warning, True, (255, 255, 255, 255))
                panel.blit(text, (50, y_offset))
                y_offset += 30
            hint = self.FONT.render("点击继续游戏...", True, (255, 255, 255, 255))
            panel.blit(hint, (self.window_width//2 - hint.get_width()//2, y_offset + 10))
            
            self.screen.blit(panel, (0, self.window_height//2 - panel_height//2))
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == MOUSEBUTTONDOWN or event.type == KEYDOWN:
                        waiting = False
        except Exception as e:
            generate_crash_report(e)
            try:
                self.screen.fill(ERROR_COLOR)
                error_text = self.FONT.render(f"资源警告显示失败: {str(e)}", True, (255, 255, 255, 255))
                self.screen.blit(error_text, (50, 50))
                pygame.display.flip()
                pygame.time.delay(3000)
            except:
                print(f"严重错误: 无法显示资源警告 - {e}")
    
    def draw_game_elements(self):
        """绘制游戏界面元素"""
        effective_cell_size = self.effective_cell_size
        
        # 绘制标题
        title = self.TITLE_FONT.render("扫雷游戏", True, TEXT_COLOR)
        title_y = 10
        self.screen.blit(title, (self.window_width//2 - title.get_width()//2, title_y))
        
        # 绘制积分显示
        score_text = self.FONT.render(f"单局积分: {self.score}  总积分: {self.total_score}", True, SCORE_COLOR)
        score_y = title_y + title.get_height() + 10
        self.screen.blit(score_text, (20, score_y))
        
        # 绘制时间显示
        if self.show_time and not self.game_over and not self.win:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_text = self.FONT.render(f"时间: {minutes:02d}:{seconds:02d}", True, TIME_COLOR)
            time_y = score_y + score_text.get_height() + 10
            self.screen.blit(time_text, (self.window_width - time_text.get_width() - 20, time_y))
        
        # 绘制按钮
        for btn_type, rect in self.buttons:
            if btn_type == "tool":
                text = f"扫雷道具({self.tool_cost}分)"
                color = TOOL_COLOR
                hover_color = TOOL_HOVER
                if self.tool_active:
                    color = (255, 255, 0)
                    hover_color = (255, 255, 100)
            elif btn_type == "reset":
                text = "重置游戏"
                color = BUTTON_COLOR
                hover_color = BUTTON_HOVER
            elif btn_type == "save":
                text = "保存游戏"
                color = (150, 200, 100, 200)
                hover_color = (170, 220, 120, 220)
            elif btn_type == "load":
                text = "读取存档"
                color = (200, 150, 100, 200)
                hover_color = (220, 170, 120, 220)
            elif btn_type == "config":
                text = "游戏设置"
                color = (180, 100, 200, 200)
                hover_color = (200, 120, 220, 200)
            elif btn_type == "customize":
                text = "自定义资源"
                color = (100, 200, 200, 200)
                hover_color = (120, 220, 220, 220)
            elif btn_type == "open_resources":
                text = "打开资源目录"
                color = (100, 180, 180, 200)
                hover_color = (120, 200, 200, 220)
            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            button_color = hover_color if rect.collidepoint(pygame.mouse.get_pos()) else color
            button_surface.fill(button_color)
            self.screen.blit(button_surface, rect.topleft)
            pygame.draw.rect(self.screen, (50, 50, 50, 255), rect, 2, border_radius=5)
            text_surf = self.FONT.render(text, True, TEXT_COLOR)
            self.screen.blit(text_surf, (rect.centerx - text_surf.get_width()//2, rect.centery - text_surf.get_height()//2))
        
        # 绘制棋盘
        for y in range(self.height):
            for x in range(self.width):
                if y >= self.height or x >= self.width:
                    continue
                cell = self.board[y][x]
                draw_x = x * effective_cell_size
                draw_y = y * effective_cell_size + self.header_height
                rect = pygame.Rect(draw_x, draw_y, effective_cell_size, effective_cell_size)
                cell_surface = pygame.Surface((effective_cell_size, effective_cell_size), pygame.SRCALPHA)
                
                if cell.is_revealed:
                    cell_surface.fill(REVEALED)
                    if cell.is_mine:
                        pygame.draw.circle(cell_surface, MINECOLOR, (effective_cell_size//2, effective_cell_size//2), effective_cell_size // 3)
                    elif cell.neighbor_mines > 0:
                        num_text = self.FONT.render(str(cell.neighbor_mines), True, NUM_COLORS[cell.neighbor_mines - 1])
                        cell_surface.blit(num_text, (effective_cell_size // 2 - num_text.get_width() // 2, effective_cell_size // 2 - num_text.get_height() // 2))
                else:
                    cell_surface.fill(UNREVEALED)
                    if cell.is_flagged:
                        if self.flag_image:
                            img_rect = self.flag_image.get_rect(center=(effective_cell_size//2, effective_cell_size//2))
                            cell_surface.blit(self.flag_image, img_rect)
                        else:
                            pygame.draw.rect(cell_surface, FLAG, (5, 5, effective_cell_size-10, effective_cell_size-10))
                            pygame.draw.line(cell_surface, (255, 255, 0), (5, 5), (effective_cell_size//2, effective_cell_size//2), 2)
                            pygame.draw.line(cell_surface, (255, 255, 0), (effective_cell_size-5, 5), (effective_cell_size//2, effective_cell_size//2), 2)
                pygame.draw.rect(cell_surface, GRID_LINE, (0, 0, effective_cell_size, effective_cell_size), 1)
                self.screen.blit(cell_surface, rect.topleft)
        
        if self.game_over or self.win:
            overlay = pygame.Surface((self.window_width, self.height * effective_cell_size), pygame.SRCALPHA)
            if self.game_over:
                overlay.fill((255, 0, 0, 180))
                game_over_text = self.TITLE_FONT.render("游戏结束!", True, (255, 255, 255, 255))
                self.screen.blit(game_over_text, (self.window_width//2 - game_over_text.get_width()//2, self.header_height + self.height * effective_cell_size // 2 - game_over_text.get_height()//2))
                restart_text = self.FONT.render("点击'重置游戏'按钮重新开始", True, (255, 255, 255, 255))
                self.screen.blit(restart_text, (self.window_width//2 - restart_text.get_width()//2, self.header_height + self.height * effective_cell_size // 2 + 30))
            elif self.win:
                overlay.fill((0, 200, 0, 180))
                win_text = self.TITLE_FONT.render("恭喜获胜!", True, (255, 255, 255, 255))
                self.screen.blit(win_text, (self.window_width//2 - win_text.get_width()//2, self.header_height + self.height * effective_cell_size // 2 - win_text.get_height()//2))
                self.total_score += self.score
                self.save_score()
                score_text = self.FONT.render(f"单局得分: {self.score}  总积分: {self.total_score}", True, (255, 255, 255, 255))
                self.screen.blit(score_text, (self.window_width//2 - score_text.get_width()//2, self.header_height + self.height * effective_cell_size // 2 + 30))
        
        # 绘制侧边栏
        sidebar_width = 20
        sidebar_height = self.window_height - self.header_height
        sidebar_x = self.window_width - sidebar_width
        sidebar_y = self.header_height
        sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, sidebar_width, sidebar_height)
        sidebar_surface = pygame.Surface((sidebar_width, sidebar_height), pygame.SRCALPHA)
        sidebar_surface.fill(SIDEBAR_COLOR)
        self.screen.blit(sidebar_surface, sidebar_rect.topleft)
    
    def draw(self):
        """渲染游戏界面"""
        try:
            self.screen.fill(TRANSPARENT)
            if self.background_image:
                self.background_image = pygame.transform.scale(self.background_image, (self.window_width, self.window_height))
                self.screen.blit(self.background_image, (0, 0))
            self.draw_game_elements()
            pygame.display.flip()
        except Exception as e:
            generate_crash_report(e)
            try:
                self.screen.fill(ERROR_COLOR)
                error_text = self.FONT.render(f"渲染失败: {str(e)}", True, (255, 255, 255, 255))
                self.screen.blit(error_text, (50, 50))
                pygame.display.flip()
            except:
                print(f"严重错误: 无法渲染屏幕 - {e}")
    
    def config_screen(self):
        """游戏配置界面（支持重置配置）"""
        try:
            config_active = True
            original_width = self.width
            original_height = self.height
            original_mine = self.mine_percentage
            original_show_time = self.show_time
            original_sound = self.sound_manager.enabled
            original_cell_size = self.cell_size
            original_tool_size = self.tool_size
            
            width_input = str(self.width)
            height_input = str(self.height)
            mine_input = str(int(self.mine_percentage * 100))
            show_time = "1" if self.show_time else "0"
            sound_enabled = "1" if self.sound_manager.enabled and not self.sound_manager.has_errors() else "0"
            cell_size_input = str(self.cell_size)
            tool_size_input = str(self.tool_size)
            
            input_boxes = [
                {"rect": pygame.Rect(200, 150, 100, 30), "text": width_input, "label": "宽度 (10-100):", "type": "width"},
                {"rect": pygame.Rect(200, 200, 100, 30), "text": height_input, "label": "高度 (10-60):", "type": "height"},
                {"rect": pygame.Rect(200, 250, 100, 30), "text": mine_input, "label": "地雷比例 (%):", "type": "mines"},
                {"rect": pygame.Rect(200, 300, 100, 30), "text": show_time, "label": "显示时间 (0/1):", "type": "time"},
                {"rect": pygame.Rect(200, 350, 100, 30), "text": sound_enabled, "label": "音效开关 (0/1):", "type": "sound"},
                {"rect": pygame.Rect(200, 400, 100, 30), "text": cell_size_input, "label": "单元格大小 (15-40):", "type": "cell_size"},
                {"rect": pygame.Rect(200, 450, 100, 30), "text": tool_size_input, "label": "道具大小 (3-7):", "type": "tool_size"}
            ]
            
            save_button = pygame.Rect(150, 500, 100, 40)
            cancel_button = pygame.Rect(270, 500, 100, 40)
            reset_button = pygame.Rect(390, 500, 100, 40)
            active_input = None
            clock = pygame.time.Clock()
            
            while config_active:
                config_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
                config_surface.fill(CONFIG_BG)
                
                title = self.TITLE_FONT.render("游戏配置", True, (50, 50, 120, 255))
                config_surface.blit(title, (self.window_width//2 - title.get_width()//2, 50))
                
                for box in input_boxes:
                    input_surface = pygame.Surface((box["rect"].width, box["rect"].height), pygame.SRCALPHA)
                    color = (200, 220, 255, 255) if active_input == box else INPUT_BG
                    input_surface.fill(color)
                    pygame.draw.rect(input_surface, (0, 0, 0, 255), (0, 0, box["rect"].width, box["rect"].height), 2, border_radius=5)
                    label = self.FONT.render(box["label"], True, (50, 50, 100, 255))
                    config_surface.blit(label, (box["rect"].x - label.get_width() - 20, box["rect"].y + 5))
                    text_surf = self.FONT.render(box["text"], True, (0, 0, 0, 255))
                    input_surface.blit(text_surf, (10, 5))
                    config_surface.blit(input_surface, box["rect"].topleft)
                
                # 绘制按钮
                for btn_rect, text, color in [
                    (save_button, "保存配置", (100, 200, 100, 255)),
                    (cancel_button, "取消", (200, 100, 100, 255)),
                    (reset_button, "重置配置", (200, 200, 100, 255))
                ]:
                    btn_surface = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
                    btn_surface.fill(color)
                    pygame.draw.rect(btn_surface, (0, 0, 0, 255), (0, 0, btn_rect.width, btn_rect.height), 2, border_radius=5)
                    btn_text = self.FONT.render(text, True, (255, 255, 255, 255))
                    btn_surface.blit(btn_text, (btn_rect.width//2 - btn_text.get_width()//2, btn_rect.height//2 - btn_text.get_height()//2))
                    config_surface.blit(btn_surface, btn_rect.topleft)
                
                self.screen.blit(config_surface, (0, 0))
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == MOUSEBUTTONDOWN:
                        for box in input_boxes:
                            if box["rect"].collidepoint(event.pos):
                                active_input = box
                            else:
                                if active_input == box:
                                    active_input = None
                        if save_button.collidepoint(event.pos):
                            try:
                                width = int(input_boxes[0]["text"])
                                height = int(input_boxes[1]["text"])
                                mine_percentage = int(input_boxes[2]["text"]) / 100
                                show_time = input_boxes[3]["text"] == "1"
                                sound_enabled = input_boxes[4]["text"] == "1"
                                cell_size = int(input_boxes[5]["text"])
                                tool_size = int(input_boxes[6]["text"])
                                
                                if 10 <= width <= 100 and 10 <= height <= 60 and 1 <= mine_percentage <= 30 and 15 <= cell_size <= 40 and 3 <= tool_size <= 7:
                                    self.width = width
                                    self.height = height
                                    self.mine_percentage = mine_percentage
                                    self.show_time = show_time
                                    self.sound_manager.enabled = sound_enabled
                                    self.cell_size = cell_size
                                    self.tool_size = tool_size
                                    self.save_config()
                                    self.reset_game()
                                    config_active = False
                                else:
                                    self.show_message("输入值超出范围，请重新输入", 2000)
                            except ValueError:
                                self.show_message("输入格式错误，请输入有效的数字", 2000)
                        elif cancel_button.collidepoint(event.pos):
                            config_active = False
                        elif reset_button.collidepoint(event.pos):
                            input_boxes[0]["text"] = str(self.original_width)
                            input_boxes[1]["text"] = str(self.original_height)
                            input_boxes[2]["text"] = str(int(self.original_mine_percentage * 100))
                            input_boxes[3]["text"] = "1" if self.original_show_time else "0"
                            input_boxes[4]["text"] = "1" if self.original_sound_enabled and not self.sound_manager.has_errors() else "0"
                            input_boxes[5]["text"] = str(self.original_cell_size)
                            input_boxes[6]["text"] = str(self.original_tool_size)
                    if event.type == KEYDOWN:
                        if active_input:
                            if event.key == K_BACKSPACE:
                                active_input["text"] = active_input["text"][:-1]
                            elif event.unicode.isdigit():
                                active_input["text"] += event.unicode
        
        except Exception as e:
            generate_crash_report(e)
            print(f"配置界面出错: {e}")
    
    def customize_resources(self):
        Tk().withdraw()
        flag_path = askopenfilename(title="选择旗子图标", filetypes=[("PNG Files", "*.png")])
        if flag_path:
            global FLAG_IMAGE_PATH
            FLAG_IMAGE_PATH = flag_path
            self.flag_image = self.load_flag_image()

        bg_path = askopenfilename(title="选择背景图片", filetypes=[("PNG Files", "*.png")])
        if bg_path:
            global BACKGROUND_IMAGE_PATH
            BACKGROUND_IMAGE_PATH = bg_path
            self.background_image = self.load_background_image()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.window_width, self.window_height = event.size
                    self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                    self.background_image = self.load_background_image()
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if y < self.header_height:
                        for btn_type, rect in self.buttons:
                            if rect.collidepoint(x, y):
                                if btn_type == "tool":
                                    self.tool_active = True
                                elif btn_type == "reset":
                                    self.reset_game()
                                elif btn_type == "save":
                                    self.save_game()
                                elif btn_type == "load":
                                    self.load_game()
                                elif btn_type == "config":
                                    self.config_screen()
                                elif btn_type == "customize":
                                    self.customize_resources()
                                elif btn_type == "open_resources":
                                    resource_dir = get_resource_path("")
                                    if os.name == 'nt':
                                        os.startfile(resource_dir)
                                    elif os.name == 'posix':
                                        subprocess.call(['open', resource_dir])
                    else:
                        board_x = (x - 10) // self.effective_cell_size
                        board_y = (y - self.header_height - 10) // self.effective_cell_size
                        if event.button == 1:  # 左键
                            if self.tool_active:
                                if self.use_tool(board_x, board_y):
                                    self.tool_active = False
                            else:
                                self.reveal(board_x, board_y)
                        elif event.button == 3:  # 右键
                            self.toggle_flag(board_x, board_y)
                        elif event.button == 2:  # 中键
                            self.reveal_around(board_x, board_y)

            if not self.game_over and not self.win:
                self.win = self.check_win()
                if self.win:
                    if not self.sound_manager.has_errors():
                        self.sound_manager.play("win")

            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    game = Minesweeper()
    game.run()