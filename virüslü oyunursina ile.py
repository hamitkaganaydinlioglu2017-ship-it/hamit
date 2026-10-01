import sys
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# 1. Grafik ve FPS Ayarları
window.vsync = False
application.target_fps = 300
window.fps_counter.enabled = True
window.exit_button.enabled = False  # Şaka esnasında X butonuna basılmasını engeller

chosenBlock = 1
game_mode = 'survival'
menu_open = False
third_person = False
is_dead = False

# Blok Kırma ve Şaka Değişkenleri
broken_blocks_count = 0
MAX_BROKEN_BLOCKS = 20  # Limit 20 blok
crash_triggered = False

# Can ve Oyuncu Sağlık Değişkenleri
max_health = 10
current_health = 10
hearts = []

# 2. Oyuncu Ayarları
player = FirstPersonController()
player.speed = 8
player.jump_height = 1.5

# Mavi Karakter Modeli (F5 için)
character_model = Entity(
    parent=player,
    model='cube',
    color=color.azure,
    scale=(0.8, 1.8, 0.8),
    origin_y=-0.5,
    position=(0, -1, 0),
    enabled=False
)

# 3. Kalp / Can Arayüzü (HUD)
heart_container = Entity(parent=camera.ui, position=(-0.85, -0.4))

for i in range(max_health):
    heart = Entity(
        parent=heart_container,
        model='quad',
        color=color.red,
        scale=(0.03, 0.03),
        position=(i * 0.035, 0)
    )
    hearts.append(heart)

def update_hearts():
    for i, heart in enumerate(hearts):
        if i < current_health:
            heart.color = color.red
            heart.enabled = (game_mode == 'survival')
        else:
            heart.color = color.dark_gray
            heart.enabled = (game_mode == 'survival')

# 4. ÖLÜM EKRANI ARAYÜZÜ
death_bg = Panel(scale=(1, 1), color=color.black66, enabled=False, z=-1)
death_text = Text(text="OLDUNUZ!", parent=death_bg, y=0.15, origin=(0, 0), scale=3, color=color.red)

def respawn():
    global current_health, is_dead
    current_health = max_health
    player.position = (0, 5, 0)
    is_dead = False
    death_bg.enabled = False
    mouse.locked = True
    player.enabled = True
    update_hearts()

btn_respawn = Button(text="Yeniden Dog", parent=death_bg, y=-0.1, scale=(0.3, 0.08), color=color.red, on_click=respawn)

# 5. "BAY BAY COMPUTER" YAZISI
bye_text = Text(
    text="bay bay computer",
    parent=camera.ui,
    origin=(0, 0),
    scale=3,
    color=color.red,
    enabled=False
)

# 6. SAHTE MAVİ EKRAN (BSOD) TASARIMI
def trigger_fake_bsod():
    # Menüyü ve oyuncuyu tamamen devre dışı bırak, fareyi gizle
    global menu_open
    menu_open = True
    player.enabled = False
    mouse.visible = False
    mouse.locked = True
    
    # Tüm arayüzü gizle
    heart_container.enabled = False
    bye_text.enabled = False
    
    # Windows Mavi Ekran Rengi (Hex: #0078d7)
    bsod_color = color.rgb(0, 120, 215)
    
    # Arka planı kaplayan mavi panel
    bsod_bg = Panel(scale=(2, 2), color=bsod_color, z=-10, parent=camera.ui)
    
    # Windows 10/11 Tarzı Hata Metni
    bsod_msg = """
    :(
    
    Kisisel bilgisayariniz bir sorunla karsilasti ve yeniden baslatilmasi gerekiyor.
    Yalnizca bazi hata bilgileri toplaniyor, ardindan yeniden baslatabilirsiniz.
    
    %100 tamamlandi
    
    
    Daha fazla bilgi almak icin daha sonra cevrimiçi arama yapabilirsiniz:
    HATA KODU: MINECRAFT_BLOCK_CRASH_LIMIT (Hamit_v1.0)
    
    Eger destek personeliyle gorusuyorsaniz su bilgileri verin:
    Durdurma kodu: CRITICAL_PROCESS_DIED (20_BLOCK_LIMIT)
    """
    
    Text(
        text=bsod_msg,
        parent=bsod_bg,
        position=(-0.6, 0.3),
        scale=1.4,
        color=color.white
    )
    
    # 5 saniye sonra oyunu tamamen kapat (bilgisayar resetlenmiş hissi verir)
    invoke(sys.exit, delay=5.0)

