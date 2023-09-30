import datetime
import logging
import queue

from config import Config
def find_closest_game_date(time,
                           matchday=Config.MATCHDAY,
                           matchtime=Config.MATCHTIME,
                           hours_offset: int = 2
                           ):
    if time.weekday() == matchday:
        if time.time() < matchtime:
            return datetime.datetime.combine(time.date(), matchtime) + datetime.timedelta(hours=hours_offset)
        else:
            return datetime.datetime.combine((time + datetime.timedelta(days=7)).date(), matchtime) + datetime.timedelta(hours=hours_offset)

    else:
        new_time = datetime.datetime.combine((time + datetime.timedelta(days=(matchday - time.weekday()) % 7)).date(),
                                  time=matchtime) + datetime.timedelta(hours=hours_offset)

        return new_time