import re
import nonebot, hoshino

from nonebot import on_command

from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter

sv_help = '''
- [来杯咖啡] 后接反馈内容 联系维护组 请不要反馈无意义的事情
'''.strip()

sv = Service(
    name='来杯咖啡',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='通用',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助来杯咖啡"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


_max = 5
lmt = DailyNumberLimiter(_max)
EXCEED_NOTICE = f'您今天已经喝过{_max}杯了，请明早5点后再来！'


@sv.on_prefix('来杯咖啡')
async def feedback(bot, ev: CQEvent):
    uid = ev.user_id
    if not lmt.check(uid):
        await bot.finish(ev, EXCEED_NOTICE, at_sender=True)
    coffee = hoshino.config.SUPERUSERS[0]
    text = str(ev.message).strip()
    if not text:
        await bot.send(ev, "请发送来杯咖啡+您要反馈的内容~", at_sender=True)
    else:
        await bot.send_private_msg(self_id=ev.self_id, user_id=coffee, message=f'【收到一条反馈信息】 发送者:{uid}发送群:{ev.group_id}\n{text}')
        await bot.send(ev, f'您的反馈已发送至维护组！\n======\n{text}', at_sender=True)
        lmt.increase(uid)


@on_command('【收到一条反馈信息】', only_to_me=False)
async def respond(session):
    origin = session.current_arg.strip()
    pattern = re.compile(r'^发送者:(\d+)发送群:(\d+)\s([\s\S]*)#([\s\S]*)$')
    results = pattern.match(origin)
    user, uid, problem, reply = results.group(1), results.group(2), results.group(3), results.group(4)
    if results is None:
        await session.finish('请带上您要回应的内容~')
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有维护组才能使用该功能~')
        return
    await nonebot.get_bot().send_group_msg(group_id=uid, message=f'【来自维护组的回复】对于 [CQ:at,qq={user}] 提交的关于「{problem}」问题作出以下回应。\n======\n：{reply}')
    await session.finish(f'您的回复已发送至用户！\n======\n{reply}')
