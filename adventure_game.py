import requests
import os
import time
import random
from urllib.parse import urlparse

class Character:
    def __init__(self, name, character_class):
        self.name = name
        self.character_class = character_class
        self.health = 100
        self.attack = 10
        self.defense = 5
        self.inventory = []
        self.gold = 0
        
        # 根据职业调整属性
        if character_class == "战士":
            self.attack += 5
            self.defense += 3
        elif character_class == "法师":
            self.attack += 8
            self.health -= 10
        elif character_class == "盗贼":
            self.attack += 3
            self.health += 5
            self.inventory.append("开锁工具")

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        print(f"{self.name}受到了{actual_damage}点伤害，剩余生命值: {self.health}")
        if not self.is_alive():
            print(f"{self.name}已经死亡!")

    def attack_enemy(self, enemy):
        damage = random.randint(self.attack // 2, self.attack)
        print(f"{self.name}对{enemy.name}造成了{damage}点伤害")
        enemy.take_damage(damage)

class Enemy:
    def __init__(self, name, health, attack, defense, reward):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.reward = reward

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        if not self.is_alive():
            print(f"{self.name}被击败了!")

    def attack_player(self, player):
        damage = random.randint(self.attack // 2, self.attack)
        print(f"{self.name}对{player.name}造成了{damage}点伤害")
        player.take_damage(damage)

class Game:
    def __init__(self):
        self.player = None
        self.current_room = "entrance"
        self.completed_puzzles = set()
        self.game_over = False
        self.won = False
        self.rooms = self.setup_rooms()
        self.reward_image_url = "https://github.com/Atclid/atclid/blob/main/1752730405339393c13e0b6318d182d3f5ecd54b116d964a3402948ccbbf6ef83a9b9e7ce3172.0.jpg?raw=true"

    def setup_rooms(self):
        # 游戏房间设置
        return {
            "entrance": {
                "description": "你站在一个古老城堡的入口。面前有两扇门，左边一扇，右边一扇。",
                "exits": {"left": "armory", "right": "library"},
                "enemy": None,
                "puzzle": None,
                "item": None
            },
            "armory": {
                "description": "这是城堡的军械库。墙壁上挂着各种武器和盔甲。中央有一个宝箱。",
                "exits": {"back": "entrance", "forward": "throne_room"},
                "enemy": Enemy("守卫骷髅", 40, 12, 5, {"gold": 20, "item": "铁剑"}),
                "puzzle": None,
                "item": "盾牌"
            },
            "library": {
                "description": "这是城堡的图书馆。成千上万的书籍堆放在书架上。一张桌子上有一本发光的书。",
                "exits": {"back": "entrance", "forward": "dungeon"},
                "enemy": None,
                "puzzle": {
                    "question": "发光的书上写着：'我永不休息，永不停歇，上上下下，运行不止。我是什么？'",
                    "answer": "时钟",
                    "reward": "魔法卷轴"
                },
                "item": None
            },
            "throne_room": {
                "description": "这是城堡的王座室。一个巨大的石制王座矗立在房间中央。",
                "exits": {"back": "armory"},
                "enemy": Enemy("石像鬼", 80, 15, 8, {"gold": 50, "item": "王冠"}),
                "puzzle": None,
                "item": None
            },
            "dungeon": {
                "description": "这是城堡的地牢。一股霉味扑面而来。一个囚犯向你求助。",
                "exits": {"back": "library"},
                "enemy": None,
                "puzzle": {
                    "question": "囚犯说：'如果你有开锁工具，就可以放我出去。你要帮助我吗？(是/否)'",
                    "answer": "是",
                    "requires_item": "开锁工具",
                    "reward": {"gold": 30, "item": "钥匙"}
                },
                "item": None
            },
            "treasure_room": {
                "description": "你找到了宝藏室！房间中央有一个巨大的宝箱，散发着诱人的光芒。",
                "exits": {},
                "enemy": Enemy("巨龙", 150, 20, 10, {"gold": 100, "item": "宝藏"}),
                "puzzle": {
                    "question": "要打开宝箱，你需要输入密码。密码是一个数字：什么数字乘以自己等于144？",
                    "answer": "12",
                    "reward": None  # 解开谜题后游戏胜利
                },
                "item": None,
                "locked": True,
                "key_required": "钥匙"
            }
        }

    def print_room_info(self):
        room = self.rooms[self.current_room]
        print(f"\n--- {self.current_room.upper()} ---")
        print(room["description"])
        
        if room["item"] and room["item"] not in self.player.inventory:
            print(f"你看到了一个{item_name}。")
        
        if room.get("locked", False):
            if self.player.inventory and room["key_required"] in self.player.inventory:
                print(f"这个房间被一把锁锁住了，但你有{room['key_required']}。")
            else:
                print(f"这个房间被一把锁锁住了，你需要{room['key_required']}才能打开。")
        
        print("\n出口:")
        for direction in room["exits"]:
            print(f"- {direction}: {room['exits'][direction]}")

    def handle_input(self):
        command = input("\n你想做什么? ").lower().strip()
        
        if command in ["quit", "exit"]:
            self.game_over = True
            print("感谢游玩！")
            return
        
        room = self.rooms[self.current_room]
        
        # 处理移动
        if command in room["exits"]:
            if room.get("locked", False) and room["key_required"] not in self.player.inventory:
                print(f"门被锁住了，你需要{room['key_required']}才能打开。")
                return
            
            self.current_room = room["exits"][command]
            print(f"你向{command}移动，进入了{self.current_room}。")
            
            # 检查新房间是否有敌人
            if self.rooms[self.current_room]["enemy"] and self.rooms[self.current_room]["enemy"].is_alive():
                self.handle_combat()
                
            # 检查新房间是否有谜题
            if (self.rooms[self.current_room]["puzzle"] and 
                self.current_room not in self.completed_puzzles):
                self.handle_puzzle()
                
            # 检查是否到达宝藏室
            if self.current_room == "treasure_room" and self.rooms[self.current_room]["enemy"].is_alive():
                self.handle_combat()
                
            if self.current_room == "treasure_room" and not self.rooms[self.current_room]["enemy"].is_alive():
                if self.rooms[self.current_room]["puzzle"] and self.current_room not in self.completed_puzzles:
                    self.handle_puzzle()
                
        # 处理物品收集
        elif command == "take" and room["item"] and room["item"] not in self.player.inventory:
            self.player.inventory.append(room["item"])
            print(f"你捡起了{room['item']}。")
            
            # 如果捡起钥匙，解锁宝藏室
            if room["item"] == "钥匙" and "treasure_room" in self.rooms:
                self.rooms["treasure_room"]["locked"] = False
                print("你听到远处传来一声锁打开的声音。")
                
        # 处理战斗命令
        elif command == "attack" and room["enemy"] and room["enemy"].is_alive():
            self.handle_combat()
            
        # 处理查看状态
        elif command == "status":
            print(f"\n--- {self.player.name}的状态 ---")
            print(f"职业: {self.player.character_class}")
            print(f"生命值: {self.player.health}")
            print(f"攻击力: {self.player.attack}")
            print(f"防御力: {self.player.defense}")
            print(f"物品: {', '.join(self.player.inventory) if self.player.inventory else '无'}")
            print(f"金币: {self.player.gold}")
            
        # 处理查看物品
        elif command == "inventory":
            print("\n--- 你的物品 ---")
            if self.player.inventory:
                for item in self.player.inventory:
                    print(f"- {item}")
            else:
                print("你没有任何物品。")
                
        # 处理使用物品
        elif command.startswith("use "):
            item = command[4:].strip()
            if item in self.player.inventory:
                if item == "魔法卷轴":
                    if self.current_room == "treasure_room":
                        print("你使用了魔法卷轴，宝箱突然打开了！")
                        self.completed_puzzles.add(self.current_room)
                        self.win_game()
                    else:
                        print("你使用了魔法卷轴，但什么也没发生。")
                else:
                    print(f"你不能使用{item}。")
            else:
                print(f"你没有{item}。")
                
        else:
            print("无效命令。你可以移动(输入方向)、查看状态、攻击敌人、拾取物品或使用物品。")

    def handle_combat(self):
        room = self.rooms[self.current_room]
        enemy = room["enemy"]
        
        if not enemy or not enemy.is_alive():
            return
            
        print(f"\n--- 战斗开始！---")
        print(f"你的对手: {enemy.name}")
        print(f"敌人生命值: {enemy.health}")
        print(f"敌人攻击力: {enemy.attack}")
        print(f"敌人防御力: {enemy.defense}")
        
        while enemy.is_alive() and self.player.is_alive():
            print("\n你的回合!")
            action = input("你想做什么? (攻击/逃跑) ").lower().strip()
            
            if action == "攻击":
                self.player.attack_enemy(enemy)
                
                if enemy.is_alive():
                    print("\n敌人的回合!")
                    enemy.attack_player(self.player)
                    
                    if not self.player.is_alive():
                        self.game_over = True
                        print("游戏结束！")
                        return
            elif action == "逃跑":
                if random.random() < 0.5:
                    print("你成功逃脱了！")
                    possible_exits = list(room["exits"].values())
                    if possible_exits:
                        self.current_room = random.choice(possible_exits)
                        print(f"你逃到了{self.current_room}。")
                    return
                else:
                    print("你逃跑失败了！")
                    print("\n敌人的回合!")
                    enemy.attack_player(self.player)
                    
                    if not self.player.is_alive():
                        self.game_over = True
                        print("游戏结束！")
                        return
            else:
                print("无效命令，你失去了一次攻击机会。")
                print("\n敌人的回合!")
                enemy.attack_player(self.player)
                
                if not self.player.is_alive():
                    self.game_over = True
                    print("游戏结束！")
                    return
        
        # 战斗胜利
        if not enemy.is_alive() and self.player.is_alive():
            print("\n--- 战斗胜利！---")
            if enemy.reward.get("gold"):
                self.player.gold += enemy.reward["gold"]
                print(f"你获得了{enemy.reward['gold']}金币！")
            if enemy.reward.get("item"):
                self.player.inventory.append(enemy.reward["item"])
                print(f"你获得了{item_name}！")

    def handle_puzzle(self):
        room = self.rooms[self.current_room]
        puzzle = room["puzzle"]
        
        if not puzzle or self.current_room in self.completed_puzzles:
            return
            
        print(f"\n--- 谜题 ---")
        print(puzzle["question"])
        
        # 检查是否需要特定物品
        if puzzle.get("requires_item"):
            if puzzle["requires_item"] not in self.player.inventory:
                print(f"你需要{puzzle['requires_item']}才能解决这个谜题。")
                return
                
        answer = input("你的答案是: ").lower().strip()
        
        if answer == puzzle["answer"].lower():
            print("正确！你解开了谜题！")
            self.completed_puzzles.add(self.current_room)
            
            if puzzle.get("reward"):
                if isinstance(puzzle["reward"], str):  # 奖励是物品
                    self.player.inventory.append(puzzle["reward"])
                    print(f"你获得了{puzzle['reward']}！")
                elif isinstance(puzzle["reward"], dict):  # 奖励是物品和金币
                    if puzzle["reward"].get("gold"):
                        self.player.gold += puzzle["reward"]["gold"]
                        print(f"你获得了{puzzle['reward']['gold']}金币！")
                    if puzzle["reward"].get("item"):
                        self.player.inventory.append(puzzle["reward"]["item"])
                        print(f"你获得了{puzzle['reward']['item']}！")
            
            # 如果是宝藏室的谜题，游戏胜利
            if self.current_room == "treasure_room":
                self.win_game()
        else:
            print("错误！再试一次。")

    def win_game(self):
        print("\n--- 恭喜你！你赢得了游戏！---")
        print("你找到了传说中的宝藏，成为了富有的人！")
        self.won = True
        self.game_over = True
        
        # 尝试下载奖励图片
        print("\n正在获取通关奖励...")
        self.download_reward_image()

    def download_reward_image(self):
        try:
            # 解析URL获取文件名
            parsed_url = urlparse(self.reward_image_url)
            filename = os.path.basename(parsed_url.path)
            
            # 发送请求
            response = requests.get(self.reward_image_url, stream=True)
            response.raise_for_status()
            
            # 确保目录存在
            if not os.path.exists("rewards"):
                os.makedirs("rewards")
                
            # 保存文件
            file_path = os.path.join("rewards", filename)
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    
            print(f"奖励图片已成功下载到: {file_path}")
            print("快去查看你的胜利奖品吧！")
            
        except Exception as e:
            print(f"无法下载奖励图片: {e}")
            print("你仍然赢得了游戏！奖励图片可以通过这个链接手动获取:")
            print(self.reward_image_url)

    def create_character(self):
        print("\n--- 创建你的角色 ---")
        name = input("请输入你的角色名称: ").strip()
        
        while True:
            print("\n选择你的职业:")
            print("1. 战士 - 高攻击和防御")
            print("2. 法师 - 高魔法攻击")
            print("3. 盗贼 - 灵活且初始拥有开锁工具")
            
            choice = input("请输入职业编号 (1-3): ").strip()
            
            if choice == "1":
                character_class = "战士"
                break
            elif choice == "2":
                character_class = "法师"
                break
            elif choice == "3":
                character_class = "盗贼"
                break
            else:
                print("无效选择，请重新输入。")
                
        self.player = Character(name, character_class)
        print(f"\n欢迎, {name} the {character_class}! 你的冒险即将开始...")

    def play(self):
        print("\n=== 城堡冒险 ===\n")
        print("你是一位勇敢的冒险者，听说在一座古老的城堡中藏着巨大的宝藏。")
        print("你的任务是进入城堡，找到宝藏，并活着出来。")
        print("祝你好运！\n")
        
        self.create_character()
        
        while not self.game_over:
            self.print_room_info()
            self.handle_input()
            time.sleep(0.5)  # 给玩家一些阅读时间

if __name__ == "__main__":
    game = Game()
    game.play()    