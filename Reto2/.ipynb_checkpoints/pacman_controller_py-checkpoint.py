#!/usr/bin/env python
import rospy
import random
from pacman.msg import actions
from pacman.msg import pacmanPos
from pacman.msg import ghostsPos
from pacman.msg import cookiesPos
from pacman.msg import bonusPos
from pacman.msg import game
from pacman.msg import performance
from pacman.srv import mapService
import numpy as np
from PIL import Image


def pacmanPosCallback(msg):
    global x_P, y_P
    x_P = msg.pacmanPos.x
    y_P = msg.pacmanPos.y
    pass

def ghostsPosCallback(msg):
    global ghostsPosx, ghostsPosy, gmode
    ghostsPosx = []
    ghostsPosy = []
    gmode = []
    for i in range(msg.nGhosts):
        ghostsPosy.append(-msg.ghostsPos[i].y-min_Y)
        ghostsPosx.append(msg.ghostsPos[i].x-min_X)
        gmode.append(msg.mode[i])
    pass

def cookiesPosCallback(msg):
    global cookiesPosx, cookiesPosy
    cookiesPosx = []
    cookiesPosy = []
    for i in range(msg.nCookies):
        cookiesPosy.append(-msg.cookiesPos[i].y-min_Y)
        cookiesPosx.append(msg.cookiesPos[i].x-min_X)
    pass

def bonusPosCallback(msg):
    global bonusPosx, bonusPosy
    bonusPosx = []
    bonusPosy = []
    for i in range(msg.nBonus):
        bonusPosx.append(msg.bonusPos[i].x-min_X)
        bonusPosy.append(-msg.bonusPos[i].y-min_Y)
    pass

def gameStateCallback(msg):
#    rospy.loginfo('Game State: {} '.format(msg.state)) 
    pass

def performanceCallback(msg):
#    rospy.loginfo('Lives: {} Score: {} Time: {} PerformEval: {}'.format(msg.lives, msg.score, msg.gtime, msg.performEval) )
    pass

def createM(nm):
    mapArray = np.zeros((-min_Y+max_Y+1,-min_X+max_X+1,3))
    # Add obstacles
    for i in range(len(obstx)):
        mapArray[-obsty[i]-min_Y,obstx[i]-min_X,0] = 0
        mapArray[-obsty[i]-min_Y,obstx[i]-min_X,1] = 139
        mapArray[-obsty[i]-min_Y,obstx[i]-min_X,2] = 139
    # Add cookies
    for i in range(len(cookiesPosx)):
        mapArray[cookiesPosy[i],cookiesPosx[i],0] = 255
        mapArray[cookiesPosy[i],cookiesPosx[i],1] = 0
        mapArray[cookiesPosy[i],cookiesPosx[i],2] = 0    
    #Add bonus    
    for i in range(len(bonusPosx)):
        mapArray[bonusPosy[i],bonusPosx[i],0] = 255
        mapArray[bonusPosy[i],bonusPosx[i],1] = 255
        mapArray[bonusPosy[i],bonusPosx[i],2] = 255
    # Add pacman
    mapArray[(y_P+min_Y)*-1,x_P-min_X,0] = 255
    mapArray[(y_P+min_Y)*-1,x_P-min_X,1] = 255
    # Add ghosts
    for i in range(len(ghostsPosx)):
        if (gmode[i] == 0):
            mapArray[ghostsPosy[i],ghostsPosx[i],0] = 0
            mapArray[ghostsPosy[i],ghostsPosx[i],1] = 0
            mapArray[ghostsPosy[i],ghostsPosx[i],2] = 255
        else:
            mapArray[ghostsPosy[i],ghostsPosx[i],0] = 128
            mapArray[ghostsPosy[i],ghostsPosx[i],1] = 128
            mapArray[ghostsPosy[i],ghostsPosx[i],2] = 128

    im = Image.fromarray(mapArray.astype(np.uint8))
    im.save('/home/fulloa10/shared/Pictures/state'+str(nm)+'.png')
def pacman_controller_py():

    rospy.init_node('pacman_controller_py', anonymous=True)
    pub = rospy.Publisher('pacmanActions0', actions, queue_size=10)
    rospy.Subscriber('pacmanCoord0', pacmanPos, pacmanPosCallback)
    rospy.Subscriber('ghostsCoord', ghostsPos, ghostsPosCallback)
    rospy.Subscriber('cookiesCoord', cookiesPos, cookiesPosCallback)
    rospy.Subscriber('bonusCoord', bonusPos, bonusPosCallback)
    rospy.Subscriber('gameState', game, gameStateCallback)
    rospy.Subscriber('performanceEval', performance, performanceCallback)
    
    try:
        mapRequestClient = rospy.ServiceProxy('pacman_world', mapService)
        mapa = mapRequestClient("Controller py")
        rospy.loginfo("# Obs: {}".format(mapa.nObs))
        rospy.loginfo("minX : {}  maxX : {}".format(mapa.minX, mapa.maxX))
        rospy.loginfo("minY : {}  maxY : {}".format(mapa.minY, mapa.maxY))
        global min_X, min_Y, max_X, max_Y, obstx, obsty
        obstx = np.zeros(mapa.nObs,dtype=int)
        obsty = np.zeros(mapa.nObs,dtype=int)
        for i in range(mapa.nObs):
            obstx[i] = mapa.obs[i].x
            obsty[i] = mapa.obs[i].y
        
        min_X = mapa.minX
        min_Y = mapa.minY
        max_X = mapa.maxX
        max_Y = mapa.maxY
        nm = 0
        rate = rospy.Rate(10) # 10hz
        msg = actions();
        actfl = open('/home/fulloa10/shared/action.txt','r+')
        while not rospy.is_shutdown():
            if 'y_P' in globals():
                createM(nm)
            
            a = actfl.read()
            if a:
                if a[-1] == '-':
                    a = random.randint(0, 3)
                    print('**************** a was generated randomly **********************')
                elif a[-1].isdigit()
                    a = int(a[-1])
                    actfl.write('-')
            msg.action = a;
            pub.publish(msg.action)
            rate.sleep()
            nm+=1
        
    except rospy.ServiceException as e:
        print ("Error!! Make sure pacman_world node is running ")
    
if __name__ == '__main__':
    try:
        pacman_controller_py()
    except rospy.ROSInterruptException:
        pass
