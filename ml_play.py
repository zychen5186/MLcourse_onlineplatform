###課程一開始直接計算球落點的程式
"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    pre_ball = (0,0)

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        new_ball = scene_info.ball

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
            ball_served = True
        else:
            if (new_ball[1] - pre_ball[1]) > 0:
                slope = (new_ball[0] - pre_ball[0]) / (new_ball[1] - pre_ball[1])
                fall_point = new_ball[0] + (400 - new_ball[1]) * slope
                if fall_point > 200:
                    fall_point = 200 - (fall_point - 200)
                if fall_point < 0:
                    fall_point = 0 - fall_point

                if fall_point > (scene_info.platform[0]+30):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)#此function告訴platform他在這個frame應該要做什麼動作
                elif fall_point < (scene_info.platform[0]+10):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif (new_ball[1] - pre_ball[1]) < 0:
                if (scene_info.platform[0] > new_ball[0]):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                if (scene_info.platform[0] < new_ball[0]):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)    
            
            pre_ball = scene_info.ball