def start_crash_sequence():
    global crash_triggered
    if crash_triggered:
        return
    crash_triggered = True
    
    # Kırmızı yazıyı göster
    bye_text.enabled = True
    
    # 1.5 saniye sonra sahte mavi ekranı aç
    invoke(trigger_fake_bsod, delay=1.5)

# 7. ESC Menü Arayüzü
menu_bg = Panel(scale=(0.4, 0.5), color=color.black66, enabled=False)
menu_title = Text(text="OYUN MENUSU", parent=menu_bg, y=0.35, origin=(0, 0), scale=1.5)

def set_creative():
    global game_mode
    game_mode = 'creative'
    player.gravity = 0
    update_hearts()
    toggle_menu()

def set_survival():
    global game_mode
    game_mode = 'survival'
    player.gravity = 1
    update_hearts()
    toggle_menu()

btn_creative = Button(text="Yaratici Mod", parent=menu_bg, y=0.1, scale=(0.3, 0.08), color=color.azure, on_click=set_creative)
btn_survival = Button(text="Hayatta Kalma Modu", parent=menu_bg, y=-0.05, scale=(0.3, 0.08), color=color.orange, on_click=set_survival)
btn_close = Button(text="Oyuna Don", parent=menu_bg, y=-0.2, scale=(0.3, 0.08), color=color.gray, on_click=lambda: toggle_menu())

def toggle_menu():
    global menu_open
    if is_dead or crash_triggered:
        return
    menu_open = not menu_open
    menu_bg.enabled = menu_open
    mouse.locked = not menu_open
    player.enabled = not menu_open

# 8. Tuş Dinleyicisi
def input(key):
    global third_person, chosenBlock

    if key == 'escape':
        toggle_menu()

    if menu_open or is_dead or crash_triggered:
        return

    if key == 'f5':
        third_person = not third_person
        if third_person:
            player.camera_pivot.z = -5
            player.camera_pivot.y = 2
            character_model.enabled = True
        else:
            player.camera_pivot.z = 0
            player.camera_pivot.y = 0
            character_model.enabled = False

    if key == '1': chosenBlock = 1
    if key == '2': chosenBlock = 2

# Hasar Alma ve Düşme Mantığı
last_y = player.y
fall_distance = 0

def take_damage(amount):
    global current_health, is_dead
    current_health -= amount
    if current_health <= 0:
        current_health = 0
        is_dead = True
        death_bg.enabled = True
        mouse.locked = False
        player.enabled = False
    update_hearts()

# 9. Ana Güncelleme Döngüsü
def update():
    global last_y, fall_distance

    if menu_open or is_dead or crash_triggered:
        return

    # Koşma / Sprint
    if held_keys['left shift'] or held_keys['right shift']:
        player.speed = 14
    else:
        player.speed = 8

    # Mod Kontrolleri
    if game_mode == 'creative':
        player.gravity = 0
        if held_keys['space']:
            player.y += 6 * time.dt
        if held_keys['c']:
            player.y -= 6 * time.dt
    else:
        player.gravity = 1
        # Düşme Hasarı
        if player.y < last_y and not player.grounded:
            fall_distance += (last_y - player.y)
        if player.grounded:
            if fall_distance > 4:
                damage = int(fall_distance - 3)
                take_damage(damage)
            fall_distance = 0
        last_y = player.y

    # Gökyüzü Takibi
    sky.position = player.position

    # Sonsuz Harita Üretimi
    player_x = int(player.x)
    player_z = int(player.z)
    render_distance = 8

    for z in range(player_z - render_distance, player_z + render_distance):
        for x in range(player_x - render_distance, player_x + render_distance):
            if (x, z) not in generated_blocks:
                Block(position=(x, 0, z))
                generated_blocks.add((x, z))

# Gökyüzü Sınıfı
class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture='sky_default',
            scale=1000,
            double_sided=True
        )

# Blok Sınıfı
class Block(Button):
    def __init__(self, position=(0,0,0), texture='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            texture=texture,
            color=color.white,
            origin_y=.5,
            highlight_color=color.lime
        )

    def input(self, key):
        global broken_blocks_count

        if self.hovered and not menu_open and not is_dead and not crash_triggered:
            if key == 'right mouse down':
                if chosenBlock == 1:
                    Block(position=self.position + mouse.normal, texture='grass')
                if chosenBlock == 2:
                    Block(position=self.position + mouse.normal, texture='white_cube')
            
            if key == 'left mouse down':
                destroy(self)
                broken_blocks_count += 1
                if broken_blocks_count >= MAX_BROKEN_BLOCKS:
                    start_crash_sequence()

sky = Sky()
generated_blocks = set()

update_hearts()
app.run()
