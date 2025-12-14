
import sys
import time



#from .starrailcontroller import StarRailController

from utils.date import Date
from tasks.power.power import Power
from module.game import cloud_game, get_game_controller
from module.logger import log
from module.screen import screen
from module.automation import auto
from module.config import cfg
from module.notification import notif
from module.notification.notification import NotificationLevel
from module.ocr import ocr
from module.screen import screen

#starrail = StarRailController(cfg=cfg, logger=log)


def start():
    log.hr("开始运行", 0)
    start_game()
    log.hr("完成", 2)


def start_game():
    MAX_RETRY = 3

    def wait_until(condition, timeout, period=1):
        """等待直到条件满足或超时"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            if condition():
                return True
            time.sleep(period)
        return False

    
    def cloud_game_check_and_enter():
        # 点击进入
        if auto.click_element("./assets/images/screen/click_enter.png", "image", 0.9):
            return True
        # 同意浏览器授权
        if auto.click_element("./assets/images/screen/cloud/agree_to_authorize.png", "image", 0.9, take_screenshot=False):
            time.sleep(0.5)
            auto.click_element("每次访问时都充许", "text", 0.9)
        # 是否保存网页地址，点击 x 关闭
        auto.click_element("./assets/images/screen/cloud/close.png", "image", 0.9, take_screenshot=False)
        # 是否将《云·星穹铁道》添加到桌面，需要点击“下次再说”
        auto.click_element("./assets/images/screen/cloud/next_time.png", "image", 0.9, take_screenshot=False)
        # 免责声明，需要点击“接受”
        auto.click_element("./assets/images/screen/cloud/accept.png", "image", 0.9, take_screenshot=False)
        # 适配用户协议和隐私政策更新提示，需要点击“同意”
        auto.click_element("./assets/images/screen/agree_update.png", "image", 0.9, take_screenshot=False)
        # 云游戏设置的引导，需要多次点击 “下一步”
        if auto.click_element("下一步", "text", 0.9, include=True, take_screenshot=False):
            time.sleep(0.5)
            auto.click_element("下一步", "text", 0.9, include=True)
            time.sleep(0.5)
            auto.click_element("我知道了", "text", 0.9, include=True)
        # 由于浏览器语言原因，云游戏启动时可能会是默认英文，需要改成中文
        if auto.click_element("Settings", "text", 0.9, take_screenshot=False):
            time.sleep(0.5)
            auto.click_element("English", "text", 0.9, crop=(1541.0 / 1920, 198.0 / 1080, 156.0 / 1920, 58.0 / 1080))
            time.sleep(0.5)
            auto.click_element("简体中文", "text", 0.9)
            time.sleep(0.5)
            auto.press_key("esc")




    def start_cloud_game():
        if not cloud_game.start_game_process():
            raise Exception("启动或连接浏览器失败")
        log.info("游戏进程已启动")
        if not cloud_game.is_in_game():
            log.info("正在进入云游戏...")
            if not cloud_game.enter_cloud_game():
                raise Exception("进入云游戏失败")
            log.info("已进入云游戏，正在等待加载完成...")
            # time.sleep(10)    #dont need to wait
            if not wait_until(lambda: cloud_game_check_and_enter(), 600):
                raise TimeoutError("查找并点击进入按钮超时")
            log.info("已进入游戏界面")

    for retry in range(MAX_RETRY):
        try:
            start_cloud_game()
            if not wait_until(lambda: screen.get_current_screen(), 360):
                raise TimeoutError("获取当前界面超时")
            break
        except Exception as e:
            log.error(f"尝试启动游戏时发生错误：{e}")
            # 确保在重试前停止游戏
            cloud_game.stop_game()
            
            if retry == MAX_RETRY - 1:
                raise  # 如果是最后一次尝试，则重新抛出异常


def stop(detect_loop=False):
    log.hr("停止运行", 0)



    if detect_loop and cfg.after_finish == "Loop":
        after_finish_is_loop()
    else:
        if detect_loop:
            notify_after_finish_not_loop()
        if cfg.after_finish in ["Exit", "Loop", "Shutdown", "Sleep", "Hibernate", "Restart", "Logoff", "TurnOffDisplay", "RunScript"]:
            get_game_controller().shutdown(cfg.after_finish)
        log.hr("完成", 2)

                
        sys.exit(0)


def after_finish_is_loop():

    def get_wait_time(current_power):
        # 距离体力到达配置文件指定的上限剩余秒数
        wait_time_power_limit = (cfg.power_limit - current_power) * 6 * 60
        # 距离第二天凌晨4点剩余秒数，+30避免显示3点59分不美观，#7
        wait_time_next_day = Date.get_time_next_x_am(cfg.refresh_hour) + 30
        # 取最小值
        wait_time = min(wait_time_power_limit, wait_time_next_day)
        return wait_time

    if cfg.loop_mode == "power":
        current_power = Power.get()
        if current_power >= cfg.power_limit:
            log.info(f"🟣开拓力 >= {cfg.power_limit}")
            log.info("即将再次运行")
            log.hr("完成", 2)
            return
        else:
            get_game_controller().stop_game()
            wait_time = get_wait_time(current_power)
            future_time = Date.calculate_future_time(wait_time)
    else:
        get_game_controller().stop_game()
        scheduled_time = cfg.scheduled_time
        wait_time = Date.time_to_seconds(scheduled_time)
        future_time = Date.calculate_future_time(scheduled_time)

    log.info(cfg.notify_template['ContinueTime'].format(time=future_time))
    notif.notify(content=cfg.notify_template['ContinueTime'].format(time=future_time), level=NotificationLevel.ALL)
    log.hr("完成", 2)
    # 等待状态退出OCR避免内存占用
    ocr.exit_ocr()
    time.sleep(wait_time)

    # 启动前重新加载配置 #262
    cfg._load_config()


def notify_after_finish_not_loop():

    def get_wait_time(current_power):
        # 距离体力到达300上限剩余秒数
        wait_time_power_full = (300 - current_power) * 6 * 60
        return wait_time_power_full

    current_power = Power.get()

    wait_time = get_wait_time(current_power)
    future_time = Date.calculate_future_time(wait_time)
    log.info(cfg.notify_template['FullTime'].format(power=current_power, time=future_time))
    notif.notify(content=cfg.notify_template['FullTime'].format(power=current_power, time=future_time), level=NotificationLevel.ALL)








